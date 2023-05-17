# Connectivity and Peer Confirming Equilibrium in Coordination Games

[Paper Link](https://alany1.github.io/pce/pce_paper.pdf)

This repository contains the code for "Connectivity and Peer Confirming Equilibrium in Coordination Games." We present a solver for determining Peer Confirming Equilibrium (PCE) sets in discrete games. 

## Installation

### Dependencies
Install dependencies in a new conda environment:
```
conda create -n pce python=3.7
conda activate pce
pip install -r requirements.txt
```

### LP Solvers and Graph Tools
We rely on PuLP to solve linear programs. PuLP is a python interface to several LP solvers. We recommend using CBC. You will need to install CBC separately. See [here](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html) for instructions.

For generating networks, we also use geng and showg from the nauty suite to create regular graphs. See [here](https://pallini.di.uniroma1.it/) for instructions. 

## Usage

### Creating a Discrete Game
The `SimpleGame` class is used to represent a discrete game. It is initialized with a list of players and a list of actions for each player. Currently, we assume players have access to the same actions, but this can be easily adapted to the case where players have different action sets. 

To create a new game, first import the `SimpleGame` class:
```
from game import SimpleGame
```
Then, create a new subclass of `SimpleGame` that creates a pyGambit game object.
``` 
class myGame(SimpleGame):
    def __init__(self, numPlayers, numActions, utilities):
        super().__init__(numPlayers, numActions, utilities)
        self.game = self.createGame()
        self.verbose = verbose
        
    def createGame(self):
        game = gambit.Game.new_table([self.numActions]*self.numPlayers)
        for profile in itertools.product(range(self.numActions), repeat=self.numPlayers):
            game[profile][player] = ...
        return game
        
gameWrapper = myGame(...)
```
### Invoking the Solver

Assuming your game wrapper object has been created and you have defined some network ```G```, you can invoke the solver as follows:
```
gameWrapper.configureSolver(G, "PULP_CBC_CMD")
pce = gameWrapper.solve()
```


## Examples
See `majority.py`, `potluck.py`, and `traffic.py` for examples of a few games and analysis done on them. See the paper for more details on our analysis.
