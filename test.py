import unittest
import logging
import os
import random

from elevator import Elevator
from elevator_logic import ElevatorLogic, UP, DOWN, FLOOR_COUNT


class TestElevator(unittest.TestCase):
    """ unittest versions of the doc tests
     
        having the as unittests is helpful for debugging
        for documentation on the logic behind each tests
        look at `README.md`
    """

    def test_basic(self):
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

    def test_changing_both_directions(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(5)
        e.call(5, UP)
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(4) # ignored
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6) # ignored
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6)
        e.run_until_stopped()
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
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])

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

    #@unittest.skip("demonstrating skipping")
    def test_random_requests(self):
        # just make sure that a random sequence newer crashes
        e = Elevator(ElevatorLogic())
        for i in range(1000):  
            r = random.randrange(6)
            if r == 0: e.call(
                random.randrange(FLOOR_COUNT) + 1,
                random.choice((UP, DOWN)))
            elif r == 1: e.select_floor(random.randrange(FLOOR_COUNT) + 1)
            else: e.step()

    def test_called_while_moving(self):
        e = Elevator(ElevatorLogic())
        e.call(5, UP)
        e.run_until_floor(2)
        self.assertEqual(e._logic_delegate.debug_path, [1, 2])
        e.call(3, UP)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])

    def test_one_below_one_up(self):
        e = Elevator(ElevatorLogic(), 3)
        e._logic_delegate.reset_debug_path(3)
        self.assertEqual(e._logic_delegate.debug_path, [3])
        e.select_floor(2)
        e.select_floor(4) # ignored
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [3, 2])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [3, 2])

    def test_select_not_go_twice(self):
        e = Elevator(ElevatorLogic())
        e.call(5, DOWN)
        e.select_floor(5)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(4)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4])

    def test_going_down_ingore_going_up(self):
        e = Elevator(ElevatorLogic())
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6)
        e.select_floor(4)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4])

    def test_ignore_call_on_current_floor(self):
        e = Elevator(ElevatorLogic())
        e.call(3, UP)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3])
        e.call(3, UP)
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])

    def test_change_direction_right_in_time(self):
        e = Elevator(ElevatorLogic())
        e.call(2, DOWN)
        e.call(4, UP)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4])
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4, 3, 2])

    def test_wait_one_step_on_change_dir(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(5)
        e.call(5, UP)
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(4)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6)
        e.select_floor(4)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 4])

    def test_other_dir_not_declared(self):
        e = Elevator(ElevatorLogic())
        e.select_floor(5)
        e.call(5, UP)
        e.call(5, DOWN)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5])
        e.select_floor(6)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 6])
        e.run_until_stopped() # go back to 5
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 6, 5])
        e.select_floor(6)  # ignored
        e.select_floor(4)
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 6, 5, 4])
        e.run_until_stopped()
        self.assertEqual(e._logic_delegate.debug_path, [1, 2, 3, 4, 5, 6, 5, 4])

if __name__ == '__main__':
    if os.environ.get("VERBOSE"):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()