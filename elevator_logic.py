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

def get_relative_direction(current_floor, floor):
    return DOWN if floor < current_floor else UP

def sort_destinations(current, destinations, priority=None):
    result = []
    logging.debug("SORT, we arer at {}".format(current))
    logging.debug("NOW: {}".format(destinations))
    logging.debug("DISTINACE: {}".format(list(map(lambda floor: abs(current - floor[0]), destinations))))
    destinations = sorted(destinations, key=lambda floor: -1* abs(current - floor[0]))
    logging.debug("NEW: {}".format(destinations))
    relative_direction = get_relative_direction(current, destinations[0][0])
    # first element in destinations is the farest away,
    # prioritice all requests which are on the way AND are in the same direction
    if relative_direction == DOWN:
        on_they_way = list(filter(lambda destination: destination[0] < current and destination[1] in (relative_direction, None), destinations[1:]))
    else:
        on_they_way = list(filter(lambda destination: destination[0] > current and destination[1] in (relative_direction, None), destinations[1:]))    
    # TODO: do we need that??? order stop on its way, nearesrt first
    #on_the_way = sorted(on_the_way, key=lambda floor: abs(current - floor[0]))
    logging.debug("GOTO {}, ON THE WAY {}".format(destinations[0], on_they_way))
    if priority and priority in destinations:
        priority = [destinations.pop(destinations.index(priority))]
    else:
        priority = []
    next_destinations = priority + on_they_way
    if destinations:
        next_destinations += [destinations[0]]
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
        self.current_requested_dir = None
        self.priority = None
        self.reset_debug_path(1) # per default we start at floor one, re-call this method in other test-scenarios

    def reset_debug_path(self, floor):
        self.debug_path = [floor]

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        logging.info("CALLLLLLLLLLLLL {} {}".format(floor, direction))
        if floor == self.callbacks.current_floor and self.callbacks.motor_direction is None:
            # dont move if the requested floor is the current one
            return
        if (floor, direction) not in self.destinations:
            if (floor, get_oposite_direction(direction)) not in self.destinations:
                rel_dir = get_relative_direction(self.callbacks.current_floor, floor)
                self.destinations.append((floor, direction))
                if rel_dir == self.old_direction:
                    # goto the new floor with prio as we are already moving in this direction
                    self.priority = (floor, direction)
                return

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        logging.debug("++++{} {}".format(self.callbacks.motor_direction, self.is_on_way))
        logging.debug("try to select floor={}, dests={}, cur_motor_dir={}".format(floor, self.destinations, self.current_requested_dir))
        relative_direction = get_relative_direction(self.callbacks.current_floor, floor)
        if self.callbacks.motor_direction is not None or self.is_on_way:
            if relative_direction != self.callbacks.motor_direction:
                # ignore
                logging.debug(">>>>>>> IGNOREEEEEEEEE")
                return
        if (floor, None) not in self.destinations:
            if floor in [dest[0] for dest in self.destinations]:
                logging.debug(">>>>>>> IGNOREEEEEEEEE, already going there")
                return
            is_all_selected_dests = not any(filter(None, [dest[1] for dest in self.destinations]))
            same_relative_dirs = any(map(lambda dest: get_relative_direction(self.callbacks.current_floor, dest[0]) == relative_direction, self.destinations))
            
            if self.current_requested_dir is not None and relative_direction != self.current_requested_dir:
                # TODO: might replace the next one
                logging.debug(">>>>>>>>>> IIIIIIIIGNORE - wrong direction")
                return

            if is_all_selected_dests and not same_relative_dirs and self.destinations:
                # TODO: do we need it??????
                logging.debug(">>>>>>> IGNOREEEEEEEEEEEE - nonesense")
                return
            logging.debug("############### ALARM {} {} - {} {}".format(is_all_selected_dests, self.destinations, is_all_selected_dests, same_relative_dirs))
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
        logging.info("CHANGED - DESTS: {}, current={}, dir={}".format(self.destinations, self.callbacks.current_floor, self.callbacks.motor_direction))
        if (self.callbacks.current_floor, self.callbacks.motor_direction) in self.destinations:
            logging.error(">>>>>>>>>>>>>>>>>> ALARM")
            # TODO: de-duplicate
            cur_floor, motor_dir = self.destinations.pop(self.destinations.index((self.callbacks.current_floor, self.callbacks.motor_direction)))
            if motor_dir is not None:
                self.current_requested_dir = motor_dir
            self.old_direction = self.callbacks.motor_direction
            if not self.is_on_way or (self.destinations and self.old_direction != self.destinations[0][0]) or not self.destinations:
                logging.error("STOP MOTOR, destinations={}".format(self.destinations))
                self.callbacks.motor_direction = None
        self.debug_path.append(self.callbacks.current_floor)
        if self.destinations and self.destinations[0][0] == self.callbacks.current_floor:
            cur_floor, motor_dir = self.destinations.pop(0)
            if motor_dir is not None:
                self.current_requested_dir = motor_dir
            self.old_direction = self.callbacks.motor_direction
            if not self.is_on_way or (self.destinations and self.old_direction != self.destinations[0][0]) or not self.destinations:
                logging.error("STOP MOTOR, destinations={}".format(self.destinations))
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