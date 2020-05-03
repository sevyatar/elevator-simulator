from algo.algo_interface import NaiveElevatorAlgoInterface
from algo.algo_interface import TaskType


class FIFOElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The FIFOElevatorAlgo always handles tasks in the order in which they registered into the system, no matter
    the elevator will just go past another potential task.
    '''
    class Task(object):
        def __init__(self, rider_id, floor, task_type):
            self.rider_id = rider_id
            self.floor = floor
            self.task_type = task_type

    def __init__(self, elevator_conf, max_floor):
        super().__init__(elevator_conf, max_floor)
        self.tasks = []

    def register_rider_source(self, rider_id, source_floor):
        self.tasks.append(FIFOElevatorAlgo.Task(rider_id, source_floor, TaskType.PICKUP))
        return [task.floor for task in self.tasks]

    def register_rider_destination(self, rider_id, destination_floor):
        self.tasks.append(FIFOElevatorAlgo.Task(rider_id, destination_floor, TaskType.DROPOFF))
        return [task.floor for task in self.tasks]

    def report_rider_pickup(self, timestamp, rider_id):
        pickup_task = [a for a in self.tasks if a.rider_id == rider_id and a.task_type == TaskType.PICKUP][0]
        self.tasks.remove(pickup_task)
        return [task.floor for task in self.tasks]

    def report_rider_dropoff(self, timestamp, rider_id):
        pickup_task = [a for a in self.tasks if a.rider_id == rider_id and a.task_type == TaskType.DROPOFF][0]
        self.tasks.remove(pickup_task)
        return [task.floor for task in self.tasks]
