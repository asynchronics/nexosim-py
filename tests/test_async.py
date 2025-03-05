import asyncio

import pytest

from nexosim.aio import Simulation

from nexosim.time import Duration, MonotonicTime

@pytest.mark.asyncio
async def test_concurrent_event_and_read(rt_coffee):
    pump_flow_rate = 4.5e-6
    brew_time = Duration(1)
    initial_volume = 1e-3
    simu = Simulation(rt_coffee)

    async def read_flow_rate():
        await asyncio.sleep(1)

        # brewing started
        assert (await simu.read_events("flow_rate"))[0] == pump_flow_rate

        await asyncio.sleep(1.5)

        # brewing stopped
        assert (await simu.read_events("flow_rate"))[0] == 0.0

    async def step():
        await simu.step_until(Duration(3))

    await simu.start(initial_volume)

    await simu.process_event("brew_time", brew_time)

    await simu.schedule_event(Duration(1), "brew_cmd")

    await asyncio.gather(step(), read_flow_rate())

    assert await simu.time() == MonotonicTime(3, 0)
