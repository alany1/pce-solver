import pygambit
import itertools
import numpy as np

class SimpleGame:
    def __init__(self, numPlayers, numActions, utilities):
        """
        Create a new simple game with numPlayers players and numActions actions.
        utilities[List[len(numPlayers)]]: list of utility functions for each player.

        The resulting game wrapper is discrete, finite, and each player has the same actions available.
        """
        self.numPlayers = numPlayers
        self.numActions = numActions
        self.utilities = utilities