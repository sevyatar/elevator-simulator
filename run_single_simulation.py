from simulation_runner import SimulationRunner

if __name__ == "__main__":
    sim_runner = SimulationRunner('demand_simulation_data/manual_scenario/small_office_1.csv',
                                  algo_class='algo.naive_elevator.knuth_elevator.KnuthElevatorAlgo')
    # algo_class='algo.naive_elevator.fifo_elevator.FIFOElevatorAlgo')
    # algo_class='algo.naive_elevator.shabbat_elevator.ShabbatElevatorAlgo')

    sim_runner.run_simulation()
    sim_runner.write_visualization_data_file()
    sim_runner.print_performance_stats()
