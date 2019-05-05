# Elevator simulation

## Business Logic

As for the business logic, an example implementation is provided in the `elevator_logic.py` file in this project.

    >>> from elevator_logic import ElevatorLogic, UP, DOWN, FLOOR_COUNT
    >>> from elevator import Elevator

As provided, it doesn't pass the tests in this document. Your challenge is to fix it so that it does. To run the tests, run this in your shell:

    python -m doctest -v README.md

With the correct business logic, here's how the elevator should behave:

### Basic usage

Make an elevator. It starts at the first floor.

    >>> e = Elevator(ElevatorLogic())
    1... 

Somebody on the fifth floor wants to go down.

    >>> e.call(5, DOWN)

Keep in mind that the simulation won't actually advance until we call `step` or one of the `run_until_*` methods.

    >>> e.run_until_stopped()
    2... 3... 4... 5... 

The elevator went up to the fifth floor. A passenger boards and wants to go to the first floor.

    >>> e.select_floor(1)

Also, somebody on the third floor wants to go down.

    >>> e.call(3, DOWN)

Even though the first floor was selected first, the elevator services the call at the third floor...

    >>> e.run_until_stopped()
    4... 3... 

...before going to the first floor.

    >>> e.run_until_stopped()
    2... 1... 

### Directionality

Elevators want to keep going in the same direction. An elevator will serve as many requests in one direction as it can before going the other way. For example, if an elevator is going up, it won't stop to pick up passengers who want to go down until it's done with everything that requires it to go up.

    >>> e = Elevator(ElevatorLogic())
    1... 
    >>> e.call(2, DOWN)
    >>> e.select_floor(5)

Even though the elevator was called at the second floor first, it will service the fifth floor...

    >>> e.run_until_stopped()
    2... 3... 4... 5...

...before coming back down for the second floor.

    >>> e.run_until_stopped()
    4... 3... 2...

In fact, if a passenger tries to select a floor that contradicts the current direction of the elevator, that selection is ignored entirely. You've probably seen this before. You call the elevator to go down. The elevator shows up, and you board, not realizing that it's still going up. You select a lower floor. The elevator ignores you.

    >>> e = Elevator(ElevatorLogic())
    1...
    >>> e.select_floor(3)
    >>> e.select_floor(5)
    >>> e.run_until_stopped()
    2... 3...
    >>> e.select_floor(2)

At this point the elevator is at the third floor. It's not finished going up because it's wanted at the fifth floor. Therefore, selecting the second floor goes against the current direction, so that request is ignored.

    >>> e.run_until_stopped()
    4... 5...
    >>> e.run_until_stopped()  # nothing happens, because e.select_floor(2) was ignored

Now it's done going up, so you can select the second floor.

    >>> e.select_floor(2)
    >>> e.run_until_stopped()
    4... 3... 2...