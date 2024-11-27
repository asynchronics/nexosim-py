"""The root module.

This module defines the `Simulation` type, which acts as a front-end to a
NeXosim gRPC simulation server.



Example usage:
    Starting a simulation server on port 41633:

    ```py
    from nexosim import Simulation
    from nexosim.time import MonotonicTime

    sim = Simulation(address='localhost:41633')

    # Start the simulation at 1957-11-04 19:28:34 TAI.
    t0 = MonotonicTime(1957, 11, 04, 19, 28, 34)

    # We assume here that the bench requires an integer parameter for initialization.
    simu.start(t0, 42)
    ```

    Advance simulation time and read events from a sink.
    ```py
    from dataclasses import dataclass
    from nexosim import Simulation
    from nexosim.time import MonotonicTime, Duration

    # We could read simulation events as dictionaries, but it is often more
    # convenient to use classes that mirror their Rust counterpart.
    @dataclass
    class OutputEvent:
        foo: int
        bar: str

    sim = Simulation(address='localhost:41633')
    sim.start(MonotonicTime()) # use the 1970-01-01 00:00:00 TAI epoch

    # Advance the simulation to the next scheduled timestamp.
    sim.step()

    # Read a list of `OutputEvent` objects from the "output" event sink.
    outputs = sim.read_events("output", OutputEvent)
    print(outputs)

    # Advance the simulation by 3s and read the final simulation time.
    t = sim.step_until(Duration(3))
    ```

"""

from ._simulation import Simulation, EventKey

__all__ = ["Simulation", "EventKey"]
