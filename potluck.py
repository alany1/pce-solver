import pygambit
import itertools
import numpy as np
from params_proto import PrefixProto

from game import SimpleGame
from pceSolvers.discreteSolver import DiscreteSolver

class PotluckArgs(PrefixProto):
    """SolveArgs is a ParamsProto class that contains all the parameters
    needed for the solver.
    """

    num_players: int = 5

    # Fix this to use eval
    u = lambda x: x
    graph = None


class PotluckGame(SimpleGame):

    def __init__(self, numPlayers, u=lambda x: x):
        """
        Create a new potluck game with numPlayers players.
        u: the common utility function that is used by all players, assumed to be monotonic in number of unique dishes.
        """
        super().__init__(numPlayers, numPlayers, [u] * numPlayers)
        self.game = PotluckGame.potluck_game(numPlayers, u)

    @staticmethod
    def potluck_game(n, u):
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

    def configureSolver(self, network, solverType="PULP_CBC_CMD", writePath="results/test.pkl"):
        """
        Configure the solver to be used for solving the game.
        """
        self.solver = DiscreteSolver(self, solverType, network, writePath=writePath)
        print("Configured Solver!")

    def solve(self):
        """
        Solve the game using the solver.
        """
        out = self.solver.solve()
        print("Solved Game!")
        return out

if __name__ == '__main__':
    game = PotluckGame(2)

    # Compute pure nash equilibria
    solver = pygambit.nash.ExternalEnumPureSolver()

    # The pure nash equilibria will just be whenever each player brings a unique dish (N!)
    nash = solver.solve(game.game)
    print(nash)
