import pygambit
import itertools
import numpy as np
from potluck import PotluckGame
from game import SimpleGame

class TrafficGame(SimpleGame):

    def __init__(self, numPlayers, numRoads, u = lambda x:-x):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        u: the common utility function that is used by all players, assumed to be monotonic decreasing in number of
        drivers taking the same road.
        """
        self.numPlayers = numPlayers
        self.numRoads = numRoads
        self.u = u
        self.game = self.createGame()

    def createGame(self):
        """
        Create a new traffic game with numPlayers players and numRoads roads.
        """

        game = pygambit.Game.new_table([self.numRoads] * self.numPlayers)

        game.title = "Traffic_Game"

        # Iterate through all strategy profiles to set rewards (without using game.contingencies)
        for profile in itertools.product(range(self.numRoads), repeat=self.numPlayers):

            # For each profile, compute the number of drivers taking each road
            road_counts = np.bincount(profile, minlength=self.numRoads)

            # Assign utility to each player
            for player in range(self.numPlayers):
                game[profile][player] = int(self.u(road_counts[profile[player]]))

        return game

if __name__ == "__main__":
    traffic = TrafficGame(5, 3)
