import abc
import enum


class UpDown(enum.Enum):
    UP = 0
    DOWN = 1


class TaskType(enum.Enum):
    PICKUP = 0
    DROPOFF = 1


class BaseAlgoInterface(abc.ABC):
    def __init__(self, elevator_conf, max_floor):
        self.current_timestamp = 0
        self.elevator_location = elevator_conf["INITIAL_FLOOR"]
        self.elevator_conf = elevator_conf
        self.max_floor = max_floor

    @staticmethod
    def get_algo(algo_class, elevator_conf, max_floor):
        '''
        Work some python magic -
        Load the initial module (probably 'algo'), and then recursively import its children until left with the
        relevant class type to instantiate.
        '''
        algo_module = ".".join(algo_class.split(".")[:-1])
        module = __import__(algo_module)
        for attribute in algo_class.split(".")[1:]:
            module = getattr(module, attribute)
        return module(elevator_conf, max_floor)

    def get_algo_name(self):
        module_name_split = self.__module__.split('.')
        algo_name = module_name_split[-2] + '_' + module_name_split[-1]
        return algo_name.replace('_elevator', '')

    @abc.abstractmethod
    def convert_event_for_rider_registration(self, source_floor, destination_floor):
        '''
        Used to convert the event data from the basic format, to the format that this specific algo accepts
        '''
        pass

    @abc.abstractmethod
    def register_rider_destination(self, rider_id, destination_floor):
        '''
        Used to register a rider's destination, for algorithms where the rider inputs his destination floor
        only upon entering the elevator
        '''
        pass

    def elevator_heartbeat(self, timestamp, elevator_location):
        '''
        Used by the elevator to report its location+time to the algo
        '''
        self.current_timestamp = timestamp
        self.elevator_location = elevator_location

    def report_rider_pickup(self, timestamp, rider_id):
        '''
        Signal the algo that a rider pickup took place
        '''
        pass

    def report_rider_dropoff(self, timestamp, rider_id):
        '''
        Signal the algo that a rider dropoff took place
        '''


class NaiveElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def register_rider_source(self, rider_id, source_floor):
        pass

    def convert_event_for_rider_registration(self, source_floor, destination_floor):
        '''
        Simple algo receives only the source floor when a rider requests a ride
        '''
        return [source_floor]


class UpDownElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def register_rider_source(self, rider_id, source_floor, direction: UpDown):
        pass

    def convert_event_for_rider_registration(self, source_floor, destination_floor):
        '''
        Up-Down algo receives the source floor and an indication if the destination is located above or below it
        '''
        direction = UpDown.UP if destination_floor >= source_floor else UpDown.DOWN
        return [source_floor, direction]


class DestinationFirstElevatorAlgoInterface(BaseAlgoInterface):
    @abc.abstractmethod
    def register_rider_source(self, rider_id, source_floor, destination_floor):
        pass

    def convert_event_for_rider_registration(self, source_floor, destination_floor):
        '''
        Destination-first algo receives both the source and the destination floors immediately
        '''
        return [source_floor, destination_floor]
