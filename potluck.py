import pygambit
import itertools
import numpy as np
from matplotlib import pyplot as plt
from params_proto import PrefixProto

from game import SimpleGame
from pceSolvers.discreteSolver import DiscreteSolver

import networkx as nx


class PotluckArgs(PrefixProto):
    """SolveArgs is a ParamsProto class that contains all the parameters
    needed for the solver.
    """

    num_players: int = 5

    # Fix this to use eval
    u = lambda x: x
    graph = None


class PotluckGame(SimpleGame):
    def __init__(self, numPlayers, verbose=False, u=lambda x: x):
        """
        Create a new potluck game with numPlayers players.
        u: the common utility function that is used by all players, assumed to be monotonic in number of unique dishes.
        """
        super().__init__(numPlayers, numPlayers, [u] * numPlayers)
        self.game = PotluckGame.createGame(numPlayers, u)
        self.verbose = verbose

    @staticmethod
    def createGame(n, u):
        """
        Creates the potluck game using the gambit library.

        Parameters:
        n (int): The number of players in the game.
        u (function): The common utility function, which takes the number of unique dishes as input and returns the utility.

        Returns:
        gambit.Game: The potluck game represented as a normal form game in gambit.
        """

        # Create a list of strategies for each player
        game = pygambit.Game.new_table([n] * n)

        game.title = "Potluck Game"

        # Iterate through all strategy profiles to set rewards (without using game.contingencies)
        for profile in itertools.product(range(n), repeat=n):
            # Compute the number of unique dishes
            unique_dishes = len(set(profile))

            # Calculate the utility using the provided function
            utility = u(unique_dishes)

            # Assign the utility to each player
            for player in range(n):
                game[profile][player] = utility

        return game


if __name__ == "__main__":
    # game = PotluckGame(2)

    # # Compute pure nash equilibria
    # solver = pygambit.nash.ExternalEnumPureSolver()
    #
    # # The pure nash equilibria will just be whenever each player brings a unique dish (N!)
    # nash = solver.solve(game.game)
    # print(nash)

    # Generate some graphs and look at the computed PCE
    print("hey")
    n = 4
    p = 0.5
    game = PotluckGame(n, verbose=True)
    for i in range(4):
        print(i)
        random_graph = nx.gnp_random_graph(n, p)
        print("done generating graph")
        game.configureSolver(random_graph)
        pce = game.solvePCE()
        print(pce)
        nx.draw(random_graph, with_labels=True)
        plt.show()
