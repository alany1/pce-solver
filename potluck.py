import pygambit
import itertools
import numpy as np

class PotluckGame:

    def __init__(self, numPlayers, u = lambda x:x):
        """
        Create a new potluck game with numPlayers players.
        u: the common utility function that is used by all players, assumed to be monotonic in number of unique dishes.
        """
        self.numPlayers = numPlayers
        self.numActions = numPlayers
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
    def save(self, path):
        """
        Saves the game to a file.

        Parameters:
        path (str): The path to save the game to.
        """
        self.game.save_game(path)

if __name__ == '__main__':
    game = PotluckGame(5)

    # Compute pure nash equilibria
    solver = pygambit.nash.ExternalEnumPureSolver()

    # The pure nash equilibria will just be whenever each player brings a unique dish (N!)
    nash = solver.solve(game.game)

    game.save("potluck.efg")

    # print(nash[0].strategy)
