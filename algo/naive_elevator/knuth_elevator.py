from algo.algo_interface import NaiveElevatorAlgoInterface
from algo.algo_interface import TaskType, UpDown


class KnuthElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The KnuthElevatorAlgo follows the following logic:
    1. Continue travelling in the same direction while there are remaining requests in that same direction.
    2. If there are no further requests in that direction,
        then stop and become idle, or change direction if there are requests in the opposite direction.
    '''
    class Task(object):
        def __init__(self, rider_id, floor, task_type):
            self.rider_id = rider_id
            self.floor = floor
            self.task_type = task_type

    def __init__(self, elevator_conf, max_floor):
        super().__init__(elevator_conf, max_floor)
        self.all_tasks = []
        # Arbitrarily set initial direction as "UP" if the elevator location is not the top floor
        self.current_direction = UpDown.UP if self.elevator_location < self.max_floor else UpDown.DOWN

    def _remaining_tasks_in_current_direction(self):
        if (self.current_direction == UpDown.UP and [a for a in self.all_tasks if a.floor >= self.elevator_location]) \
                or \
                (self.current_direction == UpDown.DOWN and [a for a in self.all_tasks if a.floor <= self.elevator_location]):
            return True
        else:
            return False

    def _change_direction(self):
        if self.current_direction == UpDown.UP:
            self.current_direction = UpDown.DOWN
        else:
            self.current_direction = UpDown.UP

    def _get_next_tasks(self):
        # If not more tasks - return an empty list
        if not self.all_tasks:
            return []

        # If no more tasks in current direction - change direction
        if not self._remaining_tasks_in_current_direction():
            self._change_direction()

        # Return ordered list of tasks in the current direction followed be reverse direction
        if self.current_direction == UpDown.UP:
            current_direction_tasks = sorted([t.floor for t in self.all_tasks if t.floor >= self.elevator_location],
                                             reverse=False)
            reverse_direction_tasks = sorted([t.floor for t in self.all_tasks if t.floor < self.elevator_location],
                                             reverse=True)
        else:
            current_direction_tasks = sorted([t.floor for t in self.all_tasks if t.floor <= self.elevator_location],
                                             reverse=True)
            reverse_direction_tasks = sorted([t.floor for t in self.all_tasks if t.floor > self.elevator_location],
                                             reverse=False)

        next_tasks = current_direction_tasks + reverse_direction_tasks
        return next_tasks

    def register_rider_pickup(self, rider_id, source_floor):
        self.all_tasks.append(KnuthElevatorAlgo.Task(rider_id, source_floor, TaskType.PICKUP))
        return self._get_next_tasks()

    def register_rider_destination(self, rider_id, destination_floor):
        self.all_tasks.append(KnuthElevatorAlgo.Task(rider_id, destination_floor, TaskType.DROPOFF))
        return self._get_next_tasks()

    def report_rider_pickup(self, timestamp, rider_id):
        pickup_task = [a for a in self.all_tasks if a.rider_id == rider_id and a.task_type == TaskType.PICKUP][0]
        self.all_tasks.remove(pickup_task)

    def report_rider_dropoff(self, timestamp, rider_id):
        pickup_task = [a for a in self.all_tasks if a.rider_id == rider_id and a.task_type == TaskType.DROPOFF][0]
        self.all_tasks.remove(pickup_task)
