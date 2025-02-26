"""Just a temporary playground--not a real test"""

from dataclasses import dataclass

import pytest

from nexosim import Simulation


@dataclass
class Duration:
    secs: int = 0
    nanos: int = 0

@pytest.mark.skip
def test_run():
    pump_flow_rate = 4.5e-6
    init_tank_volume = 1.5e-3
    default_brew_time = 25.0

    # simu = Simulation("localhost:41633")
    simu = Simulation("unix:///tmp/nexo")

    simu.start(1e-3)

    t = simu.time()
    print(t)

    # Brew one espresso shot with the default brew time.
    simu.process_event("brew_cmd")
    print("flow rate: {}".format(simu.read_events("flow_rate")))

    t = simu.step()
    print(t)
    print("flow rate: {}".format(simu.read_events("flow_rate")))

    # Drink too much coffee.
    volume_per_shot = pump_flow_rate * default_brew_time
    shots_per_tank = init_tank_volume / volume_per_shot
    for _ in range(int(shots_per_tank + 1)):
        print("--------------")
        print(t)
        simu.process_event("brew_cmd")
        print("flow rate: {}".format(simu.read_events("flow_rate")))
        t = simu.step()
        print(t)
        print("flow rate: {}".format(simu.read_events("flow_rate")))

    print("flow rate: {}".format(simu.read_events("flow_rate")))

    # Change the brew time and fill up the tank.
    brew_time = Duration(30)
    simu.process_event("brew_time", brew_time)
    simu.process_event("tank_fill", 1.0e-3)
    simu.process_event("brew_cmd")
    print("flow rate: {}".format(simu.read_events("flow_rate")))

    t = simu.step()
    print(t)
    print("flow rate: {}".format(simu.read_events("flow_rate")))
