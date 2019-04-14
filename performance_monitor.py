import enum

class EventType(enum.Enum):
    REQUEST = 0
    PICKUP = 1
    DROPOFF = 2

class PerformanceMonitor(object):
    def __init__(self):
        self.rider_to_events_map = {}
        self.events_log = []

    # TODO - potentially add monitoring for elevator movement

    def _AddRiderEvent(self, timestamp, rider_id, event_type, location):
        if rider_id not in self.rider_to_events_map:
            self.rider_to_events_map[rider_id] = []

        self.rider_to_events_map[rider_id].append((event_type, timestamp))
        self.events_log.append("TS: {:>7} ; Floor {:>4} ; {} rider {}".format(timestamp, location, event_type, rider_id))
        print(self.events_log[-1])

    def RiderRequest(self, timestamp, rider_id, current_location):
        self._AddRiderEvent(timestamp, rider_id, EventType.REQUEST, current_location)

    def RiderPickup(self, timestamp, rider_id, location):
        self._AddRiderEvent(timestamp, rider_id, EventType.PICKUP, location)

    def RiderDropoff(self, timestamp, rider_id, location):
        self._AddRiderEvent(timestamp, rider_id, EventType.DROPOFF, location)

    def PrintEvents(self):
        for event in self.events_log:
            print(event)

    #TODO - add some logic that computes states -
    # - total time to complete all tasks
    # - Sum/avg of rider wait times
    # - Sum/avg of rider ride times
    # - Sum/avg of rider time to destination