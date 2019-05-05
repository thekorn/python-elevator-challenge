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