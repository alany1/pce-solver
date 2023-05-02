import networkx as nx
import pygambit
import itertools
import numpy as np

from pceSolvers.discreteSolver import DiscreteSolver
from potluck import PotluckGame
from game import SimpleGame


class TrafficGame(SimpleGame):
    def __init__(self, numPlayers, numRoads, u=lambda x: -x):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        u: the common utility function that is used by all players, assumed to be monotonic decreasing in number of
        drivers taking the same road.
        """
        super().__init__(numPlayers, numRoads, [u] * numPlayers)
        self.game = self.createGame()

    def createGame(self):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        """

        game = pygambit.Game.new_table([self.numActions] * self.numPlayers)

        game.title = "Traffic_Game"

        # Iterate through all strategy profiles to set rewards (without using game.contingencies)
        for profile in itertools.product(
            range(self.numActions), repeat=self.numPlayers
        ):

            # For each profile, compute the number of drivers taking each road
            road_counts = np.bincount(profile, minlength=self.numActions)

            # Assign utility to each player
            for player in range(self.numPlayers):
                game[profile][player] = int(
                    self.utilities[player](road_counts[profile[player]])
                )

        return game


if __name__ == "__main__":
    traffic = TrafficGame(4, 3)

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

    traffic.configureSolver(G, "PULP_CBC_CMD", writePath="results/traffic.pkl")
    print(traffic.solvePCE())
