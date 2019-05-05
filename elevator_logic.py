import logging

UP = 1
DOWN = 2
FLOOR_COUNT = 6

def get_oposite_direction(direction):
    if direction == UP:
        return DOWN
    if direction == DOWN:
        return UP
    assert False, "Cannot change direction, unknow direction {}".format(direction)

def sort_destinations(current, destinations, priority=None):
    result = []
    logging.debug("SORT, we arer at {}".format(current))
    logging.debug("NOW: {}".format(destinations))
    logging.debug("DISTINACE: {}".format(list(map(lambda floor: abs(current - floor[0]), destinations))))
    destinations = sorted(destinations, key=lambda floor: -1* abs(current - floor[0]))
    logging.debug("NEW: {}".format(destinations))
    future_direction = DOWN if current > destinations[0][0] else UP
    # first element in destinations is the farest away,
    # prioritice all requests which are on the way AND are in the same direction
    if future_direction == DOWN:
        on_they_way = list(filter(lambda destination: destination[0] < current and destination[1] in (future_direction, None), destinations[1:]))
    else:
        on_they_way = list(filter(lambda destination: destination[0] > current and destination[1] in (future_direction, None), destinations[1:]))    
    # TODO: do we need that??? order stop on its way, nearesrt first
    #on_the_way = sorted(on_the_way, key=lambda floor: abs(current - floor[0]))
    logging.debug("GOTO {}, ON THE WAY {}".format(destinations[0], on_they_way))
    if priority and priority in destinations:
        priority = [destinations.pop(destinations.index(priority))]
    else:
        priority = []
    next_destinations = priority + on_they_way + [destinations[0]]
    for destination in destinations[1:]:
        if destination not in next_destinations:
            next_destinations.append(destination)
    return (next_destinations, bool(on_they_way))

class ElevatorLogic(object):
    """
    An incorrect implementation. Can you make it pass all the tests?

    Fix the methods below to implement the correct logic for elevators.
    The tests are integrated into `README.md`. To run the tests:
    $ python3.7 -m doctest -v README.md -f -o NORMALIZE_WHITESPACE

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
        self.old_direction = None
        self.priority = None
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
            if (floor, get_oposite_direction(direction)) not in self.destinations:
                self.destinations.append((floor, direction))

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        logging.debug("++++{} {}".format(self.callbacks.motor_direction, self.is_on_way))
        relative_direction = DOWN if floor < self.callbacks.current_floor else UP
        if self.callbacks.motor_direction is not None or self.is_on_way:
            if relative_direction != self.callbacks.motor_direction:
                # ignore
                logging.debug(">>>>>>> IGNOREEEEEEEEE")
                return
        if (floor, None) not in self.destinations:
            self.destinations.append((floor, None))
            if relative_direction == self.callbacks.motor_direction:
                logging.debug("+++++ before: {}".format(self.destinations))
                self.destinations, self.is_on_way = sort_destinations(self.callbacks.current_floor, self.destinations)
                logging.debug("+++++ after: {}".format(self.destinations))
        if self.callbacks.motor_direction is None and relative_direction == self.old_direction:
            self.priority = (floor, None)

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        logging.info("CHANGED - DESTS: {}, current={}".format(self.destinations, self.callbacks.current_floor))
        self.debug_path.append(self.callbacks.current_floor)
        if self.destinations and self.destinations[0][0] == self.callbacks.current_floor:
            self.destinations.pop(0)
            if not self.is_on_way or len(self.destinations) <= 1:
                logging.debug("STOP MOTOR, destinations={}".format(self.destinations))
                self.old_direction = self.callbacks.motor_direction
                self.callbacks.motor_direction = None
            

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        logging.info("READY - DESTS: {}".format(self.destinations))
        if not self.destinations:
            return
        # if we did not decide whereto go yet, we always go to the nearest floor first
        if self.callbacks.motor_direction is None:
            logging.debug("re-sort, current={}".format(self.callbacks.current_floor))
            logging.debug(self.destinations)
            self.destinations, self.is_on_way = sort_destinations(self.callbacks.current_floor, self.destinations, self.priority)
            logging.debug(self.destinations)
        destination_floor = self.destinations[0][0]
        if destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN