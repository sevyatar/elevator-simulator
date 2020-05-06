from algo.algo_interface import NaiveElevatorAlgoInterface
from algo.algo_interface import TaskType

import numpy as np
import collections
import pickle

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
    MODEL_PICKLE_FILENAME = "model.pkl"

    class Task(object):
        def __init__(self, rider_id, floor, task_type):
            self.rider_id = rider_id
            self.floor = floor
            self.task_type = task_type

    def __init__(self, elevator_conf, max_floor):
        super().__init__(elevator_conf, max_floor)
        self.tasks = []

        # Q-learning related params
        self.action_space = list(range(1, max_floor+1))
        self.state_space = [max_floor] + \
                           ([MAX_FLOOR_TASKS_TO_COUNT] * max_floor) + \
                           ([MAX_FLOOR_TASKS_TO_COUNT] * max_floor)
        self.q_table = np.random.uniform(low=-2, high=0, size=(self.state_space + [len(self.action_space)]))

        self.previous_state_and_action = None

        # Q-learning exploration params
        self.epsilon = 1
        self.epsilon_decay_value = self.epsilon / (ROUND_TO_END_EPSILON_DECAYING - ROUND_TO_START_EPSILON_DECAYING)

    def _discreet_elevator_location(self):
        '''
        For simplicity, just round the elevator's location to the nearest integer floor
        '''
        return int(round(self.elevator_location))

    def _get_state(self):
        '''
        System state is (l, P1, P2 ... Pn, D1, D2 ... Dn) where:
        l - discreet elevator location
        Pi - number of pending pickups at floor i (1 <= i <= max_floor)
        Di - number of registered dropoffs for floor i (1 <= i <= max_floor)
        '''
        # Note: using collections.Counter to count pickups/dropoffs in each floor, and sorting by floor
        pickups_counter = collections.Counter([t.floor - 1 for t in self.tasks if t.task_type == TaskType.PICKUP])
        dropoffs_counter = collections.Counter([t.floor - 1 for t in self.tasks if t.task_type == TaskType.DROPOFF])

        # Add floors with no tasks to the pickup/dropoff collections
        for floor in range(self.max_floor):
            if floor not in pickups_counter:
                pickups_counter[floor] = 0
            else:
                pickups_counter[floor] = min(pickups_counter[floor], MAX_FLOOR_TASKS_TO_COUNT)

            if floor not in dropoffs_counter:
                dropoffs_counter[floor] = 0
            else:
                dropoffs_counter[floor] = min(dropoffs_counter[floor], MAX_FLOOR_TASKS_TO_COUNT)

        state = [self._discreet_elevator_location() - 1] + list(pickups_counter.values()) + list(dropoffs_counter.values())
        return state

    def _get_next_floor_tasks(self):
        '''
        Actually runs the Q-learning RL process and returns the action (action is the next floor to go to)
        '''
        if not self.tasks:
            return None

        current_state = self._get_state()

        # For the current action - explore or exploit
        if np.random.random() > self.epsilon:
            # Get action from Q table
            current_action = np.argmax(self.q_table[current_state])
        else:
            # Get random action - a random floor out of those floors with a task in them
            # current_action = np.random.choice(self.action_space)
            current_action = np.random.choice(list(set([x.floor for x in self.tasks])))

        # Update the previous state's q value
        if self.previous_state_and_action:
            # TODO - how do I handle reward from previous action?
            reward = -1

            max_current_q = np.max(self.q_table[current_state])
            previous_q = self.q_table[self.previous_state_and_action]
            updated_q = (1 - LEARNING_RATE) * previous_q + LEARNING_RATE * (reward + DISCOUNT * max_current_q)

            # Update Q table with new Q value
            self.q_table[self.previous_state_and_action] = updated_q

        self.previous_state_and_action = current_state + [current_action - 1,]

        # return self.tasks[0].floor if self.tasks else None
        return [current_action]

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

    def _load_model_from_file(self):
        with open(self.MODEL_PICKLE_FILENAME, 'wb') as file:
            self.q_table = pickle.load(file)

    def _save_model_to_file(self):
        with open(self.MODEL_PICKLE_FILENAME, 'wb') as file:
            pickle.dump(self.q_table, file)