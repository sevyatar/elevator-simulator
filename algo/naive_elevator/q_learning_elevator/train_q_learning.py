import os
from tqdm import tqdm

from simulation_runner import SimulationRunner

# SIMULATIONS_DIR = 'demand_simulation_data/random_scenario/free_for_all'
Q_LEARNING_ALGO_CLASS = 'algo.naive_elevator.q_learning_elevator.q_learning_elevator.QLearningElevatorAlgo'
ELEVATOR_CONFIGURATION_FILE = 'elevator_configuration.yaml'

SIMULATION_FILENAME = 'demand_simulation_data/manual_scenario/small_office_2.csv'

EPISODES = 20000

def train():

    for i in range(EPISODES):
        sim_runner = SimulationRunner(SIMULATION_FILENAME, Q_LEARNING_ALGO_CLASS, ELEVATOR_CONFIGURATION_FILE)

        if i == 0:
            sim_runner.algo.reset_model()

        sim_runner.run_simulation()
        sim_runner.algo.save_model_to_file()
        # sim_runner.write_visualization_data_file()
        sim_runner.print_performance_stats()
        print()
        print()
        print()


if "__main__" == __name__:
    train()
