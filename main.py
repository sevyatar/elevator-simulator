import yaml
from elevator.elevator import Elevator
from demand_simulation.simulation import load_simulation_events
from performance_monitor import PerformanceMonitor

CONFIGURATION_FILE = 'configuration.yaml'


class SimulationRunner(object):
    def __init__(self):
        with open(CONFIGURATION_FILE, 'rb') as f:
            self.conf = yaml.load(f, Loader=yaml.FullLoader)

        elevator_conf = self.conf["ELEVATOR"]
        self.elevator = Elevator(elevator_conf)
        self.algo = self._get_algo(self.conf["ALGORITHM"]["ALGORITHM_CLASS"], elevator_conf)
        self.simulation_events = load_simulation_events(self.conf["SIMULATION"]["SIMULATION_FILE"],
                                                        self.conf["ELEVATOR"]["MAX_FLOOR"])
        self.performance_monitor = PerformanceMonitor()

    @staticmethod
    def _get_algo(algo_class, elevator_conf):
        '''
        Work some python magic -
        Load the initial module (probably 'algo'), and then recursively import its children until left with the
        relevant class type to instantiate.
        '''
        algo_module = ".".join(algo_class.split(".")[:-1])
        module = __import__(algo_module)
        for attribute in algo_class.split(".")[1:]:
            module = getattr(module, attribute)
        return module(elevator_conf)

    def _rerun_algo_with_new_pickup(self, current_ts, current_location, sim_event):
        self.algo.elevator_heartbeat(current_ts, current_location)
        event_data = self.algo.convert_event_for_rider_registration(sim_event["source_floor"],
                                                                    sim_event["destination_floor"])
        algo_output_tasks = self.algo.register_rider_pickup(sim_event["rider_id"], *event_data)
        self.elevator.register_next_tasks(algo_output_tasks)

    def _rerun_algo_with_new_dropoff(self, current_ts, current_location, rider_id, destination_floor):
        self.algo.elevator_heartbeat(current_ts, current_location)
        algo_output_tasks = self.algo.register_rider_destination(rider_id, destination_floor)
        self.elevator.register_next_tasks(algo_output_tasks)

    def run_simulation(self):
        next_event_index = 0
        rider_id_to_dropoff_location_map = {}
        active_riders_pickup_map = {}
        active_riders_dropoff_map = {}

        while next_event_index < len(self.simulation_events) or active_riders_pickup_map or active_riders_dropoff_map:
            if next_event_index < len(self.simulation_events):
                next_event_ts = self.simulation_events[next_event_index]["timestamp"]
            # If there are no more sim event coming up, just let the elevator run until all tasks are completed
            else:
                next_event_ts = None
                if self.elevator.is_task_list_empty():
                    break

            self.elevator.run_to_next_task_or_max_ts(max_timestamp=next_event_ts)
            current_ts, current_location = self.elevator.get_status()

            # A new rider is being registered
            if current_ts == next_event_ts:
                # Handle all riders registering at the same time
                while next_event_index < len(self.simulation_events) and \
                        self.simulation_events[next_event_index]["timestamp"] == current_ts:

                    sim_event = self.simulation_events[next_event_index]
                    rider_id = sim_event["rider_id"]
                    source_floor = sim_event["source_floor"]
                    destination_floor = sim_event["destination_floor"]

                    self.performance_monitor.rider_request(current_ts, rider_id, current_location)
                    self._rerun_algo_with_new_pickup(current_ts,
                                                     current_location,
                                                     sim_event)
                    active_riders_pickup_map[rider_id] = source_floor
                    rider_id_to_dropoff_location_map[rider_id] = destination_floor
                    next_event_index += 1

            # A pickup point is reached, register the rider's dropoff
            if current_location in active_riders_pickup_map.values():
                picked_up_rider_ids = \
                    [a for a in active_riders_pickup_map.keys() if active_riders_pickup_map[a] == current_location]
                for rider_id in picked_up_rider_ids:
                    self.performance_monitor.rider_pickup(current_ts, rider_id, current_location)
                    self.algo.report_rider_pickup(current_ts, rider_id)
                    dropoff_floor = rider_id_to_dropoff_location_map[rider_id]
                    active_riders_dropoff_map[rider_id] = dropoff_floor
                    self._rerun_algo_with_new_dropoff(current_ts,
                                                      current_location,
                                                      rider_id,
                                                      dropoff_floor)
                    del active_riders_pickup_map[rider_id]

            # A dropoff point is reached
            if current_location in active_riders_dropoff_map.values():
                dropped_off_rider_ids = \
                    [a for a in active_riders_dropoff_map.keys() if active_riders_dropoff_map[a] == current_location]
                for rider_id in dropped_off_rider_ids:
                    self.performance_monitor.rider_dropoff(current_ts, rider_id, current_location)
                    self.algo.report_rider_dropoff(current_ts, rider_id)
                    del active_riders_dropoff_map[rider_id]

    def print_simulation_results(self):
        print(type(self.algo).__name__)
        self.performance_monitor.print_events()
        self.performance_monitor.print_performance_stats()


if __name__ == "__main__":
    sim_runner = SimulationRunner()
    sim_runner.run_simulation()
    sim_runner.print_simulation_results()
