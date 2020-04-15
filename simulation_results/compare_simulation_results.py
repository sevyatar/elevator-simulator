import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DIRECTORY = "simulation_results"


def _load_algo_results_data():
    algo_results = {}
    for filename in os.listdir(DIRECTORY):
        if not filename.endswith(".csv"):
            continue

        algo_name = filename[:-4]
        df = pd.read_csv(os.path.join(DIRECTORY, filename))
        algo_results[algo_name] = df

    return algo_results


def _print_algo_results(algo_results):
    for algo_name, results_df in algo_results.items():
        print("ALGO: {}".format(algo_name))
        print(results_df.describe())


def _display_plots(algo_results):
    metric_names = list(list(algo_results.values())[0])
    algo_names = [x.split(".")[-1] for x in algo_results.keys()]

    fig, axs = plt.subplots(len(metric_names))
    for i, metric in enumerate(metric_names):
        x_positions = np.arange(len(algo_names))
        means = []
        stds = []
        for algo_name, results_df in algo_results.items():
            means.append(results_df[metric].mean())
            stds.append(results_df[metric].std())

        axs[i].bar(x_positions, means, yerr=stds, align='center', alpha=0.5, ecolor='black', capsize=10)

        axs[i].set_xticks(x_positions)
        axs[i].set_xticklabels(algo_names)

        # axs[i].set_ylabel(metric)
        axs[i].set_title(metric)
        axs[i].yaxis.grid(True)

    # Save the figure and show
    fig.tight_layout()
    # fig.subplots_adjust(hspace=2)
    plt.show()

def compare_simulation_results():
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)

    algo_results = _load_algo_results_data()
    # _print_algo_results(algo_results)
    _display_plots(algo_results)


if __name__ == "__main__":
    compare_simulation_results()
