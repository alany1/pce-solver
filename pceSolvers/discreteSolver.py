"""
Suggestion:
As the inital solve is often the bottleneck, maybe we can improve the performance by first restricting to the set
of rationalizable strategies.

Can also increase threads further and investigate presolve option.

Also can try to use a different solver (e.g. PYGLPK) and see if that helps.
"""


import itertools
import os
import pickle
import sys
import io

from tqdm import tqdm
from params_proto import Proto, ParamsProto, PrefixProto
import pulp as pl
import numpy as np
import networkx as nx


import contextlib
import functools


class DiscreteSolver:
    def __init__(
        self,
        gameWrapper,
        solver,
        network: nx.Graph = None,
        verbose=False,
        optVerbose=False,
        numThreads=8,
        presolve=False,
        writePath=None,
    ):
        self.gameWrapper = gameWrapper
        self.game = gameWrapper.game
        self.solver = pl.getSolver(solver, msg=optVerbose, threads=numThreads)
        self.model = pl.LpProblem("Game", pl.LpMaximize)
        self.profiles = list(
            itertools.product(
                range(self.gameWrapper.numActions), repeat=self.gameWrapper.numPlayers
            )
        )
        self.network = network

        self.verbose = verbose
        # TODO: Fix the problem with presolve version of pulp
        self.presolve = presolve

        self.writePath = writePath

        assert self.network is not None, "Network cannot be None!"

    def consistentStrategies(self, profile, player, profilesToConsider):
        """
        Returns all strategy profiles consistent with the given profile for the given player's strategic information
        encoded by the network self.network.
        """

        consistent = set()
        for p in profilesToConsider:
            if all(profile[i] == p[i] for i in self.network.neighbors(player)):
                opponents = list(p)[:player] + list(p)[player + 1 :]
                consistent.add(tuple(opponents))

        return consistent

    def reduceProfiles(self, profilesToConsider):
        """
        Applies operator B_G.
        """
        reducedProfiles = []
        for profile in tqdm(
            profilesToConsider, desc="Reducing profiles", disable=not self.verbose
        ):
            # Check if for all players, is everyone playing a network-consistent best reply.
            clear = True
            for player in range(self.gameWrapper.numPlayers):
                consistent = self.consistentStrategies(
                    profile, player, profilesToConsider
                )

                # Check if there is some viable conjecture (distribution over consistent) where profile_i is a B.R.
                isBestResponse = self.checkBestResponse(profile, player, consistent)
                # print(f"Player {player} is a best response: {isBestResponse}")
                if not isBestResponse:
                    break
            else:
                # If all players are playing a network-consistent best reply, add the profile to the reduced set.
                reducedProfiles.append(profile)

        return reducedProfiles

    def checkBestResponse(self, profile, player, consistent):
        """
        Solve an LP to determine if there EXISTS some conjecture over opponents actions such that profile[i] is a BR
        for player i.
        """
        # Create the LP
        # prob = pl.LpProblem("best_response", pl.LpMaximize, presolve=self.presolve)
        prob = pl.LpProblem("best_response", pl.LpMaximize)

        # Create the variables. Introduce one variable for each consistent strategy profile.
        variables = []
        orderedConsistent = list(consistent)
        for p in orderedConsistent:
            variables.append(pl.LpVariable(str(p), 0, 1))

        # Create the objective function. The objective is not important as we just care about feasibility.
        prob += 0

        # Add the probability constraint that all variables must sum to 1.
        prob += sum(variables) == 1

        # Add the utility constraints. For each possible action of player i, add a constraint that the utility of
        # player i is at most the utility of profile[i].

        # For a given conjecture over opponents actions (specified by j), compute the utility of player i where i plays action profile[player]
        action_utility = sum(
            variables[j]
            * self.game[
                orderedConsistent[j][:player]
                + (profile[player],)
                + orderedConsistent[j][player:]
            ][player]
            for j in range(len(variables))
        )

        for action in range(self.gameWrapper.numActions):
            prob += (
                sum(
                    variables[j]
                    * self.game[
                        orderedConsistent[j][:player]
                        + (action,)
                        + orderedConsistent[j][player:]
                    ][player]
                    for j in range(len(variables))
                )
                <= action_utility
            )

        # Solve the LP
        prob.solve(self.solver)

        # If the LP is infeasible, then there is no conjecture over opponents actions such that profile[i] is a BR.
        if prob.status == -1:
            return False

        return True

    def solve(self):
        """ """
        previous_size = float("inf")
        current_size = len(self.profiles)
        step = 0
        while previous_size - current_size > 0:
            step += 1
            if self.verbose:
                print("====================================")
                print("Starting Step {}".format(step))
            previous_size = current_size
            self.profiles = self.reduceProfiles(self.profiles)
            current_size = len(self.profiles)
            if self.verbose:
                print(
                    "Reduced from {} to {} profiles".format(previous_size, current_size)
                )
                print("====================================")
        if self.verbose:
            print("Exited with {} profiles".format(current_size))

        if self.writePath is not None:
            # Save as a pickle file the gameWrapper object, network, and final profiles
            if self.verbose:
                print("Saving to {}".format(self.writePath))
            try:
                with open(self.writePath, "wb") as f:
                    pickle.dump(
                        (
                            self.gameWrapper.numPlayers,
                            self.gameWrapper.numActions,
                            self.network,
                            self.profiles,
                        ),
                        f,
                    )
                if self.verbose:
                    print("Saved 🎊🎉☀️⛱️🍉!")
            except Exception as e:
                print("Failed to save ⛈️ due to: {}".format(e))
        return self.profiles


if __name__ == "__main__":
    from potluck import PotluckGame, PotluckArgs

    # game = PotluckGame(5)
    PotluckArgs.num_players = 4
    PotluckArgs.u = lambda x: x
    G = nx.Graph()

    # G empty
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)

    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 0)
    G.add_edge(0, 3)
    G.add_edge(1, 3)
    G.add_edge(2, 3)

    # G.add_edge(3, 4)

    game = PotluckGame(PotluckArgs.num_players, PotluckArgs.u)
    game.configureSolver(G, "PULP_CBC_CMD")
    print(game.solvePCE())
    # solver = DiscreteSolver(game, "PULP_CBC_CMD", G, writePath="results/test.pkl")
    # solver = PotluckSolver(game, "PYGLPK", G)
