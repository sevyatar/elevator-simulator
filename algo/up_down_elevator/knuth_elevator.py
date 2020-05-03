from algo.algo_interface import UpDownElevatorAlgoInterface
from algo.algo_interface import TaskType, UpDown


class KnuthElevatorAlgo(UpDownElevatorAlgoInterface):
    '''
    The KnuthElevatorAlgo follows the following logic:
    1. Continue travelling in the same direction while there are remaining requests in that same direction.
    2. If there are no further requests in that direction,
        then stop and become idle, or change direction if there are requests in the opposite direction.
    '''
    class Task(object):
        def __init__(self, rider_id, floor, task_type, pickup_direction=None):
            self.rider_id = rider_id
            self.floor = floor
            self.task_type = task_type
            self.pickup_direction = pickup_direction

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

    def _get_pickups_for_direction(self, direction, start_from_floor=None):
        all_pickups = [t for t in self.all_tasks if
                       t.task_type == TaskType.PICKUP and
                       (not start_from_floor or
                        (t.floor >= self.elevator_location and direction == UpDown.UP) or
                        (t.floor <= self.elevator_location and direction == UpDown.DOWN)
                        )
                       ]

        sorted_pickups = sorted(all_pickups, key=lambda x: x.floor, reverse=(direction == UpDown.DOWN))
        relevant_pickups = [t for t in sorted_pickups if t.pickup_direction == direction]
        if sorted_pickups and sorted_pickups[-1].pickup_direction != direction:
            relevant_pickups += [sorted_pickups[-1]]

        return relevant_pickups

    def _get_next_tasks(self):
        # If not more tasks - return an empty list
        if not self.all_tasks:
            return []

        # If no more tasks in current direction - change direction
        if not self._remaining_tasks_in_current_direction():
            self._change_direction()

        if self.current_direction == UpDown.UP:
            current_direction_tasks = self._get_pickups_for_direction(UpDown.UP, self.elevator_location) + \
                                      [t for t in self.all_tasks if
                                       t.floor >= self.elevator_location and t.task_type != TaskType.PICKUP]

            remaining_tasks = list(set(self.all_tasks) - set(current_direction_tasks))
            reverse_direction_tasks = self._get_pickups_for_direction(UpDown.DOWN, None) + \
                                      [t for t in remaining_tasks if t.task_type == TaskType.DROPOFF]
        else:
            current_direction_tasks = self._get_pickups_for_direction(UpDown.DOWN, self.elevator_location) + \
                                      [t for t in self.all_tasks if
                                       t.floor <= self.elevator_location and t.task_type != TaskType.PICKUP]

            remaining_tasks = list(set(self.all_tasks) - set(current_direction_tasks))
            reverse_direction_tasks = self._get_pickups_for_direction(UpDown.UP, None) + \
                                      [t for t in remaining_tasks if t.task_type == TaskType.DROPOFF]

        # Return ordered list of tasks in the current direction followed be reverse direction
        return sorted([t.floor for t in current_direction_tasks], reverse=self.current_direction == UpDown.DOWN) + \
               sorted([t.floor for t in reverse_direction_tasks], reverse=self.current_direction == UpDown.UP)

    def register_rider_source(self, rider_id, source_floor, direction):
        self.all_tasks.append(KnuthElevatorAlgo.Task(rider_id, source_floor, TaskType.PICKUP, direction))
        return self._get_next_tasks()

    def register_rider_destination(self, rider_id, destination_floor):
        self.all_tasks.append(KnuthElevatorAlgo.Task(rider_id, destination_floor, TaskType.DROPOFF, None))
        return self._get_next_tasks()

    def report_rider_pickup(self, timestamp, rider_id):
        pickup_task = [a for a in self.all_tasks if a.rider_id == rider_id and a.task_type == TaskType.PICKUP][0]
        self.all_tasks.remove(pickup_task)
        return self._get_next_tasks()

    def report_rider_dropoff(self, timestamp, rider_id):
        pickup_task = [a for a in self.all_tasks if a.rider_id == rider_id and a.task_type == TaskType.DROPOFF][0]
        self.all_tasks.remove(pickup_task)
        return self._get_next_tasks()
