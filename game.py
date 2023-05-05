import pygambit
import itertools
import numpy as np

from pceSolvers.discreteSolver import DiscreteSolver


class SimpleGame:
    def __init__(self, numPlayers, numActions, utilities):
        """
        Create a new simple game with numPlayers players and numActions actions.
        utilities[List[len(numPlayers)]]: list of utility functions for each player.

        The resulting game wrapper is discrete, finite, and each player has the same actions available.
        """
        self.numPlayers = numPlayers
        self.numActions = numActions
        self.utilities = utilities

    def configureSolver(
        self, network, solverType="PULP_CBC_CMD", writePath="results/test.pkl"
    ):
        """
        Configure the solver to be used for solving the game.
        """
        self.solver = DiscreteSolver(
            self, solverType, network, verbose=self.verbose, writePath=writePath
        )
        print("Configured Solver!")

    def solvePCE(self):
        """
        Solve the game using the solver.
        """
        out = self.solver.solve()
        # print("Solved Game!")
        return out

    def solveNash(self):
        solver = pygambit.nash.ExternalEnumPureSolver()
        return solver.solve(self.game)
