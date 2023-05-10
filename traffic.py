import pickle
import networkx as nx
import pygambit
import itertools
import numpy as np
import subprocess

from tqdm import tqdm

from game import SimpleGame


class TrafficGame(SimpleGame):
    def __init__(self, numPlayers, numRoads, verbose=False, u=lambda x: -x):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        u: the common utility function that is used by all players, assumed to be monotonic decreasing in number of
        drivers taking the same road.
        """
        # super().__init__(numPlayers, numRoads, [u] * (numPlayers-1) + [lambda x: -u(x)])
        super().__init__(numPlayers, numRoads, [u] * numPlayers)
        self.game = self.createGame()
        self.verbose = verbose

    def createGame(self):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        """

        game = pygambit.Game.new_table([self.numActions] * self.numPlayers)

        game.title = "trafficGame"

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

    return min_unique_roads, [
        profile for profile in profiles if len(set(profile)) == min_unique_roads
    ]


def analyzeGame(minN, maxN):
    """
    Examine all gamma-regular graphs with up to maxN nodes and find the number of unique roads taken by all players.
    """
    results = {}
    for n in range(minN, maxN + 1):
        for k in range(1, n + 1):
            game = TrafficGame(n, k, verbose=True)

            for gamma in range(1, n + 1):
                # Play this game on all of these graphs; count the number of unique roads taken by all players and we
                # want to get the minimum.

                # Look through all gamma-regular graphs with n nodes
                # n = 6
                # gamma = 3

                geng_cmd = f"geng -c -d{gamma} -D{gamma} {n}"
                showg_cmd = "showg -e"

                # Run the geng and showg commands and get the output
                geng_output = subprocess.run(
                    geng_cmd, stdout=subprocess.PIPE, shell=True, text=True
                )
                edge_list_output = subprocess.run(
                    showg_cmd,
                    input=geng_output.stdout,
                    stdout=subprocess.PIPE,
                    shell=True,
                    text=True,
                )

                # Split the output into individual edge lists
                edge_lists = edge_list_output.stdout.strip().split("\n\n")

                all_graphs = []
                for edge_list in edge_lists:
                    G = nx.Graph()
                    G.add_nodes_from(range(n))
                    G.add_edges_from(parse_edge_list(edge_list))
                    all_graphs.append(G)

                mins = []
                for graph in tqdm(
                    all_graphs,
                    desc=f"Solving gamma-complete graphs for n={n}, k={k}, gamma={gamma}",
                ):
                    game.configureSolver(
                        graph, "PULP_CBC_CMD", writePath=None
                    )  # "results/traffic.pkl")
                    unique, _ = numUniqueRoads(game.solvePCE())
                    mins.append(unique)

                idx = np.argmin(np.array(mins))
                results[(n, k, gamma)] = mins[idx], all_graphs[idx]

                # if the value is equal to k, then we are done with this value of gamma
                # since f is monotonically increasing in gamma

                # Save the results
                print("Saving results to results/traffic_regular_analysis_2.pkl")
                with open("results/traffic_regular_analysis_2.pkl", "wb") as f:
                    pickle.dump(results, f)

                if mins[idx] == k:
                    print(
                        f"Stopping early since we have found gamma={gamma} such that f(gamma)=k={k}"
                    )
                    break
            print(f"Finished analyzing n={n}, k={k}")
        print(f"Finished analyzing n={n}")
    print("Done analyzing all games! Saved to results/traffic_regular_analysis.pkl! 🍾")


def parse_edge_list(edge_list):
    lines = edge_list.split("\n")
    if len(lines) < 3:
        return []

    edges_line = '  '.join(lines[2:])
    edge_pairs = edges_line.split("  ")  # Split with two spaces
    edges = []
    for edge_pair in edge_pairs:
        u, v = map(int, edge_pair.split())
        edges.append((u, v))

    return edges


if __name__ == "__main__":
    from potluck import PotluckGame

    analyzeGame(2, 9)
    # traffic = TrafficGame(9, 2)

    import pickle

    with open("results/traffic_regular_analysis.pkl", "rb") as f:
        results = pickle.load(f)

    for key, (value, graph) in results.items():
        print(key, value)

    # # potluck = PotluckGame(3)
    #
    # G = nx.Graph()
    #
    # # G empty
    # G.add_node(0)
    # G.add_node(1)
    # G.add_node(2)
    # G.add_node(3)
    # G.add_node(4)
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
    # # G.add_edge(0, 1)
    # # G.add_edge(0, 2)
    # # G.add_edge(0, 3)
    # # G.add_edge(0, 4)
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
    # traffic.configureSolver(G, "PULP_CBC_CMD", writePath="results/traffic.pkl")
    # pce = traffic.solvePCE()
    #
    # # Find the one with the most number of ones
    # print(max(pce, key=lambda x: sum(x)))
    #
    # print("Number of unique roads used", numUniqueRoads(pce))
    #
    # # potluck.configureSolver(G, "PULP_CBC_CMD", writePath="results/potluck.pkl")
    # # print(len(potluck.solvePCE()))
    #
    # print("Eigenvector Centrality", nx.eigenvector_centrality(G))
    # nash = traffic.solveNash()
    # print(len(nash))
