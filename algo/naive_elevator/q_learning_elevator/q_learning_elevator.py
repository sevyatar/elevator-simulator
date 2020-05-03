from algo.algo_interface import NaiveElevatorAlgoInterface
from algo.algo_interface import TaskType

import numpy as np
import collections

# Since we need to create a discreet and finite state space, we need to cap the max number of tasks per floor we use,
# every number over the cap will be rounded to the cap itself
MAX_FLOOR_TASKS_TO_COUNT = 3

# Q-learning constants
LEARNING_RATE = 0.1
DISCOUNT = 0.95

# Q-learning exploration constants
ROUND_TO_START_EPSILON_DECAYING = 1
ROUND_TO_END_EPSILON_DECAYING = 10000


class QLearningElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The QLearningElevatorAlgo uses Q-learning to decide on the elevator action.

    System state is (l, P1, P2 ... Pn, D1, D2 ... Dn) where:
    l - discreet elevator location
    Pi - number of pending pickups at floor i (1 <= i <= max_floor)
    Di - number of registered dropoffs for floor i (1 <= i <= max_floor)

    System actions are {1, 2 .. max_floor} and denote which floor the elevator is heading to next
    '''
    class Task(object):
        def __init__(self, rider_id, floor, task_type):
            self.rider_id = rider_id
            self.floor = floor
            self.task_type = task_type

    def __init__(self, elevator_conf, max_floor):
        super().__init__(elevator_conf, max_floor)
        self.tasks = []

        # Q-learning related params
        self.action_space = list(range(1, max_floor))
        self.state_space = [max_floor, max_floor * MAX_FLOOR_TASKS_TO_COUNT, max_floor * MAX_FLOOR_TASKS_TO_COUNT]
        self.q_table = np.random.uniform(low=-2, high=0, size=(self.state_space + [len(self.action_space)]))

        # Q-learning exploration params
        self.epsilon = 1
        self.epsilon_decay_value = self.epsilon / (ROUND_TO_END_EPSILON_DECAYING - ROUND_TO_START_EPSILON_DECAYING)

    def _discreet_elevator_location(self):
        '''
        For simplicity, just round the elevator's location to the nearest integer floor
        '''
        return round(self.elevator_location)

    def _get_state(self):
        '''
        System state is (l, P1, P2 ... Pn, D1, D2 ... Dn) where:
        l - discreet elevator location
        Pi - number of pending pickups at floor i (1 <= i <= max_floor)
        Di - number of registered dropoffs for floor i (1 <= i <= max_floor)
        '''
        # Note: using collections.Counter to count pickups/dropoffs in each floor, and sorting by floor
        pickups_counter = collections.Counter([t.floor for t in self.tasks if t.task_type == TaskType.PICKUP])
        dropoffs_counter = collections.Counter([t.floor for t in self.tasks if t.task_type == TaskType.DROPOFF])

        return [self._discreet_elevator_location()] + list(pickups_counter.values()) + list(dropoffs_counter.values())

    def _get_next_floor_tasks(self):
        '''
        Actually runs the RL process and returns the action (and action is the next floor to go to)
        '''
        # TODO - implement
        # return self.tasks[0].floor if self.tasks else None
        return [task.floor for task in self.tasks]

    def register_rider_source(self, rider_id, source_floor):
        self.tasks.append(QLearningElevatorAlgo.Task(rider_id, source_floor, TaskType.PICKUP))
        return self._get_next_floor_tasks()

    def register_rider_destination(self, rider_id, destination_floor):
        self.tasks.append(QLearningElevatorAlgo.Task(rider_id, destination_floor, TaskType.DROPOFF))
        return self._get_next_floor_tasks()

    def report_rider_pickup(self, timestamp, rider_id):
        pickup_task = [a for a in self.tasks if a.rider_id == rider_id and a.task_type == TaskType.PICKUP][0]
        self.tasks.remove(pickup_task)
        return self._get_next_floor_tasks()

    def report_rider_dropoff(self, timestamp, rider_id):
        pickup_task = [a for a in self.tasks if a.rider_id == rider_id and a.task_type == TaskType.DROPOFF][0]
        self.tasks.remove(pickup_task)
        return self._get_next_floor_tasks()
