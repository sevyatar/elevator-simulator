import os
import pandas as pd

DIRECTORY = "simulation_results"

def compare_simulation_results():
    algo_results = {}
    for filename in os.listdir(DIRECTORY):
        if not filename.endswith(".csv"):
            continue

        algo_name = filename[:-4]
        df = pd.read_csv(os.path.join(DIRECTORY, filename))
        algo_results[algo_name] = df

    for algo_name, results_df in algo_results.items():
        print("ALGO: {}".format(algo_name))
        print(results_df.describe())


if __name__ == "__main__":
    compare_simulation_results()
