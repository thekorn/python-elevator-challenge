import unittest
import logging
import os

from elevator import Elevator
from elevator_logic import ElevatorLogic, UP, DOWN, FLOOR_COUNT


class TestElevator(unittest.TestCase):

    def test_basic(self):
        """should start on floor 1"""
        e = Elevator(ElevatorLogic())
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(1)
        e.call(3, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3, 2, 1])

    def test_directionality(self):
        e = Elevator(ElevatorLogic())
        e.call(2, DOWN)
        e.select_floor(5)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3, 2])

    def test_directionality_ignored(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(3)
        e.select_floor(5)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3])
        e.select_floor(2)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(2)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3, 2])

    def test_changing_directions(self):
        e = Elevator(ElevatorLogic())
        e.call(2, DOWN)
        e.call(4, UP)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4])
        e.select_floor(5)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3, 2])

    def test_changing_directions_no_furtherup(self):
        e = Elevator(ElevatorLogic())
        e.call(2, DOWN)
        e.call(4, UP)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 3, 2])

    @unittest.skip("demonstrating skipping")
    def test_changing_both_directions(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(5)
        e.call(5, UP)
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        e.select_floor(4)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 6])

    def test_en_passant(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(6)
        e.run_until_floor(2)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2])
        e.select_floor(3)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3])
        e.run_until_floor(4)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4])
        e.call(5, UP)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 6])

    def test_en_passant_wrong_direction(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(5)
        e.run_until_floor(2)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2])
        e.call(2, UP)
        e.step()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3])
        e.select_floor(3)  # missed the boat, ignored
        e.step()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3, 2])



if __name__ == '__main__':
    if os.environ.get("VERBOSE"):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()