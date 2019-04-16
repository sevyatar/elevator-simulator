import yaml
from elevator.elevator import Elevator
from demand_simulation.simulation import LoadSimulationEvents
from performance_monitor import PerformanceMonitor

CONFIGURATION_FILE = 'configuration.yaml'

class SimulationRunner(object):
    def __init__(self):
        with open(CONFIGURATION_FILE, 'rb') as f:
            self.conf = yaml.load(f, Loader=yaml.FullLoader)

        elevator_conf = self.conf["ELEVATOR"]
        self.elevator = Elevator(elevator_conf)
        self.algo = self.GetAlgo(self.conf["ALGORITHM"]["ALGORITHM_CLASS"], elevator_conf)
        self.simulation_events = LoadSimulationEvents(self.conf["SIMULATION"]["SIMULATION_FILE"],
                                                      self.conf["ELEVATOR"]["MAX_FLOOR"])
        self.performance_monitor = PerformanceMonitor()

    def GetAlgo(self, algo_class, elevator_conf):
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

    def _RerunAlgoWithNewPickup(self, current_ts, current_location, sim_event):
        self.algo.ElevatorHeartbeat(current_ts, current_location)
        event_data = self.algo.ConvertEventForRiderRegistration(sim_event["source_floor"],
                                                                sim_event["destination_floor"])
        algo_output_tasks = self.algo.RegisterRiderPickup(sim_event["rider_id"], *event_data)
        self.elevator.RegisterNextTasks(algo_output_tasks)

    def _RerunAlgoWithNewDropoff(self, current_ts, current_location, rider_id, destination_floor):
        self.algo.ElevatorHeartbeat(current_ts, current_location)
        algo_output_tasks = self.algo.RegisterRiderDestination(rider_id, destination_floor)
        self.elevator.RegisterNextTasks(algo_output_tasks)

    def RunSimulation(self):
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
                if self.elevator.IsTaskListEmpty():
                    break

            self.elevator.RunToNextTaskOrMaxTs(max_timestamp=next_event_ts)
            current_ts, current_location = self.elevator.GetStatus()

            # A new rider is being registered
            if current_ts == next_event_ts:
                # Handle all riders registering at the same time
                while next_event_index < len(self.simulation_events) and \
                        self.simulation_events[next_event_index]["timestamp"] == current_ts:

                    sim_event = self.simulation_events[next_event_index]
                    rider_id = sim_event["rider_id"]
                    source_floor = sim_event["source_floor"]
                    destination_floor = sim_event["destination_floor"]

                    self.performance_monitor.RiderRequest(current_ts, rider_id, current_location)
                    self._RerunAlgoWithNewPickup(current_ts,
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
                    self.performance_monitor.RiderPickup(current_ts, rider_id, current_location)
                    self.algo.ReportRiderPickup(current_ts, rider_id)
                    dropoff_floor = rider_id_to_dropoff_location_map[rider_id]
                    active_riders_dropoff_map[rider_id] = dropoff_floor
                    self._RerunAlgoWithNewDropoff(current_ts,
                                                  current_location,
                                                  rider_id,
                                                  dropoff_floor)
                    del active_riders_pickup_map[rider_id]


            # A dropoff point is reached
            if current_location in active_riders_dropoff_map.values():
                dropped_off_rider_ids = \
                    [a for a in active_riders_dropoff_map.keys() if active_riders_dropoff_map[a] == current_location]
                for rider_id in dropped_off_rider_ids:
                    self.performance_monitor.RiderDropoff(current_ts, rider_id, current_location)
                    self.algo.ReportRiderDropoff(current_ts, rider_id)
                    del active_riders_dropoff_map[rider_id]

    def PrintSimulationResults(self):
        self.performance_monitor.PrintEvents()
        self.performance_monitor.PrintPerformanceStats()


if __name__ == "__main__":
    sim_runner = SimulationRunner()
    sim_runner.RunSimulation()
    sim_runner.PrintSimulationResults()