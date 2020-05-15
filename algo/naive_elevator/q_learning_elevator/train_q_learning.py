import os
import pandas as pd
import matplotlib.pyplot as plt

from simulation_runner import SimulationRunner
from algo.naive_elevator.q_learning_elevator import q_learning_elevator

Q_LEARNING_ALGO_CLASS = 'algo.naive_elevator.q_learning_elevator.q_learning_elevator.QLearningElevatorAlgo'
ELEVATOR_CONFIGURATION_FILE = 'elevator_configuration.yaml'

EPISODES = 50000
q_learning_elevator.ROUND_TO_START_LEARNING_DECAY = 0
q_learning_elevator.ROUND_TO_END_LEARNING_DECAY = EPISODES * (3 / 4)


def visualize_training_results(df):
    plt.figure()

    plt.subplot(311)
    plt.plot(df["time_to_complete_all_tasks"].tolist())
    plt.ylabel('time_to_complete_all_tasks')

    plt.subplot(312)
    plt.plot(df["total_time_to_destination"].tolist())
    plt.ylabel('total_time_to_destination')

    plt.subplot(313)
    plt.plot(df["median_time_to_destination"].tolist())
    plt.ylabel('median_time_to_destination')

    plt.show()


def run_simulations(scenarios_filenames, should_visualize_results=False):
    performance_stats = []
    for i, scenario_filename in enumerate(scenarios_filenames):
        sim_runner = SimulationRunner(scenario_filename, Q_LEARNING_ALGO_CLASS, ELEVATOR_CONFIGURATION_FILE)

        if i == 0:
            sim_runner.algo.reset_model()

        sim_runner.run_simulation()
        sim_runner.algo.save_model_to_file()
        # sim_runner.write_visualization_data_file()
        performance_stats.append(sim_runner.get_performance_stats())

        if i % 100 == 0:
            print(f"Running episode - {i}")
            sim_runner.print_performance_stats()
            print()
            print()

    df = pd.DataFrame(performance_stats)
    df.to_csv('algo/naive_elevator/q_learning_elevator/performance_stats.csv', index=False)

    if should_visualize_results:
        visualize_training_results(df)


def train_on_single_scenario():
    simulation_filename = 'demand_simulation_data/manual_scenario/tiny_office_1.csv'
    scenarios = [simulation_filename] * EPISODES
    run_simulations(scenarios, should_visualize_results=True)


def train_on_scenarios_dir():
    simulations_dir = 'demand_simulation_data/random_scenario/tiny_office_building'
    sim_files = [os.path.join(simulations_dir, f) for f in os.listdir(simulations_dir) if f.endswith('.csv')]

    scenarios = sim_files * ((EPISODES // len(sim_files)) + 1)
    run_simulations(scenarios[:EPISODES], should_visualize_results=True)


if "__main__" == __name__:
    # train_on_single_scenario()
    train_on_scenarios_dir()
