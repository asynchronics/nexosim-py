import asyncio

import pytest

from nexosim.aio import Simulation

from nexosim.time import Duration, MonotonicTime

@pytest.mark.asyncio
async def test_concurrent_event_and_read(rt_coffee):
    pump_flow_rate = 4.5e-6
    brew_time = Duration(1)
    timeout = Duration(2)
    initial_volume = 1e-3
    simu = Simulation(rt_coffee)

    async def run():
        await simu.step_unbounded()

    async def observe_brewing():
        # brewing started
        assert (await simu.await_event("flow_rate", timeout)) == pump_flow_rate

        # brewing stopped
        assert (await simu.await_event("flow_rate", timeout)) == 0.0

    async def monitor_water():
        water_sense = await simu.read_events("water_sense")
        assert water_sense == ["NotEmpty"]

    async def monitor_commands():
        commands = await simu.read_events("pump_cmd")
        assert commands == ["On", "Off"]

    async def main_test():
        await observe_brewing()

        await asyncio.gather(monitor_water(), monitor_commands())

        assert (await simu.read_events("latest_pump_cmd")) == ["Off"]

        await simu.halt()


    await simu.start(initial_volume)

    await simu.process_event("brew_time", brew_time)

    await simu.schedule_event(Duration(1), "brew_cmd")

    await asyncio.gather(run(), main_test())

    assert await simu.time() == MonotonicTime(2, 0)
