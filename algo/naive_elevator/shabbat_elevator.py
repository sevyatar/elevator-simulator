from algo.algo_interface import NaiveElevatorAlgoInterface

class ShabbatElevatorAlgo(NaiveElevatorAlgoInterface):
    '''
    The ShabbatElevatorAlgo stops on every floor, both on the way up and on the way down
    '''

    def _CreateTaskRounds(self, rounds):
        upward = list(range(2, self.elevator_conf["MAX_FLOOR"] + 1))
        downward = list(range(self.elevator_conf["MAX_FLOOR"] - 1, 0, -1))
        return (upward + downward) * rounds

    def __init__(self, elevator_conf):
        super().__init__(elevator_conf)
        self.tasks = self._CreateTaskRounds(100)

    def _EnsureEnoughTasksInQueue(self):
        if len(self.tasks) < 10:
            self.tasks += self._CreateTaskRounds(100)

    def ConvertEventForRiderRegistration(self, *args):
        '''
        Shabbat elevator doesn't care about the user input...
        '''
        return []

    def RegisterRiderPickup(self, *args):
        self._EnsureEnoughTasksInQueue()
        return self.tasks

    def RegisterRiderDestination(self, *args):
        self._EnsureEnoughTasksInQueue()
        return self.tasks

    def ReportRiderPickup(self, *args):
        pass

    def ReportRiderDropoff(self, *args):
        pass
