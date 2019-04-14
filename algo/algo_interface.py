import abc
import enum

class UpDown(enum.Enum):
    UP = 0
    DOWN = 1

class TaskType(enum.Enum):
    PICKUP = 0
    DROPOFF = 1


class BaseAlgoInterface(abc.ABC):
    def __init__(self):
        self.current_timestamp = None
        self.elevator_location = None

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

class UpDownElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def RegisterRiderPickup(self, rider_id, source_floor, direction: UpDown):
        pass

class DestinationFirstElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def RegisterRiderPickup(self, rider_id, source_floor, destination_floor):
        pass