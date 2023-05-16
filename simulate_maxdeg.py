import networkx as nx
import random

n = 8
p = 0.25
num_trials = 100000
count = 0

deg_threshold = n-3

for _ in range(num_trials):
    G = nx.gnp_random_graph(n, p)
    max_degree = max(dict(G.degree()).values())

    if max_degree <= deg_threshold:
        count += 1

probability = count / num_trials
print(probability)
