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

        consistent = []
        for p in profilesToConsider:
            if all(profile[i] == p[i] for i in self.network.neighbors(player)):
                consistent.append(p)

        return consistent

    def reduceProfiles(self, profilesToConsider):
        """
        Applies operator B_G.
        """
        pass

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

