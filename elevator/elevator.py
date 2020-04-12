import copy
import math


class Elevator(object):
    '''
    This class simulates an elevator. Generally, for any single point in time the elevator has a length>=0 list of tasks,
    where a 'task' is a floor to be reached and then open and close the doors. Each task can be either a pickup, dropoff
    of a 'wait' task.
    '''
    class Task(object):
        def __init__(self, floor, task_type):
            self.floor = floor
            self.task_type = task_type

    def __init__(self, conf):
        self.current_location = conf["INITIAL_FLOOR"]
        self.time_to_ascend_one_floor = conf["TIME_TO_GO_UP_ONE_FLOOR"]
        self.time_to_descend_one_floor = conf["TIME_TO_GO_DOWN_ONE_FLOOR"]
        self.time_to_open_doors = conf["TIME_TO_OPEN_DOORS"]
        self.time_to_close_doors = conf["TIME_TO_CLOSE_DOORS"]

        self.task_list = []
        self.current_ts = 0
        self.doors_open = False
        self.ts_to_arrival_floor_log = {self.current_ts : conf["INITIAL_FLOOR"]}

    def register_next_tasks(self, tasks):
        self.task_list = copy.copy(tasks)

    def get_status(self):
        return self.current_ts, self.current_location

    def is_task_list_empty(self):
        return self.task_list == []

    def get_ts_to_arrival_floor_log(self):
        return self.ts_to_arrival_floor_log

    def _move_elevator(self, new_location, new_ts, time_to_move_one_floor):
        '''
        Used for 2 things:
            - Changing elevator value to indicate new location and current TS
            - Log all the floors that the elevator visited/passed through
        '''
        # Elevator going up
        if new_location > self.current_location:
            all_floors = list(range(math.ceil(self.current_location), math.floor(new_location)))
        # Elevator going down
        else:
            all_floors = list(range(math.floor(self.current_location), math.ceil(new_location), -1))

        for floor in all_floors:
            arrival_ts = self.current_ts + (abs(floor - self.current_location) * time_to_move_one_floor)
            self.ts_to_arrival_floor_log[arrival_ts] = floor

        self.current_location = new_location
        self.current_ts = new_ts

    def run_to_next_task_or_max_ts(self, max_timestamp):
        '''
        Lets the elevator run until it hits its next task, or until a timestamp is reached
        If max_timestamp in None, assume we can always reach the next task
        '''
        # If no more tasks, advance time and return
        if not self.task_list:
            self.current_ts = max_timestamp
            return

        # TODO - currently, the elevator can change direction immediately at any time, should I allow it?

        # If doors are currently open, the elevator must close them before moving again
        if self.doors_open:
            self.current_ts += self.time_to_close_doors
            self.doors_open = False
            # In case we went over max_timestamp by waiting for the doors to close, return without moving
            # (for simplicity - round "current_ts" to be the same as "max_timestamp", although it's less accurate)
            if max_timestamp is not None and (self.current_ts > max_timestamp):
                self.current_ts = max_timestamp
                return

        floor_difference_to_next_task = (self.task_list[0] - self.current_location)
        time_to_move_one_floor = self.time_to_ascend_one_floor \
            if floor_difference_to_next_task >= 0 \
            else self.time_to_descend_one_floor
        time_to_next_task = time_to_move_one_floor * abs(floor_difference_to_next_task)

        # If the elevator CAN reach the next task in time
        if max_timestamp is None or (self.current_ts + time_to_next_task <= max_timestamp):
            self._move_elevator(new_location=self.task_list[0],
                                new_ts=self.current_ts + time_to_next_task + self.time_to_open_doors,
                                time_to_move_one_floor=time_to_move_one_floor)
            self.doors_open = True
            del self.task_list[0]
        # If the elevator CAN'T reach the next task in time
        else:
            new_location = self.current_location + ((1 if floor_difference_to_next_task > 0 else -1) *
                                                    (max_timestamp - self.current_ts) / time_to_move_one_floor)
            self._move_elevator(new_location=new_location, new_ts=max_timestamp,
                                time_to_move_one_floor=time_to_move_one_floor)


