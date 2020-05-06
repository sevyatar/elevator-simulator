import enum
import json
import statistics
import numpy as np


class EventType(enum.Enum):
    REQUEST = 0
    PICKUP = 1
    DROPOFF = 2
    FLOOR_PASSED = 3


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


class PerformanceMonitor(object):
    def __init__(self, floor_count):
        self.rider_to_events_map = {}
        self.events_log = []
        self.floor_count = floor_count

    class Event(object):
        def __init__(self, rider_id, event_type, timestamp, event_location, elevator_location):
            self.rider_id = rider_id
            self.event_type = event_type
            self.timestamp = timestamp
            self.event_location = event_location
            self.elevator_location = elevator_location

    def _sort_events(self):
        self.events_log = sorted(self.events_log, key=lambda x: x.timestamp)

    def _add_rider_event(self, timestamp, rider_id, event_type, event_location, elevator_location):
        if rider_id not in self.rider_to_events_map:
            self.rider_to_events_map[rider_id] = []

        event = PerformanceMonitor.Event(rider_id, event_type, timestamp, event_location, elevator_location)
        self.rider_to_events_map[rider_id].append(event)
        self.events_log.append(event)

    def rider_request(self, timestamp, rider_id, pickup_location, dropoff_location, elevator_location):
        self._add_rider_event(timestamp, rider_id, EventType.REQUEST, pickup_location, elevator_location)

    def rider_pickup(self, timestamp, rider_id, location):
        self._add_rider_event(timestamp, rider_id, EventType.PICKUP, location, location)

    def rider_dropoff(self, timestamp, rider_id, location):
        self._add_rider_event(timestamp, rider_id, EventType.DROPOFF, location, location)

    def floors_visited(self, ts_to_floor_mapping):
        for ts, floor in ts_to_floor_mapping.items():
            event = PerformanceMonitor.Event(rider_id=None,
                                             event_type=EventType.FLOOR_PASSED,
                                             timestamp=ts,
                                             event_location=floor,
                                             elevator_location=floor)
            self.events_log.append(event)

    def write_visualization_data_file(self):
        self._sort_events()
        data = dict(floors=self.floor_count, initial_floor=1, events=[])

        for e in self.events_log:
            print("TS: {:>7} ; Elevator Floor: {:>4} Event Floor {} ; {} rider {}".format(e.timestamp,
                                                                                          e.elevator_location,
                                                                                          e.event_location,
                                                                                          e.event_type,
                                                                                          e.rider_id))
            data["events"].append(dict(ts=e.timestamp, event_floor=e.event_location, elevator_floor=e.elevator_location,
                                       event_type=e.event_type.name, rider=e.rider_id))

        with open('monitoring/visualize/data.js', 'w') as outfile:
            # UGLINESS AHEAD - I need to put the json data in a .js file, so I do some string modification
            text = json.dumps(data, cls=NpEncoder, indent=2)
            text = "data = " + text
            outfile.write(text)

    def calculate_performace_stats(self):
        wait_times = []
        ride_times = []
        times_to_destination = []
        for rider_id, events in self.rider_to_events_map.items():
            request = [a for a in events if a.event_type == EventType.REQUEST][0]
            pickup = [a for a in events if a.event_type == EventType.PICKUP][0]
            dropoff = [a for a in events if a.event_type == EventType.DROPOFF][0]

            wait_times.append(pickup.timestamp - request.timestamp)
            ride_times.append(dropoff.timestamp - pickup.timestamp)
            times_to_destination.append(dropoff.timestamp - request.timestamp)

        time_to_complete_all_tasks = self.events_log[-1].timestamp

        total_wait_time = sum(wait_times)
        mean_wait_time = statistics.mean(wait_times)
        median_wait_time = statistics.median(wait_times)

        total_ride_time = sum(ride_times)
        mean_ride_time = statistics.mean(ride_times)
        median_ride_time = statistics.median(ride_times)

        total_time_to_destination = sum(times_to_destination)
        mean_time_to_destination = statistics.mean(times_to_destination)
        median_time_to_destination = statistics.median(times_to_destination)

        return dict(
            time_to_complete_all_tasks=time_to_complete_all_tasks,
            total_wait_time=total_wait_time,
            mean_wait_time=mean_wait_time,
            median_wait_time=median_wait_time,
            total_ride_time=total_ride_time,
            mean_ride_time=mean_ride_time,
            median_ride_time=median_ride_time,
            total_time_to_destination=total_time_to_destination,
            mean_time_to_destination=mean_time_to_destination,
            median_time_to_destination=median_time_to_destination
        )

    def print_performance_stats(self):
        stats_dict = self.calculate_performace_stats()

        print("Time to complete all tasks - {}".format(stats_dict["time_to_complete_all_tasks"]))
        print("Wait time - total: {:>7} avg: {}".format(stats_dict["total_wait_time"], stats_dict["mean_wait_time"]))
        print("Ride time - total: {:>7} avg: {}".format(stats_dict["total_ride_time"], stats_dict["mean_ride_time"]))
        print("Rider time to destination - total: {:>7} avg: {}".format(stats_dict["total_time_to_destination"],
                                                                        stats_dict["mean_time_to_destination"]))

