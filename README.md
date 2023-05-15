# Connectivity and Peer Confirming Equilibrium in Coordination Games

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

### Invoking the Solver


## Examples


## References