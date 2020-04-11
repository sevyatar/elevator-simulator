from algo.algo_interface import NaiveElevatorAlgoInterface


class ShabbatElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The ShabbatElevatorAlgo stops on every floor, both on the way up and on the way down
    '''

    def _create_task_rounds(self, rounds):
        upward = list(range(2, self.max_floor + 1))
        downward = list(range(self.max_floor - 1, 0, -1))
        return (upward + downward) * rounds

    def __init__(self, elevator_conf, max_floor):
        super().__init__(elevator_conf, max_floor)
        self.tasks = [1] + self._create_task_rounds(100)

    def _ensure_enough_tasks_in_queue(self):
        if len(self.tasks) < 10:
            self.tasks += self._create_task_rounds(100)

    def convert_event_for_rider_registration(self, *args):
        '''
        Shabbat elevator doesn't care about the user input...
        '''
        return []

    def register_rider_pickup(self, *args):
        self._ensure_enough_tasks_in_queue()
        return self.tasks

    def register_rider_destination(self, *args):
        self._ensure_enough_tasks_in_queue()
        return self.tasks

    def report_rider_pickup(self, *args):
        pass

    def report_rider_dropoff(self, *args):
        pass
