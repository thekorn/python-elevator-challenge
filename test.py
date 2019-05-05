import unittest
import contextlib
from io import StringIO

from elevator import Elevator
from elevator_logic import ElevatorLogic, UP, DOWN, FLOOR_COUNT


class TestElevator(unittest.TestCase):

    def test_init(self):
        """should start on floor 1"""
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            e = Elevator(ElevatorLogic())
            e.call(5, DOWN)
            e.run_until_stopped()
        output = temp_stdout.getvalue().strip()
        self.assertEqual(output, '1...')

        #with contextlib.redirect_stderr(temp_stdout):
            




if __name__ == '__main__':
    unittest.main()