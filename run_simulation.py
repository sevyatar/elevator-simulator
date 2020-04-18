import os
import yaml
import tqdm
import time
import pandas as pd
from elevator.elevator import Elevator
from demand_simulation_data.load_simulation_data import load_simulation_events
from monitoring.performance_monitor import PerformanceMonitor

CONFIGURATION_FILE = 'configuration.yaml'


class SimulationRunner(object):
    def __init__(self, simulation_filename, algo_class=None):
        with open(CONFIGURATION_FILE, 'rb') as f:
            self.conf = yaml.load(f, Loader=yaml.FullLoader)

        elevator_conf = self.conf["ELEVATOR"]
        self.elevator = Elevator(elevator_conf)
        self.simulation_events = load_simulation_events(simulation_filename)
        self.max_floor = max(set([a["source_floor"] for a in self.simulation_events] +
                                 [a["destination_floor"] for a in self.simulation_events]))
        self.algo_class = algo_class if algo_class else self.conf["ALGORITHM"]["ALGORITHM_CLASS"]
        self.algo = self._get_algo(elevator_conf)
        self.performance_monitor = PerformanceMonitor(self.max_floor)

        self.current_ts = 0
        self.current_location = None

        self.rider_id_to_dropoff_location_map = {}
        self.active_riders_pickup_map = {}
        self.active_riders_dropoff_map = {}
        self.next_event_index = 0

    def get_algo_class(self):
        return self.algo_class

    def _get_algo(self, elevator_conf):
        '''
        Work some python magic -
        Load the initial module (probably 'algo'), and then recursively import its children until left with the
        relevant class type to instantiate.
        '''
        algo_module = ".".join(self.algo_class.split(".")[:-1])
        module = __import__(algo_module)
        for attribute in self.algo_class.split(".")[1:]:
            module = getattr(module, attribute)
        return module(elevator_conf, self.max_floor)

    def _rerun_algo_with_new_pickup(self, current_ts, current_location, sim_event):
        self.algo.elevator_heartbeat(current_ts, current_location)
        event_data = self.algo.convert_event_for_rider_registration(sim_event["source_floor"],
                                                                    sim_event["destination_floor"])
        algo_output_tasks = self.algo.register_rider_pickup(current_ts, sim_event["rider_id"], *event_data)
        self.elevator.register_next_tasks(algo_output_tasks)

    def _rerun_algo_with_new_dropoff(self, current_ts, current_location, rider_id, destination_floor):
        self.algo.elevator_heartbeat(current_ts, current_location)
        algo_output_tasks = self.algo.register_rider_destination(current_ts, rider_id, destination_floor)
        self.elevator.register_next_tasks(algo_output_tasks)

    def _record_all_rider_requests(self):
        # Loop over all riders registering at the same time
        while self.next_event_index < len(self.simulation_events) and \
                self.simulation_events[self.next_event_index]["timestamp"] == self.current_ts:
            sim_event = self.simulation_events[self.next_event_index]
            rider_id = sim_event["rider_id"]
            source_floor = sim_event["source_floor"]
            destination_floor = sim_event["destination_floor"]

            self.performance_monitor.rider_request(self.current_ts, rider_id, source_floor,
                                                   destination_floor, self.current_location)
            self._rerun_algo_with_new_pickup(self.current_ts,
                                             self.current_location,
                                             sim_event)
            self.active_riders_pickup_map[rider_id] = source_floor
            self.rider_id_to_dropoff_location_map[rider_id] = destination_floor
            self.next_event_index += 1

    def _handle_rider_pickup(self):
        picked_up_rider_ids = \
            [a for a in self.active_riders_pickup_map.keys()
             if self.active_riders_pickup_map[a] == self.current_location]

        for rider_id in picked_up_rider_ids:
            self.performance_monitor.rider_pickup(self.current_ts, rider_id, self.current_location)
            self.algo.report_rider_pickup(self.current_ts, rider_id)
            dropoff_floor = self.rider_id_to_dropoff_location_map[rider_id]
            self.active_riders_dropoff_map[rider_id] = dropoff_floor
            self._rerun_algo_with_new_dropoff(self.current_ts,
                                              self.current_location,
                                              rider_id,
                                              dropoff_floor)
            del self.active_riders_pickup_map[rider_id]

    def _handle_rider_dropoff(self):
        dropped_off_rider_ids = \
            [a for a in self.active_riders_dropoff_map.keys() if
             self.active_riders_dropoff_map[a] == self.current_location]
        for rider_id in dropped_off_rider_ids:
            self.performance_monitor.rider_dropoff(self.current_ts, rider_id, self.current_location)
            self.algo.report_rider_dropoff(self.current_ts, rider_id)
            del self.active_riders_dropoff_map[rider_id]

    def run_simulation(self):
        # Keep running the simulation as long as there are still future events or there are still incomplete rides
        while self.next_event_index < len(self.simulation_events) \
                or self.active_riders_pickup_map or self.active_riders_dropoff_map:

            # Are there any more tasks?
            if self.next_event_index < len(self.simulation_events):
                next_event_ts = self.simulation_events[self.next_event_index]["timestamp"]
            else:
                # If there are no more sim event coming up, just let the elevator run until all tasks are completed
                next_event_ts = None
                if self.elevator.is_task_list_empty():
                    break

            self.elevator.run_to_next_task_or_max_ts(max_timestamp=next_event_ts)
            self.current_ts, self.current_location = self.elevator.get_status()

            # A new rider(s) is being registered
            if self.current_ts == next_event_ts:
                self._record_all_rider_requests()

            # A pickup point is reached, register the rider's dropoff
            if self.current_location in self.active_riders_pickup_map.values():
                self._handle_rider_pickup()

            # A dropoff point is reached
            if self.current_location in self.active_riders_dropoff_map.values():
                self._handle_rider_dropoff()

        # Log all floors visited
        self.performance_monitor.floors_visited(self.elevator.get_ts_to_arrival_floor_log())

    def write_visualization_data_file(self):
        self.performance_monitor.write_visualization_data_file()

    def get_performance_stats(self):
        return self.performance_monitor.calculate_performace_stats()

    def print_performance_stats(self):
        self.performance_monitor.print_performance_stats()


def run_single_simulation():
    sim_runner = SimulationRunner('demand_simulation_data/manual_scenario/small_office_1.csv')
    sim_runner.run_simulation()
    sim_runner.write_visualization_data_file()
    sim_runner.print_performance_stats()


def run_all_simulations_in_dir(directory, algo_class):
    print("running all simulations using: {}".format(algo_class))

    stats_dicts = []
    for filename in tqdm.tqdm(os.listdir(directory)):
        if not filename.endswith(".csv"):
            continue

        sim_runner = SimulationRunner(os.path.join(directory, filename), algo_class)
        sim_runner.run_simulation()
        stats = sim_runner.get_performance_stats()
        stats_dicts.append(stats)

    df = pd.DataFrame(stats_dicts)
    df.to_csv(os.path.join("simulation_results", algo_class + ".csv"), index=False)


def run_multiple_simulations():
    sim_data_dir = 'demand_simulation_data/random_scenario/office_building'
    algo_classes_to_run = [
        'algo.naive_elevator.fifo_elevator.FIFOElevatorAlgo',
        'algo.naive_elevator.shabbat_elevator.ShabbatElevatorAlgo'
    ]

    for algo_class in algo_classes_to_run:
        run_all_simulations_in_dir(sim_data_dir, algo_class)
        time.sleep(0.1)


if __name__ == "__main__":
    # run_single_simulation()
    run_multiple_simulations()

