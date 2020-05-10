import pandas as pd
from tqdm import tqdm

from simulation_runner import SimulationRunner
from algo.naive_elevator.q_learning_elevator import q_learning_elevator

# SIMULATIONS_DIR = 'demand_simulation_data/random_scenario/free_for_all'
Q_LEARNING_ALGO_CLASS = 'algo.naive_elevator.q_learning_elevator.q_learning_elevator.QLearningElevatorAlgo'
ELEVATOR_CONFIGURATION_FILE = 'elevator_configuration.yaml'

# SIMULATION_FILENAME = 'demand_simulation_data/manual_scenario/small_office_2.csv'
SIMULATION_FILENAME = 'demand_simulation_data/manual_scenario/tiny_office_1.csv'

EPISODES = 50000
q_learning_elevator.ROUND_TO_START_LEARNING_DECAY = 0
q_learning_elevator.ROUND_TO_END_LEARNING_DECAY = EPISODES * (3 / 4)

def train():
    performance_stats = []
    for i in range(EPISODES):
        sim_runner = SimulationRunner(SIMULATION_FILENAME, Q_LEARNING_ALGO_CLASS, ELEVATOR_CONFIGURATION_FILE)

        if i == 0:
            sim_runner.algo.reset_model()

        sim_runner.run_simulation()
        sim_runner.algo.save_model_to_file()
        # sim_runner.write_visualization_data_file()
        performance_stats.append(sim_runner.get_performance_stats())

        if i % 500 == 0:
            print(f"Running episode - {i}")
            sim_runner.print_performance_stats()
            pd.DataFrame(performance_stats).to_csv('algo/naive_elevator/q_learning_elevator/performance_stats.csv',
                                                   index=False)
            print()
            print()
            print()



if "__main__" == __name__:
    train()
