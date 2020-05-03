import unittest
import random
from collections import defaultdict
from elevator import Elevator


class ElevatorTest(unittest.TestCase):
    @staticmethod
    def _get_default_conf():
        return {
            "INITIAL_FLOOR": 1,
            "TIME_TO_GO_UP_ONE_FLOOR": 3,
            "TIME_TO_GO_DOWN_ONE_FLOOR": 4,
            "TIME_TO_OPEN_DOORS": 5,
            "TIME_TO_CLOSE_DOORS": 6
        }

    def test_init(self):
        conf = defaultdict(lambda: 0)
        initial_floor = random.randint(1, 100000)
        conf["INITIAL_FLOOR"] = initial_floor
        elevator = Elevator(conf)
        current_ts, current_location = elevator.get_status()
        self.assertEqual(current_ts, 0)
        self.assertEqual(current_location, initial_floor)

    def test_RunToNextTaskOrMaxTs_basic(self):
        conf = self._get_default_conf()
        elevator = Elevator(conf)
        next_tasks = [conf["INITIAL_FLOOR"] + 1,
                      conf["INITIAL_FLOOR"] + 2,
                      conf["INITIAL_FLOOR"] + 4,
                      conf["INITIAL_FLOOR"] + 3]
        elevator.register_next_tasks(next_tasks)

        elevator.run_to_next_task_or_max_ts(None)
        ts1, location1 = elevator.get_status()
        self.assertEqual(ts1, conf["TIME_TO_GO_UP_ONE_FLOOR"] + conf["TIME_TO_OPEN_DOORS"])
        self.assertEqual(location1, next_tasks[0])

        elevator.run_to_next_task_or_max_ts(None)
        ts2, location2 = elevator.get_status()
        self.assertEqual(ts2, ts1 +
                         conf["TIME_TO_GO_UP_ONE_FLOOR"] +
                         conf["TIME_TO_CLOSE_DOORS"] +
                         conf["TIME_TO_OPEN_DOORS"])
        self.assertEqual(location2, next_tasks[1])

        elevator.run_to_next_task_or_max_ts(None)
        ts3, location3 = elevator.get_status()
        self.assertEqual(ts3, ts2 + (2*conf["TIME_TO_GO_UP_ONE_FLOOR"]) + conf["TIME_TO_CLOSE_DOORS"] + conf[
            "TIME_TO_OPEN_DOORS"])
        self.assertEqual(location3, next_tasks[2])

        elevator.run_to_next_task_or_max_ts(None)
        ts4, location4 = elevator.get_status()
        self.assertEqual(ts4, ts3 + conf["TIME_TO_GO_DOWN_ONE_FLOOR"] + conf["TIME_TO_CLOSE_DOORS"] + conf[
            "TIME_TO_OPEN_DOORS"])
        self.assertEqual(location4, next_tasks[3])

    def test_RunToNextTaskOrMaxTs_cant_make_next_task(self):
        conf = self._get_default_conf()
        elevator = Elevator(conf)
        next_tasks = [conf["INITIAL_FLOOR"] + 1]
        elevator.register_next_tasks(next_tasks)

        max_ts_1 = float(conf["TIME_TO_GO_UP_ONE_FLOOR"]) / 2
        elevator.run_to_next_task_or_max_ts(max_ts_1)
        ts1, location1 = elevator.get_status()
        self.assertEqual(ts1, max_ts_1)
        self.assertEqual(location1, conf["INITIAL_FLOOR"] + 0.5)

        # Now the elevator can reach the next task (and open doors)
        max_ts_2 = conf["TIME_TO_GO_UP_ONE_FLOOR"] + conf["TIME_TO_OPEN_DOORS"]
        elevator.run_to_next_task_or_max_ts(max_ts_2)
        ts2, location2 = elevator.get_status()
        self.assertEqual(ts2, max_ts_2)
        self.assertEqual(location2, next_tasks[0])


if __name__ == '__main__':
    unittest.main()
