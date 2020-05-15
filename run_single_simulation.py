from simulation_runner import SimulationRunner

ELEVATOR_CONFIGURATION_FILE = 'elevator_configuration.yaml'


if __name__ == "__main__":
    sim_runner = SimulationRunner(
        elevator_config_filename=ELEVATOR_CONFIGURATION_FILE,
        # simulation_filename='demand_simulation_data/manual_scenario/small_office_1.csv',
        # simulation_filename='demand_simulation_data/manual_scenario/small_office_2.csv',
        simulation_filename='demand_simulation_data/manual_scenario/tiny_office_1.csv',
        # simulation_filename='demand_simulation_data/manual_scenario/medium_office_1.csv',
        # simulation_filename='demand_simulation_data/random_scenario/free_for_all/sim_524.csv',
        # algo_class='algo.up_down_elevator.knuth_elevator.KnuthElevatorAlgo')
        algo_class='algo.naive_elevator.knuth_elevator.KnuthElevatorAlgo')
        # algo_class='algo.naive_elevator.q_learning_elevator.q_learning_elevator.QLearningElevatorAlgo')
        # algo_class='algo.naive_elevator.fifo_elevator.FIFOElevatorAlgo')
        # algo_class='algo.naive_elevator.shabbat_elevator.ShabbatElevatorAlgo')

    sim_runner.run_simulation()
    sim_runner.write_visualization_data_file()
    sim_runner.print_performance_stats()
