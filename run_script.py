from majority import simulateRandomGraphs
import pickle

if __name__ == "__main__":
    results = {}
    n = 8
    for p in [0.25, 0.5, 0.75]:
        res, goodGraphs, badGraphs = simulateRandomGraphs(100, n, p)
        results[p] = res
        with open("results/majority_random_graphs.pkl", "wb") as f:
            pickle.dump(results, f)

    print(results)
