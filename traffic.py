import networkx as nx
import pygambit
import itertools
import numpy as np

from game import SimpleGame


class TrafficGame(SimpleGame):
    def __init__(self, numPlayers, numRoads, u=lambda x: -x):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        u: the common utility function that is used by all players, assumed to be monotonic decreasing in number of
        drivers taking the same road.
        """
        # super().__init__(numPlayers, numRoads, [u] * (numPlayers-1) + [lambda x: -u(x)])
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

def numUniqueRoads(profiles):
    """
    Get the minimum number of unique roads taken by all players in any profile as well as how many
    profiles attain that minimum.
    """
    min_unique_roads = len(set(profiles[0]))

    for profile in profiles:
        min_unique_roads = min(min_unique_roads, len(set(profile)))

    return min_unique_roads, [profile for profile in profiles if len(set(profile)) == min_unique_roads]

if __name__ == "__main__":
    from potluck import PotluckGame

    traffic = TrafficGame(9, 2)
    # potluck = PotluckGame(3)

    G = nx.Graph()

    # G empty
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)

    G.add_node(6)
    G.add_node(7)
    G.add_node(8)


    # Fully Connected

    # ====== 5 nodes ======
    # G.add_edge(0, 1)
    # G.add_edge(0, 2)
    # G.add_edge(0, 3)
    # G.add_edge(0, 4)
    #
    # G.add_edge(1, 2)
    # G.add_edge(1, 3)
    # G.add_edge(1, 4)
    #
    # G.add_edge(2, 3)
    # G.add_edge(2, 4)
    # #
    # G.add_edge(3, 4)
    # ====================

    # ====== 6 nodes ======
    # G.add_edge(0, 1)
    # G.add_edge(0, 2)
    # G.add_edge(0, 3)
    # G.add_edge(0, 4)
    # G.add_edge(0, 5)
    #
    # G.add_edge(1, 2)
    # G.add_edge(1, 3)
    # G.add_edge(1, 4)
    # G.add_edge(1, 5)
    #
    # G.add_edge(2, 3)
    # G.add_edge(2, 4)
    # G.add_edge(2, 5)

    # G.add_edge(3, 4)
    # G.add_edge(3, 5)

    # G.add_edge(4, 5)

    # ====================

    # ====== 8 nodes ======
    G.add_edge(0, 1)
    G.add_edge(0, 2)
    G.add_edge(0, 3)
    G.add_edge(0, 4)
    G.add_edge(0, 5)
    G.add_edge(0, 6)
    G.add_edge(0, 7)
    G.add_edge(0, 8)

    G.add_edge(1, 2)
    G.add_edge(1, 3)
    G.add_edge(1, 4)
    G.add_edge(1, 5)
    G.add_edge(1, 6)
    G.add_edge(1, 7)
    G.add_edge(1, 8)

    G.add_edge(2, 3)
    G.add_edge(2, 4)
    G.add_edge(2, 5)
    G.add_edge(2, 6)
    G.add_edge(2, 7)
    G.add_edge(2, 8)

    # G.add_edge(3, 4)
    # G.add_edge(3, 5)
    # G.add_edge(3, 6)

    # G.add_edge(4, 5)
    # G.add_edge(4, 6)

    # G.add_edge(5, 6)

    # ====================

    traffic.configureSolver(G, "PULP_CBC_CMD", writePath="results/traffic.pkl")
    pce = traffic.solvePCE()

    # Find the one with the most number of ones
    print(max(pce, key=lambda x: sum(x)))

    print("Number of unique roads used", numUniqueRoads(pce))

    # potluck.configureSolver(G, "PULP_CBC_CMD", writePath="results/potluck.pkl")
    # print(len(potluck.solvePCE()))

    print("Eigenvector Centrality", nx.eigenvector_centrality(G))
    nash = traffic.solveNash()
    print(len(nash))