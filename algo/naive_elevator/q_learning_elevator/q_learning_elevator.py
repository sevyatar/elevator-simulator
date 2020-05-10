from algo.algo_interface import NaiveElevatorAlgoInterface
from algo.algo_interface import TaskType

import numpy as np
import collections
import pickle

# Since we need to create a discreet and finite state space, we need to cap the max number of tasks per floor we use,
# every number over the cap will be rounded to the cap itself
MAX_FLOOR_TASKS_TO_COUNT = 2

# Q-learning constants
INITIAL_EPSILON = 1
MIN_EPSILON = 0
INITIAL_LEARNING_RATE = 0.8
MIN_LEARNING_RATE = 0.1
DISCOUNT = 0.95

# Q-learning exploration constants
ROUND_TO_START_LEARNING_DECAY = 0
ROUND_TO_END_LEARNING_DECAY = 10000


class QLearningElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The QLearningElevatorAlgo uses Q-learning to decide on the elevator action.

    System state is (l, P1, P2 ... Pn, D1, D2 ... Dn) where:
    l - discreet elevator location
    Pi - number of pending pickups at floor i (1 <= i <= max_floor)
    Di - number of registered dropoffs for floor i (1 <= i <= max_floor)

    System actions are {1, 2 .. max_floor} and denote which floor the elevator is heading to next
    '''
    MODEL_PICKLE_FILENAME = "algo/naive_elevator/q_learning_elevator/model.pkl"

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
                           ([MAX_FLOOR_TASKS_TO_COUNT + 1] * max_floor) + \
                           ([MAX_FLOOR_TASKS_TO_COUNT + 1] * max_floor)
        self.previous_state_and_action = None

        # Params for calculating reward
        self.last_action_ts = None
        self.rider_registration_ts = {}

        try:
            self.load_model_from_file()
        except Exception as e:
            self.reset_model()

    ####################################################################################################
    # The following methods are responsible for maintaining a persistent state between multiple runs (episodes)
    def reset_model(self):
        self.q_table = np.random.uniform(low=-200, high=0, size=(self.state_space + [len(self.action_space)]))
        self.episode = 0
        self.epsilon = INITIAL_EPSILON
        self.learning_rate = INITIAL_LEARNING_RATE

    def load_model_from_file(self):
        with open(self.MODEL_PICKLE_FILENAME, 'rb') as file:
            (self.q_table, self.episode, self.epsilon, self.learning_rate) = pickle.load(file)

        # This is a new episode, so increment the counter
        self.episode += 1

        # If needed, decay epsilon and learning rate
        if ROUND_TO_END_LEARNING_DECAY >= self.episode >= ROUND_TO_START_LEARNING_DECAY:
            count_rounds_to_decay = ROUND_TO_END_LEARNING_DECAY - ROUND_TO_START_LEARNING_DECAY
            self.epsilon = INITIAL_EPSILON + ((MIN_EPSILON - INITIAL_EPSILON) * self.episode / count_rounds_to_decay)
            self.learning_rate = INITIAL_LEARNING_RATE + \
                                 ((MIN_LEARNING_RATE - INITIAL_LEARNING_RATE) * self.episode / count_rounds_to_decay)

    def save_model_to_file(self):
        with open(self.MODEL_PICKLE_FILENAME, 'wb') as file:
            pickle.dump((self.q_table, self.episode, self.epsilon, self.learning_rate), file)

    ####################################################################################################

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
        return tuple(state)

    def _last_action_reward(self):
        '''
        Conceptually, we want to minimize the time between a rider requesting a ride and dropoff,
        so we "punish" the system for every second that a rider hasn't reached his destination
        '''
        rider_registrations = self.rider_registration_ts.values()
        reward = -1 * sum([(self.current_timestamp - x) for x in rider_registrations if x >= self.last_action_ts])
        return reward

    def _get_next_floor_tasks(self):
        '''
        Actually runs the Q-learning RL process and returns the action (action is the next floor to go to)
        '''
        if not self.tasks:
            return []

        current_state = self._get_state()

        # For the current action - explore or exploit
        if np.random.random() > self.epsilon:
            # Get action from Q table
            current_action = np.argmax(self.q_table[current_state])
        else:
            # Get random action - a random floor out of those floors with a task in them
            # Floors are [1..max_floor] while actions are [0..(max_floor-1)], so we substract -1 from the floors
            current_action = np.random.choice(list(set([(x.floor - 1) for x in self.tasks])))

        # Update the previous state's q value, only if some time has passed
        # (implying that the elevator really acted on the previous decision)
        if self.previous_state_and_action and self.last_action_ts != self.current_timestamp:
            reward = self._last_action_reward()

            max_current_q = np.max(self.q_table[current_state])
            previous_q = self.q_table[self.previous_state_and_action]
            updated_q = (1 - self.learning_rate) * previous_q + self.learning_rate * (reward + DISCOUNT * max_current_q)

            # Update Q table with new Q value
            self.q_table[self.previous_state_and_action] = updated_q

        self.previous_state_and_action = current_state + (current_action,)
        self.last_action_ts = self.current_timestamp

        # Floors are [1..max_floor] while actions are [0..(max_floor-1)], so we add +1 to returned value
        next_floor = current_action + 1
        # We add all subsequent floors to make sure all next tasks are passed to the elevator queue
        # (this helps us avoid some weird corner cases)
        subsequent_floors = [t.floor for t in self.tasks if t.floor != next_floor]
        return [next_floor] + subsequent_floors

    def register_rider_source(self, rider_id, source_floor):
        self.tasks.append(QLearningElevatorAlgo.Task(rider_id, source_floor, TaskType.PICKUP))
        self.rider_registration_ts[rider_id] = self.current_timestamp
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
        # Note - I have to calculate next tasks before removing the rider from rider_registration_ts, since
        # we need this entry to accurately calculate reward
        next_tasks = self._get_next_floor_tasks()
        del self.rider_registration_ts[rider_id]
        return next_tasks

    def _load_model_from_file(self):
        with open(self.MODEL_PICKLE_FILENAME, 'wb') as file:
            self.q_table = pickle.load(file)

    def _save_model_to_file(self):
        with open(self.MODEL_PICKLE_FILENAME, 'wb') as file:
            pickle.dump(self.q_table, file)
