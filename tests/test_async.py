import asyncio

import pytest
import pytest_asyncio

from nexosim.aio import Simulation
from nexosim.exceptions import SimulationHaltedError, SimulationNotStartedError
from nexosim.time import Duration, MonotonicTime


@pytest.mark.slow
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

    await simu.start(initial_volume)

    await simu.process_event("brew_time", brew_time)

    await simu.schedule_event(Duration(1), "brew_cmd")

    await asyncio.gather(run(), main_test())

    assert await simu.time() == MonotonicTime(2, 0)


@pytest_asyncio.fixture
async def sim(coffee):
    """A started coffee bench simulation object."""
    async with Simulation(coffee) as sim:
        await sim.start()
        yield sim


@pytest_asyncio.fixture
async def rt_sim(rt_coffee):
    """A started coffee bench simulation object."""
    async with Simulation(rt_coffee) as sim:
        await sim.start()
        yield sim


@pytest.mark.asyncio
async def test_reinitialize_sim_losses_state(sim):
    await sim.step_until(Duration(1))
    await sim.start()

    assert await sim.time() == MonotonicTime(0, 0)


@pytest.mark.asyncio
async def test_terminate_start(sim):
    await sim.step_until(Duration(1))
    assert await sim.time() == MonotonicTime(1, 0)
    await sim.terminate()
    with pytest.raises(SimulationNotStartedError):
        await sim.time()
    await sim.start()

    assert await sim.time() == MonotonicTime(0, 0)


@pytest.mark.asyncio
async def test_step_sets_time_to_scheduled_event(sim):
    await sim.schedule_event(MonotonicTime(1, 0), "brew_cmd")
    await sim.step()

    assert await sim.time() == MonotonicTime(1, 0)


@pytest.mark.asyncio
async def test_step_no_event_scheduled(sim):
    await sim.step()

    assert await sim.time() == MonotonicTime(0, 0)


@pytest.mark.asyncio
async def test_step_until_changes_time(sim):
    await sim.step_until(MonotonicTime(1))

    assert await sim.time() == MonotonicTime(1, 0)


@pytest.mark.asyncio
async def test_step_until_duration(sim):
    await sim.step_until(MonotonicTime(1))
    await sim.step_until(Duration(1))

    assert await sim.time() == MonotonicTime(2, 0)


@pytest.mark.asyncio
async def test_schedule_event_relative_time(sim):
    await sim.step_until(MonotonicTime(1))
    await sim.schedule_event(Duration(1), "brew_cmd")
    await sim.step()

    assert await sim.time() == MonotonicTime(2)


@pytest.mark.asyncio
async def test_schedule_event_period(sim):
    await sim.schedule_event(
        MonotonicTime(1), "brew_time", Duration(1), period=Duration(1)
    )
    for _ in range(10):
        await sim.step()

    assert await sim.time() == MonotonicTime(10)


@pytest.mark.asyncio
async def test_cancel_event(sim):
    key = await sim.schedule_event(
        MonotonicTime(1), "brew_time", Duration(1), with_key=True
    )
    await sim.cancel_event(key)
    await sim.step()

    assert await sim.time() == MonotonicTime(0)


@pytest.mark.asyncio
async def test_cancel_periodic_event(sim):
    key = await sim.schedule_event(
        MonotonicTime(1), "brew_time", Duration(1), period=Duration(1), with_key=True
    )
    await sim.step()
    await sim.step()

    await sim.cancel_event(key)
    await sim.step()

    assert await sim.time() == MonotonicTime(2)


@pytest.mark.asyncio
async def test_process_event(sim):
    await sim.process_event("brew_cmd")

    assert await sim.read_events("flow_rate") == [4.5e-6]


@pytest.mark.asyncio
async def test_read_event_as_str(sim):
    await sim.process_event("brew_cmd")

    assert await sim.read_events("flow_rate", str) == ["4.5e-06"]


@pytest.mark.asyncio
async def test_step_unbounded(sim):
    for i in range(1, 11):
        await sim.schedule_event(MonotonicTime(i), "brew_cmd")

    await sim.step_unbounded()

    assert await sim.read_events("flow_rate") == [4.5e-6, 0.0] * 5


@pytest.mark.slow
@pytest.mark.asyncio
async def test_step_unbounded_new_event(rt_sim):
    await rt_sim.schedule_event(MonotonicTime(1), "brew_cmd")
    await rt_sim.schedule_event(MonotonicTime(3), "brew_cmd")

    async def run():
        await rt_sim.step_unbounded()

    async def extra_event():
        await asyncio.sleep(2)
        await rt_sim.schedule_event(MonotonicTime(3, 1000), "brew_cmd")
        await rt_sim.schedule_event(MonotonicTime(3, 2000), "brew_cmd")

    await asyncio.gather(run(), extra_event())

    assert await rt_sim.read_events("flow_rate") == [4.5e-6, 0.0] * 2
    assert await rt_sim.time() == MonotonicTime(3, 2000)


@pytest.mark.asyncio
async def test_close_sink(sim):
    await sim.close_sink("flow_rate")

    await sim.process_event("brew_cmd")

    assert await sim.read_events("flow_rate") == []


@pytest.mark.asyncio
async def test_open_sink(sim):
    await sim.close_sink("flow_rate")
    await sim.open_sink("flow_rate")

    await sim.process_event("brew_cmd")

    assert await sim.read_events("flow_rate") == [4.5e-6]


@pytest.mark.asyncio
async def test_await_event_cast(rt_sim):
    await rt_sim.schedule_event(Duration(1), "brew_cmd")

    async def step():
        await rt_sim.step()

    async def await_event():
        assert await rt_sim.await_event("flow_rate", Duration(2), str) == "4.5e-06"

    await asyncio.gather(step(), await_event())


@pytest.mark.slow
@pytest.mark.asyncio
async def test_halt(rt_sim):
    await rt_sim.schedule_event(MonotonicTime(1), "brew_cmd")
    await rt_sim.schedule_event(MonotonicTime(3), "brew_cmd")

    async def run():
        with pytest.raises(SimulationHaltedError):
            await rt_sim.step_until(Duration(5))

    async def halt():
        await asyncio.sleep(2)
        await rt_sim.halt()

    await asyncio.gather(run(), halt())
