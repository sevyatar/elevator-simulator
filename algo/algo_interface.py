import abc
import enum

class UpDown(enum.Enum):
    UP = 0
    DOWN = 1

class NaiveElevatorAlgoInterface(abc.ABC):
    @abc.abstractmethod
    def RegisterRider(self, timestamp, source_floor):
        pass

class UpDownElevatorAlgoInterface(abc.ABC):
    @abc.abstractmethod
    def RegisterRider(self, timestamp, source_floor, direction: UpDown):
        pass

class DestinationFirstElevatorAlgoInterface(abc.ABC):
    @abc.abstractmethod
    def RegisterRider(self, timestamp, source_floor, destination_floor):
        pass