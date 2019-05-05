UP = 1
DOWN = 2
FLOOR_COUNT = 6

def debug_motor_direction(direction):
    if direction == UP:
        return "UP"
    elif direction == DOWN:
        return "DOWN"
    return direction

class ElevatorLogic(object):
    """
    An incorrect implementation. Can you make it pass all the tests?

    Fix the methods below to implement the correct logic for elevators.
    The tests are integrated into `README.md`. To run the tests:
    $ python -m doctest -v README.md

    To learn when each method is called, read its docstring.
    To interact with the world, you can get the current floor from the
    `current_floor` property of the `callbacks` object, and you can move the
    elevator by setting the `motor_direction` property. See below for how this is done.
    """

    def __init__(self):
        # Feel free to add any instance variables you want.
        self.destination_floor = None
        self.callbacks = None

        self.directions = []

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        if self.destination_floor is None:
            self.destination_floor = floor
        else:
            assert False, "called: destination floor is already set to {}, current={}".format(self.destination_floor, self.callbacks.current_floor)

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        if self.destination_floor is None:
            self.destination_floor = floor
        else:
            assert False, "selected: destination floor is already set to {}, direction={}".format(self.destination_floor, debug_motor_direction(self.callbacks.motor_direction))

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        if self.destination_floor == self.callbacks.current_floor:
            self.callbacks.motor_direction = None
            self.destination_floor = None

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        if self.destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif self.destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN
