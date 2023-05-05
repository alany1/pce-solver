import networkx as nx
import pygambit
import itertools
import numpy as np
import subprocess

from tqdm import tqdm

from game import SimpleGame

class SimpleMajorityGame(SimpleGame):
    """
    Version of the Majority game where players solely care about being in the majority group.

    This is the opposite of the traffic game, where players solely care about being in the minority group.
    """
    def __init__(self, numPlayers, numActions, verbose=False):
        """
        :param numPlayers: Number of players playing the [numActions] majority game.
        :param numActions: Number of actions available to each player.
        """
        super().__init__(numPlayers, numActions, [lambda x: SimpleMajorityGame.binaryPreference(i, x) for i in range(numPlayers)])
        self.game = self.createGame()
        self.verbose = verbose

    @staticmethod
    def binaryPreference(player, profile):
        majority = np.argmax(np.bincount(profile))
        return 1 if profile[player] == majority else 0

    def createGame(self):
        game = pygambit.Game.new_table([self.numActions] * self.numPlayers)

        game.title = "SimpleMajorityGame"

        # Iterate through all strategy profiles to set rewards (without using game.contingencies)
        for profile in itertools.product(
                range(self.numActions), repeat=self.numPlayers
        ):
            # Assign utility to each player
            for player in range(self.numPlayers):
                game[profile][player] = int(
                    self.utilities[player](profile)
                )

        return game

if __name__ == "__main__":
    majorityGame = SimpleMajorityGame(5, 2, verbose=True)

    G = nx.Graph()

    # G empty
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    # G.add_node(5)
    #
    # G.add_node(6)
    # G.add_node(7)
    # G.add_node(8)
    # #
    #
    # # Fully Connected
    #
    # # ====== 5 nodes ======
    G.add_edge(0, 1)
    G.add_edge(0, 2)
    G.add_edge(0, 3)
    G.add_edge(0, 4)
    # #
    # # G.add_edge(1, 2)
    # # G.add_edge(1, 3)
    # # G.add_edge(1, 4)
    # #
    # # G.add_edge(2, 3)
    # # G.add_edge(2, 4)
    # # #
    # # G.add_edge(3, 4)
    # # ====================
    #
    # # ====== 6 nodes ======
    # # G.add_edge(0, 1)
    # # G.add_edge(0, 2)
    # # G.add_edge(0, 3)
    # # G.add_edge(0, 4)
    # # G.add_edge(0, 5)
    # #
    # # G.add_edge(1, 2)
    # # G.add_edge(1, 3)
    # # G.add_edge(1, 4)
    # # G.add_edge(1, 5)
    # #
    # # G.add_edge(2, 3)
    # # G.add_edge(2, 4)
    # # G.add_edge(2, 5)
    #
    # # G.add_edge(3, 4)
    # # G.add_edge(3, 5)
    #
    # # G.add_edge(4, 5)
    #
    # # ====================
    #
    # # ====== 8 nodes ======
    # G.add_edge(0, 1)
    # G.add_edge(0, 2)
    # G.add_edge(0, 3)
    # G.add_edge(0, 4)
    # G.add_edge(0, 5)
    # G.add_edge(0, 6)
    # G.add_edge(0, 7)
    # G.add_edge(0, 8)
    #
    # G.add_edge(1, 2)
    # G.add_edge(1, 3)
    # G.add_edge(1, 4)
    # G.add_edge(1, 5)
    # G.add_edge(1, 6)
    # G.add_edge(1, 7)
    # G.add_edge(1, 8)
    #
    # G.add_edge(2, 3)
    # G.add_edge(2, 4)
    # G.add_edge(2, 5)
    # G.add_edge(2, 6)
    # G.add_edge(2, 7)
    # G.add_edge(2, 8)
    #
    # # G.add_edge(3, 4)
    # # G.add_edge(3, 5)
    # # G.add_edge(3, 6)
    #
    # # G.add_edge(4, 5)
    # # G.add_edge(4, 6)
    #
    # # G.add_edge(5, 6)
    #
    # # ====================
    #
    majorityGame.configureSolver(G, "PULP_CBC_CMD", writePath="results/Majority.pkl")
    pce = majorityGame.solvePCE()
