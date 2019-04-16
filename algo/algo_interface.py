import abc
import enum

class UpDown(enum.Enum):
    UP = 0
    DOWN = 1

class TaskType(enum.Enum):
    PICKUP = 0
    DROPOFF = 1


class BaseAlgoInterface(abc.ABC):
    def __init__(self, elevator_conf):
        self.current_timestamp = None
        self.elevator_location = None
        self.elevator_conf = elevator_conf

    @abc.abstractmethod
    def ConvertEventForRiderRegistration(self, source_floor, destination_floor):
        '''
        Used to convert the event data from the basic format, to the format that this specific algo accepts
        '''
        pass

    @abc.abstractmethod
    def RegisterRiderDestination(self, rider_id, destination_floor):
        '''
        Used to register a rider's destination, for algorithms where the rider inputs his destination floor
        only upon entering the elevator
        '''
        pass

    def ElevatorHeartbeat(self, timestamp, elevator_location):
        self.current_timestamp = timestamp
        self.elevator_location = elevator_location

    def ReportRiderPickup(self, timestamp, rider_id):
        pass

    def ReportRiderDropoff(self, timestamp, rider_id):
        pass

class NaiveElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def RegisterRiderPickup(self, rider_id, source_floor):
        pass

    def ConvertEventForRiderRegistration(self, source_floor, destination_floor):
        '''
        Simple algo receives only the source floor when a rider requests a ride
        '''
        return [source_floor]

class UpDownElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def RegisterRiderPickup(self, rider_id, source_floor, direction: UpDown):
        pass

    def ConvertEventForRiderRegistration(self, source_floor, destination_floor):
        '''
        Up-Down algo receives the source floor and an indication if the destination is located above or below it
        '''
        direction = UpDown.UP if destination_floor >= source_floor else UpDown.DOWN
        return [source_floor, direction]

class DestinationFirstElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def RegisterRiderPickup(self, rider_id, source_floor, destination_floor):
        pass

    def ConvertEventForRiderRegistration(self, source_floor, destination_floor):
        '''
        Destination-first algo receives both the source and the destination floors immediately
        '''
        return [source_floor, destination_floor]