UP = 1
DOWN = 2
FLOOR_COUNT = 6

def sort_destinations(current, destinations):
    result = []
    print("SORT, we arer at {}".format(current))
    print("NOW: {}".format(destinations))
    print("DISTINACE: {}".format(list(map(lambda floor: abs(current - floor[0]), destinations))))
    destinations = sorted(destinations, key=lambda floor: -1* abs(current - floor[0]))
    print("NEW: {}".format(destinations))
    future_direction = DOWN if current > destinations[0][0] else UP
    # first element in destinations is the farest away,
    # prioritice all requests which are on the way AND are in the same direction
    if future_direction == DOWN:
        on_they_way = list(filter(lambda destination: destination[0] < current and destination[1] in (future_direction, None), destinations[1:]))
    else:
        on_they_way = list(filter(lambda destination: destination[0] > current and destination[1] in (future_direction, None), destinations[1:]))    
    # TODO: do we need that??? order stop on its way, nearesrt first
    #on_the_way = sorted(on_the_way, key=lambda floor: abs(current - floor[0]))
    print("GOTO {}, ON THE WAY {}".format(destinations[0], on_they_way))
    next_destinations = on_they_way + [destinations[0]]
    for destination in destinations[1:]:
        if destination not in next_destinations:
            next_destinations.append(destination)
    return (next_destinations, bool(on_they_way))

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
        self.destinations = []
        self.callbacks = None

        self.is_on_way = False
        self.debug_path = [1] # we always start at floor one

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        if (floor, direction) not in self.destinations:
            self.destinations.append((floor, direction))

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        print(self.callbacks.motor_direction, self.is_on_way)
        if self.callbacks.motor_direction is not None or self.is_on_way:
            relative_direction = DOWN if floor < self.callbacks.current_floor else UP
            if relative_direction != self.callbacks.motor_direction:
                # ignore
                print("IGNOREEEEEEEEE")
                return 
        if (floor, None) not in self.destinations:
            self.destinations.append((floor, None))

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        self.debug_path.append(self.callbacks.current_floor)
        if self.destinations and self.destinations[0][0] == self.callbacks.current_floor:
            self.destinations.pop(0)
            if not self.is_on_way or len(self.destinations) <= 1:
                self.callbacks.motor_direction = None
            

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        if not self.destinations:
            return
        # if we did not decide whereto go yet, we always go to the nearest floor first
        if self.callbacks.motor_direction is None:
            print("re-sort, current={}".format(self.callbacks.current_floor))
            print(self.destinations)
            self.destinations, self.is_on_way = sort_destinations(self.callbacks.current_floor, self.destinations)
            print(self.destinations)
        destination_floor = self.destinations[0][0]
        if destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN