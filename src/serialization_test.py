from nexosim import Simulation
from nexosim.time import MonotonicTime

state = None

with Simulation("0.0.0.0:3700") as sim:
    sim.start(MonotonicTime(0))
    sim.schedule_event(MonotonicTime(3), "input", 17)
    sim.schedule_event(MonotonicTime(6), "input", 21)
    sim.step()
    state = sim.save()
    print(state)

    sim.restore(state)
    # sim.step()
    # sim.step()

