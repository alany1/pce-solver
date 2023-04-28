from params_proto import Proto, ParamsProto, PrefixProto
from potluck import PotluckGame
import pulp as pl
import numpy as np
import networkx as nx


class PotluckArgs(PrefixProto):
    """SolveArgs is a ParamsProto class that contains all the parameters
    needed for the solver.
    """
    num_players: int = 5

    # Fix this to use eval
    u = lambda x: x
    graph = None


class PotluckSolver:
    def __init__(self, game, solver, network: nx.Graph = None):
        self.game = game
        self.solver = pl.getSolver(solver)
        self.model = pl.LpProblem("Potluck", pl.LpMaximize)
        self.profiles = self.game.contingencies
        self.network = network
        assert self.network is not None, "Network cannot be None!"

    def consistentStrategies(self, profile, player, profilesToConsider):
        """
        Returns all strategy profiles consistent with the given profile for the given player's strategic information
        encoded by the network self.network.
        """

        consistent = set()
        for p in profilesToConsider:
            if all(profile[i] == p[i] for i in self.network.neighbors(player)):
                opponents = list(p)[:player] + list(p)[player + 1:]
                consistent.add(tuple(opponents))

        return consistent

    def reduceProfiles(self, profilesToConsider):
        """
        Applies operator B_G.
        """
        reducedProfiles = []
        for profile in profilesToConsider:
            # Check if for all players, is everyone playing a network-consistent best reply.
            clear = True
            for player in range(self.game.numPlayers):
                consistent = self.consistentStrategies(profile, player, profilesToConsider)

                # Check if there is some viable conjecture (distribution over consistent) where profile_i is a B.R.
                if not self.checkBestResponse(profile, player, consistent):
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
        prob = pl.LpProblem("Best Response", pl.LpMaximize)

        # Create the variables. Introduce one variable for each consistent strategy profile.
        variables = []
        for p in consistent:
            variables.append(pl.LpVariable(str(p), 0, 1))

        # Create the objective function. The objective is not important as we just care about feasibility.
        prob += 0

        # Add the probability constraint that all variables must sum to 1.
        prob += sum(variables) == 1

        # Add the utility constraints. For each possible action of player i, add a constraint that the utility of
        # player i is at most the utility of profile[i].
        action_utility = sum(
            variables[j] * self.game[profile[:player] + (profile[player],) + profile[player + 1:]][player] for j in
            range(len(variables)))

        for action in range(self.game.numActions[player]):
            prob += sum(variables[j] * self.game[profile[:player] + (action,) + profile[player + 1:]][player]
                        for j in range(len(variables))) <= action_utility

        # Solve the LP
        prob.solve(self.solver)

        # If the LP is infeasible, then there is no conjecture over opponents actions such that profile[i] is a BR.
        if prob.status == -1:
            return False

        return True

    def addConstraints(self):
        pass


if __name__ == "__main__":
    # game = PotluckGame(5)
    PotluckArgs.num_players = 2
    PotluckArgs.u = lambda x: x
    G = nx.Graph()

    # G empty
    G.add_node(1)

    G.add_node(2)

    game = PotluckGame(PotluckArgs.num_players, PotluckArgs.u)

    solver = PotluckSolver(game, "PULP_CBC_CMD", G)
