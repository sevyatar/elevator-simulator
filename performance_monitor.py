import enum

class EventType(enum.Enum):
    REQUEST = 0
    PICKUP = 1
    DROPOFF = 2

class PerformanceMonitor(object):
    def __init__(self):
        self.rider_to_events_map = {}
        self.events_log = []

    class Event(object):
        def __init__(self, rider_id, event_type, timestamp, location):
            self.rider_id = rider_id
            self.event_type = event_type
            self.timestamp = timestamp
            self.location = location

    # TODO - potentially add monitoring for elevator movement

    def _AddRiderEvent(self, timestamp, rider_id, event_type, location):
        if rider_id not in self.rider_to_events_map:
            self.rider_to_events_map[rider_id] = []

        event = PerformanceMonitor.Event(rider_id, event_type, timestamp, location)
        self.rider_to_events_map[rider_id].append(event)
        self.events_log.append(event)

    def RiderRequest(self, timestamp, rider_id, current_location):
        self._AddRiderEvent(timestamp, rider_id, EventType.REQUEST, current_location)

    def RiderPickup(self, timestamp, rider_id, location):
        self._AddRiderEvent(timestamp, rider_id, EventType.PICKUP, location)

    def RiderDropoff(self, timestamp, rider_id, location):
        self._AddRiderEvent(timestamp, rider_id, EventType.DROPOFF, location)

    def PrintEvents(self):
        for e in self.events_log:
            print("TS: {:>7} ; Floor {:>4} ; {} rider {}".format(e.timestamp, e.location, e.event_type, e.rider_id))

    def PrintPerformanceStats(self):
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
