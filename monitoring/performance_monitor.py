import enum
import json


class EventType(enum.Enum):
    REQUEST = 0
    PICKUP = 1
    DROPOFF = 2


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

    def write_visualization_data_file(self):
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
            text = json.dumps(data, indent=2)
            text = "data = " + text
            outfile.write(text)

    def print_performance_stats(self):
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

        print("Time to complete all tasks - {}".format(self.events_log[-1].timestamp))
        print("Wait time - total: {:>7} avg: {}".format(sum(wait_times), sum(wait_times) / len(wait_times)))
        print("Ride time - total: {:>7} avg: {}".format(sum(ride_times), sum(ride_times) / len(ride_times)))
        print("Rider time to destination - total: {:>7} avg: {}".format(sum(times_to_destination), sum(times_to_destination) / len(times_to_destination)))

