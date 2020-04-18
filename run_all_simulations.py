import os
import pandas as pd
from tqdm import tqdm

from simulation_runner import SimulationRunner


def run_all_simulations_in_dir(directory, algo_class):
    print("running all simulations using: {}".format(algo_class))

    stats_dicts = []
    for filename in tqdm(os.listdir(directory)):
        if not filename.endswith(".csv"):
            continue

        sim_runner = SimulationRunner(os.path.join(directory, filename), algo_class)
        sim_runner.run_simulation()
        stats = sim_runner.get_performance_stats()
        stats_dicts.append(stats)

    df = pd.DataFrame(stats_dicts)
    df.to_csv(os.path.join("simulation_results", algo_class + ".csv"), index=False)


def run_multiple_simulations():
    sim_data_dir = 'demand_simulation_data/random_scenario/free_for_all'
    algo_classes_to_run = [
        'algo.naive_elevator.fifo_elevator.FIFOElevatorAlgo',
        'algo.naive_elevator.shabbat_elevator.ShabbatElevatorAlgo',
        'algo.naive_elevator.knuth_elevator.KnuthElevatorAlgo'
    ]

    for algo_class in algo_classes_to_run:
        run_all_simulations_in_dir(sim_data_dir, algo_class)


if __name__ == "__main__":
    run_multiple_simulations()
