import logging

UP = 1
DOWN = 2
FLOOR_COUNT = 6

def get_oposite_direction(direction):
    """ Returns the oposite Direction, raises an Excpetion if direction is unknown """
    if direction == UP:
        return DOWN
    if direction == DOWN:
        return UP
    assert False, "Cannot change direction, unknow direction {}".format(direction)

def get_relative_direction(current_floor, floor):
    """ Get direction for given floor based on a current one """
    return DOWN if floor < current_floor else UP

def sort_destinations(current, destinations, priority=None):
    """ Sort destinations, first one will be the very next destination
    
        Criterias:
            * if priority is not None, priority will be the next destination
            * the general direction will be determind by the farest floor
            * every request which is on the way, and on the same direction
              will be prioritieced

        Returns a tuple, where:
            * the first element is the list of all future destinations
            * the second element is a boolean describing if the next
              destination is a one which is on the way to the `real` target
    """
    logging.debug("SORTING: current destinations={}")
    destinations = sorted(destinations, key=lambda floor: -1 * abs(current - floor[0]))
    relative_direction = get_relative_direction(current, destinations[0][0])
    # first element in destinations is the farest away,
    # prioritice all requests which are on the way AND are in the same direction
    if relative_direction == DOWN:
        on_the_way = list(filter(lambda destination: destination[0] < current and destination[1] in (relative_direction, None), destinations[1:]))
    else:
        on_the_way = list(filter(lambda destination: destination[0] > current and destination[1] in (relative_direction, None), destinations[1:]))    
    if priority and priority in destinations:
        priority = [destinations.pop(destinations.index(priority))]
    else:
        priority = []
    next_destinations = priority + on_the_way
    if destinations:
        next_destinations += [destinations[0]]
    for destination in destinations[1:]:
        if destination not in next_destinations:
            next_destinations.append(destination)
    logging.debug("SORTING:RESULT destinations={}, on_the_way={}".format(next_destinations, bool(on_the_way)))
    return (next_destinations, bool(on_the_way))

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
        self.destinations = []
        self.callbacks = None

        # helper variables
        self.is_on_way = False
        self.is_idle = []
        self.old_direction = None
        self.current_requested_dir = None
        self.priority = None
        self.reset_debug_path(1) # per default we start at floor one, re-call this method in other test-scenarios

    def reset_debug_path(self, floor):
        """ initialize the debug path, use for debugging purposes only """
        self.debug_path = [floor]

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        logging.debug("CALLED at floor={} for direction={}".format(floor, direction))
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
            else:
                # if someone pressed both directions on the same floor
                # the elevator sets itself in an idle mode to skip the next one or two requests
                # Criteria:
                #   * if the next requested floor is in the current direction we go there,
                #     then back to the floor where the elevator got reset, the next request will
                #     be ignored, and then normally proveeded
                #   * if the next request is not in the current direction, we skip the next two
                #     requests
                logging.debug("IDLE: set into idle mode")
                self.is_idle = [True, True]
                self.destinations.pop(
                    self.destinations.index((floor, get_oposite_direction(direction)))
                )

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        logging.debug("SELECTED: floor={}".format(floor))
        if self.is_idle:
            # in idel mode, we are ignoring this request
            self.is_idle.pop()
            return
        relative_direction = get_relative_direction(self.callbacks.current_floor, floor)
        if self.callbacks.motor_direction is not None or self.is_on_way:
            # if the the elevator is moving, and the requested floor is in the oposite direction
            # we ignore the request
            if relative_direction != self.callbacks.motor_direction:
                return
        if (floor, None) not in self.destinations:
            # the selected destination must not be already in the stack
            if floor in [dest[0] for dest in self.destinations]:
                # we are visting the floor soon anyways, no need to do so twice
                return
            is_all_selected_dests = not any(filter(None, [dest[1] for dest in self.destinations]))
            same_relative_dirs = any(map(lambda dest: get_relative_direction(self.callbacks.current_floor, dest[0]) == relative_direction, self.destinations))
            
            if self.current_requested_dir is not None and relative_direction != self.current_requested_dir:
                # destinations in two different directions are requested, without moving
                # we are ignoring the one whih is not in the current direction
                return

            if is_all_selected_dests and not same_relative_dirs and self.destinations:
                # the request which is not in  the current direction gets ignored
                # if contraire destinations are selected
                return
            # Add the target floor to destinations
            self.destinations.append((floor, None))
            if relative_direction == self.callbacks.motor_direction:
                # re-order the destinations to go to the next floor which is in the current direction
                self.destinations, self.is_on_way = sort_destinations(self.callbacks.current_floor, self.destinations)
        if self.callbacks.motor_direction is None and relative_direction == self.old_direction:
            # if the elevator is not moving and the future target is in the previous
            # direction we prioritize the requested floor
            # `the elevator was going down, a new request to go further down came in, we are going there first`
            self.priority = (floor, None)

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        logging.debug("CHANGED: current_floor={}, dests={}, motor_dir={}".format(self.callbacks.current_floor, self.destinations, self.callbacks.motor_direction))
        # add the current floor to the debugging path
        self.debug_path.append(self.callbacks.current_floor)
        if (self.callbacks.current_floor, self.callbacks.motor_direction) in self.destinations:
            # there is another request for the same floor in the stack of destinations
            # we can ignore this one, as we are already there
            # we just have to remember the direction we where comeing from
            # TODO: de-duplicate
            cur_floor, motor_dir = self.destinations.pop(self.destinations.index((self.callbacks.current_floor, self.callbacks.motor_direction)))
            if motor_dir is not None:
                self.current_requested_dir = motor_dir
            self.old_direction = self.callbacks.motor_direction
            if not self.is_on_way or (self.destinations and self.old_direction != self.destinations[0][0]) or not self.destinations:
                # stop the elevator as we are not on transition to another target in the same direction
                self.callbacks.motor_direction = None
        if self.destinations and self.destinations[0][0] == self.callbacks.current_floor:
            # if the next destination is for the same floor we just have to remember the 
            # current direction of movement
            cur_floor, motor_dir = self.destinations.pop(0)
            if motor_dir is not None:
                self.current_requested_dir = motor_dir
            self.old_direction = self.callbacks.motor_direction
            if not self.is_on_way or (self.destinations and self.old_direction != self.destinations[0][0]) or not self.destinations:
                # stop the elevator as we are not on transition to another target in the same direction
                self.callbacks.motor_direction = None

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        logging.debug("READY: currecnt_floor={}, destinations={}".format(self.callbacks.current_floor, self.destinations))
        if not self.destinations:
            # no more work to do, stop here
            return
        if self.callbacks.motor_direction is None:
            # if we did not decide where to go yet, we always go to the nearest floor first
            self.destinations, self.is_on_way = sort_destinations(self.callbacks.current_floor, self.destinations, self.priority)
        # decide which direction to go for the next destination
        destination_floor = self.destinations[0][0]
        if destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN