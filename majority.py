import pickle

import networkx as nx
import pygambit
import itertools
import numpy as np
import subprocess

from matplotlib import pyplot as plt
from networkx.generators.atlas import graph_atlas_g
from tqdm import tqdm

from game import SimpleGame
from traffic import parse_edge_list


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
                # game[profile][player] = int(
                #     self.utilities[player](profile)
                # )
                game[profile][player] = int(SimpleMajorityGame.binaryPreference(player, profile))

        return game

def analyze(n, gamma, game):
    """
    Examine all gamma-regular graphs with n nodes and determine if there exists a PCE with
    an even split among players.

    TODO: Save all graphs that permit an even split.
    """
    assert gamma < n, "gamma must be less than n"

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

    if gamma != 0 and edge_lists == ['']:
        print("No graphs found!")
        return None, None

    all_graphs = []
    for edge_list in edge_lists:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(parse_edge_list(edge_list))
        all_graphs.append(G)

    for graph in tqdm(
            all_graphs,
            desc=f"Solving gamma-complete graphs for n={n}, gamma={gamma}",
    ):
        game.configureSolver(
            graph, "PULP_CBC_CMD", writePath=None
        )  # "results/traffic.pkl")

        pce = game.solvePCE()
        count_ones = [sum(x)==n//2 for x in pce]
        found = np.argmax(count_ones)
        # smallest = min(pce, key=lambda x: sum(x))
        if any(count_ones):
            print("Found a graph with an even split!")
            return pce[found], graph

    return None,None

def searchGraphs(n, majorityGame):
    """
    Iterate through all possible graphs of size n and find the graphs that give rise to PCE sets containing a
    profile where n/2 players take each action.
    """

    # Iterate through all possible graphs
    graphs = []
    for i, graph in enumerate(graph_atlas_g()):
        if len(graph) == n:
            graphs.append(graph)

    goodGraphs = []
    badGraphs = []
    for graph in tqdm(graphs, desc="Searching graphs", colour="green"):
    # Check if the graph gives rise to a PCE set containing a profile where n/2 players take each action
        majorityGame.configureSolver(graph, "PULP_CBC_CMD", writePath="results/Majority.pkl")
        pce = majorityGame.solvePCE()

        for profile in pce:
            count_ones = sum(profile)
            if count_ones == n//2 or len(profile)-count_ones == n//2:
                goodGraphs.append(graph)
                print("Found graph with n/2 players taking each action")
                break
        else:
            badGraphs.append(graph)
    return goodGraphs, badGraphs



if __name__ == "__main__":

    n = 7

    majorityGame = SimpleMajorityGame(n, 2, verbose=True)

    try:
        with open(f"results/majority_{n}.pkl", "rb") as f:
            results = pickle.load(f)
    except FileNotFoundError:
        print("File not found, analyzing graphs")
        results = {}
        for gamma in range(n):
            print(f"Analyzing gamma={gamma}")
            results[gamma] = analyze(n, gamma, majorityGame)

        # Save results
        with open(f"results/majority_{n}.pkl", "wb") as f:
            pickle.dump(results, f)

    print(results)

    # Draw the graphs
    for gamma, (pce, graph) in results.items():
        if pce is not None:
            nx.draw(graph, with_labels=True)
            plt.title(f"Gamma={gamma}")
            plt.show()


    # ==================================================================================
    # import pickle
    #
    # n = 6
    # majorityGame = SimpleMajorityGame(n, 2, verbose=True)
    #
    # try:
    #     with open(f"results/majority_{n}.pkl", "rb") as f:
    #         data = pickle.load(f)
    #         goodGraphs, badGraphs = data
    # except FileNotFoundError:
    #     print("File not found, searching graphs")
    #     goodGraphs, badGraphs = searchGraphs(n, majorityGame)
    #     goodGraphs = sorted(goodGraphs, key=lambda g: len(g.edges()))
    #     badGraphs = sorted(badGraphs, key=lambda g: len(g.edges()))
    #     # Save to pickle
    #     with open(f"results/majority_{n}.pkl", "wb") as f:
    #         data = [goodGraphs, badGraphs]
    #         pickle.dump(data, f)
    #
    # # Visualize each graph
    # for graph in badGraphs:
    #     nx.draw(graph, with_labels=True)
    #     plt.show()

    # ==================================================================================






    # G = nx.Graph()
    # # G empty
    # G.add_node(0)
    # G.add_node(1)
    # G.add_node(2)
    # G.add_node(3)
    # G.add_node(4)
    # G.add_node(5)
    # #
    # # G.add_node(6)
    # # G.add_node(7)
    # # G.add_node(8)
    # # #
    # #
    # # # Fully Connected
    # #
    # # # ====== 5 nodes ======
    # G.add_edge(0, 1)
    # G.add_edge(0, 2)
    # G.add_edge(0, 3)
    # G.add_edge(0, 4)
    # G.add_edge(0, 5)
    # # #
    # G.add_edge(1, 2)
    # G.add_edge(1, 3)
    # G.add_edge(1, 4)
    # # G.add_edge(1, 5)
    # # #
    # G.add_edge(2, 3)
    # # G.add_edge(2, 4)
    # G.add_edge(2, 5)
    # # # #
    # G.add_edge(3, 4)
    # # G.add_edge(3, 5)
    #
    # G.add_edge(4, 5)
    #
    # # # ====================
    # #
    # # # ====== 6 nodes ======
    # # # G.add_edge(0, 1)
    # # # G.add_edge(0, 2)
    # # # G.add_edge(0, 3)
    # # # G.add_edge(0, 4)
    # # # G.add_edge(0, 5)
    # # #
    # # # G.add_edge(1, 2)
    # # # G.add_edge(1, 3)
    # # # G.add_edge(1, 4)
    # # # G.add_edge(1, 5)
    # # #
    # # # G.add_edge(2, 3)
    # # # G.add_edge(2, 4)
    # # # G.add_edge(2, 5)
    # #
    # # # G.add_edge(3, 4)
    # # # G.add_edge(3, 5)
    # #
    # # # G.add_edge(4, 5)
    # #
    # # # ====================
    # #
    # # # ====== 8 nodes ======
    # # G.add_edge(0, 1)
    # # G.add_edge(0, 2)
    # # G.add_edge(0, 3)
    # # G.add_edge(0, 4)
    # # G.add_edge(0, 5)
    # # G.add_edge(0, 6)
    # # G.add_edge(0, 7)
    # # G.add_edge(0, 8)
    # #
    # # G.add_edge(1, 2)
    # # G.add_edge(1, 3)
    # # G.add_edge(1, 4)
    # # G.add_edge(1, 5)
    # # G.add_edge(1, 6)
    # # G.add_edge(1, 7)
    # # G.add_edge(1, 8)
    # #
    # # G.add_edge(2, 3)
    # # G.add_edge(2, 4)
    # # G.add_edge(2, 5)
    # # G.add_edge(2, 6)
    # # G.add_edge(2, 7)
    # # G.add_edge(2, 8)
    # #
    # # # G.add_edge(3, 4)
    # # # G.add_edge(3, 5)
    # # # G.add_edge(3, 6)
    # #
    # # # G.add_edge(4, 5)
    # # # G.add_edge(4, 6)
    # #
    # # # G.add_edge(5, 6)
    # #
    # # # ====================
    # #
    # majorityGame.configureSolver(G, "PULP_CBC_CMD", writePath="results/Majority.pkl")
    # pce = majorityGame.solvePCE()
    # print(pce)
    #
    # solver = pygambit.nash.ExternalEnumPureSolver()
    #
    # # The pure nash equilibria will just be whenever each player brings a unique dish (N!)
    # nash = solver.solve(majorityGame.game)
    # print("Nash Equilibria: ", nash)

