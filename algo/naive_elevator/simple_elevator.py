from algo.algo_interface import NaiveElevatorAlgoInterface
from algo.algo_interface import TaskType

class SimpleElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The SimpleElevatorAlgo always handles tasks in the order in which they registered into the system, no matter
    the elevator will just go past another potential task.
    '''
    class Task(object):
        def __init__(self, rider_id, floor, task_type):
            self.rider_id = rider_id
            self.floor = floor
            self.task_type = task_type

    def __init__(self):
        self.tasks = []

    def RegisterRiderPickup(self, rider_id, source_floor):
        self.tasks.append(SimpleElevatorAlgo.Task(rider_id, source_floor, TaskType.PICKUP))
        return [task.floor for task in self.tasks]

    def RegisterRiderDestination(self, rider_id, destination_floor):
        '''
        Used to register a rider's destination, for algorithms where the rider inputs his destination floor
        only upon entering the elevator
        '''
        self.tasks.append(SimpleElevatorAlgo.Task(rider_id, destination_floor, TaskType.DROPOFF))
        return [task.floor for task in self.tasks]

    def ReportRiderPickup(self, timestamp, rider_id):
        pickup_task = [a for a in self.tasks if a.rider_id == rider_id and a.task_type == TaskType.PICKUP][0]
        self.tasks.remove(pickup_task)

    def ReportRiderDropoff(self, timestamp, rider_id):
        pickup_task = [a for a in self.tasks if a.rider_id == rider_id and a.task_type == TaskType.DROPOFF][0]
        self.tasks.remove(pickup_task)
