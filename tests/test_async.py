import asyncio

import pytest
import pytest_asyncio

from nexosim.aio import Simulation
from nexosim.exceptions import BenchNotBuiltError, SimulationNotStartedError
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
        await simu.run()

    async def observe_brewing():
        # brewing started
        assert (await simu.read_event("flow_rate", timeout)) == pump_flow_rate

        # brewing stopped
        assert (await simu.read_event("flow_rate", timeout)) == 0.0

    async def monitor_water():
        water_sense = await simu.try_read_events("water_sense")
        assert water_sense == ["NotEmpty"]

    async def monitor_commands():
        commands = await simu.try_read_events("pump_cmd")
        assert commands == ["On", "Off"]

    async def main_test():
        await observe_brewing()

        await asyncio.gather(monitor_water(), monitor_commands())

        assert (await simu.try_read_events("latest_pump_cmd")) == ["Off"]

    await simu.build(initial_volume)

    await simu.init()

    await simu.process_event("brew_time", brew_time)

    await simu.schedule_event(Duration(1), "brew_cmd")

    await asyncio.gather(run(), main_test())

    assert await simu.time() == MonotonicTime(2, 0)


@pytest_asyncio.fixture
async def sim(coffee):
    """A started coffee bench simulation object."""
    async with Simulation(coffee) as sim:
        await sim.build()
        await sim.init()
        yield sim


@pytest_asyncio.fixture
async def rt_sim(rt_coffee):
    """A started coffee bench simulation object."""
    async with Simulation(rt_coffee) as sim:
        await sim.build()
        await sim.init()
        yield sim


@pytest.mark.asyncio
async def test_reinitialize_sim_losses_state(sim):
    await sim.step_until(Duration(1))
    await sim.build()
    await sim.init()

    assert await sim.time() == MonotonicTime(0, 0)


@pytest.mark.asyncio
async def test_terminate_start(sim):
    await sim.step_until(Duration(1))
    assert await sim.time() == MonotonicTime(1, 0)
    await sim.terminate()
    with pytest.raises(SimulationNotStartedError):
        await sim.time()
    await sim.build()
    await sim.init()

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

    assert await sim.try_read_events("flow_rate") == [4.5e-6]


@pytest.mark.asyncio
async def test_read_event_as_str(sim):
    await sim.process_event("brew_cmd")

    assert await sim.try_read_events("flow_rate", str) == ["4.5e-06"]


@pytest.mark.asyncio
async def test_run(sim):
    for i in range(1, 11):
        await sim.schedule_event(MonotonicTime(i), "brew_cmd")

    await sim.run()

    assert await sim.try_read_events("flow_rate") == [4.5e-6, 0.0] * 5


@pytest.mark.slow
@pytest.mark.asyncio
async def test_run_new_event(rt_sim):
    await rt_sim.schedule_event(MonotonicTime(1), "brew_cmd")
    await rt_sim.schedule_event(MonotonicTime(3), "brew_cmd")

    async def run():
        await rt_sim.run()

    async def extra_event():
        await asyncio.sleep(2)
        await rt_sim.schedule_event(MonotonicTime(3, 1000), "brew_cmd")
        await rt_sim.schedule_event(MonotonicTime(3, 2000), "brew_cmd")

    await asyncio.gather(run(), extra_event())

    assert await rt_sim.try_read_events("flow_rate") == [4.5e-6, 0.0] * 2
    assert await rt_sim.time() == MonotonicTime(3, 2000)


@pytest.mark.asyncio
async def test_disable_sink(sim):
    await sim.disable_sink("flow_rate")

    await sim.process_event("brew_cmd")

    assert await sim.try_read_events("flow_rate") == []


@pytest.mark.asyncio
async def test_enable_sink(sim):
    await sim.disable_sink("flow_rate")
    await sim.enable_sink("flow_rate")

    await sim.process_event("brew_cmd")

    assert await sim.try_read_events("flow_rate") == [4.5e-6]


@pytest.mark.asyncio
async def test_await_event_cast(rt_sim):
    await rt_sim.schedule_event(Duration(1), "brew_cmd")

    async def step():
        await rt_sim.step()

    async def await_event():
        assert await rt_sim.read_event("flow_rate", Duration(2), str) == "4.5e-06"

    await asyncio.gather(step(), await_event())


@pytest.mark.slow
@pytest.mark.asyncio
async def test_halt(rt_sim):
    await rt_sim.schedule_event(MonotonicTime(1), "brew_cmd")
    await rt_sim.schedule_event(MonotonicTime(3), "brew_cmd")

    async def run():
        with pytest.raises(SimulationNotStartedError):
            await rt_sim.step_until(Duration(5))

    async def halt():
        await asyncio.sleep(2)
        await rt_sim.halt()

    await asyncio.gather(run(), halt())


@pytest.mark.asyncio
async def test_init_sim_not_built(coffee):
    async with Simulation(coffee) as sim:
        with pytest.raises(BenchNotBuiltError):
            await sim.init()


@pytest.mark.asyncio
async def test_init_time(coffee):
    async with Simulation(coffee) as sim:
        await sim.build()
        t0 = MonotonicTime(1, 0)
        await sim.init(t0)

        assert await sim.time() == t0


@pytest.mark.asyncio
async def test_save_and_restore(sim):
    await sim.process_event("brew_cmd")
    state = await sim.save()

    #
    await sim.step()
    assert await sim.try_read_events("flow_rate") == [4.5e-6, 0.0]
    assert await sim.time() == MonotonicTime(25, 0)

    # Restore the simulation state to before the step
    await sim.build()
    await sim.restore(state)
    assert await sim.time() == MonotonicTime(0, 0)

    await sim.step()
    assert await sim.time() == MonotonicTime(25, 0)
    assert await sim.try_read_events("flow_rate") == [0.0]


@pytest.mark.asyncio
async def test_save_restore_and_run(sim):
    await sim.process_event("brew_cmd")
    state = await sim.save()

    await sim.step()
    assert await sim.try_read_events("flow_rate") == [4.5e-6, 0.0]
    assert await sim.time() == MonotonicTime(25, 0)

    # Restore the simulation state
    await sim.build()
    await sim.restore_and_run(state)

    assert await sim.time() == MonotonicTime(25, 0)
    assert await sim.try_read_events("flow_rate") == [0.0]


@pytest.mark.asyncio
async def test_save_restore_and_run_concurrent(rt_coffee_ticker):
    async with Simulation(rt_coffee_ticker) as rt_sim:
        await rt_sim.build()
        await rt_sim.init()

        await rt_sim.process_event("brew_cmd")
        state = await rt_sim.save()

        await rt_sim.step_until(MonotonicTime(1))
        assert await rt_sim.try_read_events("flow_rate") == [4.5e-6]

        # Restore the simulation state
        async def restore_and_run():
            await rt_sim.build()
            try:
                await rt_sim.restore_and_run(state)
            except SimulationNotStartedError:
                ...

        async def stop_brewing_and_read():
            await asyncio.sleep(0.5)
            await rt_sim.inject_event("brew_cmd")
            await asyncio.sleep(0.5)
            assert await rt_sim.try_read_events("flow_rate") == [0.0]

        async def halt():
            await asyncio.sleep(1.5)
            await rt_sim.halt()

        await asyncio.gather(restore_and_run(), stop_brewing_and_read(), halt())


@pytest.mark.asyncio
async def test_list_event_sources(sim):
    result = await sim.list_event_sources()
    assert isinstance(result, list)
    assert set(*zip(*result, strict=False)) == {
        "brew_time",
        "brew_cmd",
        "tank_fill",
        "raw_tank_fill",
    }


@pytest.mark.asyncio
async def test_list_query_sources(sim):
    result = await sim.list_query_sources()
    assert isinstance(result, list)
    assert result == [["test_pump"]]


@pytest.mark.asyncio
async def test_list_event_sinks(sim):
    result = await sim.list_event_sinks()
    assert isinstance(result, list)
    assert set(*zip(*result, strict=False)) == {
        "flow_rate",
        "latest_pump_cmd",
        "water_sense",
        "pump_cmd",
    }


@pytest.mark.asyncio
async def test_get_event_source_schemas(sim):
    result = await sim.get_event_source_schemas(["brew_cmd"])

    assert isinstance(result, dict)
    assert ("brew_cmd",) in result


@pytest.mark.asyncio
async def test_get_event_source_schemas_raw_endpoint(sim):
    result = await sim.get_event_source_schemas(["raw_tank_fill"])

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_query_source_schemas(sim):
    result = await sim.get_query_source_schemas(["test_pump"])

    assert isinstance(result, dict)
    assert ("test_pump",) in result
    assert "request" in result[("test_pump",)]
    assert "reply" in result[("test_pump",)]


@pytest.mark.asyncio
async def test_get_event_sink_schemas(sim):
    result = await sim.get_event_sink_schemas(["flow_rate"])

    assert isinstance(result, dict)
    assert ("flow_rate",) in result


@pytest.mark.asyncio
async def test_inject_event_rest(sim):
    await sim.inject_event("brew_cmd")
    await sim.schedule_event(MonotonicTime(1), "tank_fill", 5.0)
    await sim.step()
    assert await sim.try_read_events("flow_rate") == [4.5e-6]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_inject_event_running(rt_sim):
    await rt_sim.schedule_event(MonotonicTime(1), "brew_cmd")
    await rt_sim.schedule_event(MonotonicTime(2), "tank_fill", 5.0)
    await rt_sim.schedule_event(MonotonicTime(3), "brew_cmd")

    async def run():
        await rt_sim.step_until(Duration(3))

    async def inject():
        await asyncio.sleep(1.5)
        await rt_sim.inject_event("brew_cmd")

    await asyncio.gather(run(), inject())
    assert await rt_sim.try_read_events("flow_rate") == [4.5e-06, 0.0, 4.5e-06]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_inject_event_running_with_ticker(rt_coffee_ticker):
    async with Simulation(rt_coffee_ticker) as rt_sim:
        await rt_sim.build()
        await rt_sim.init()

        await rt_sim.schedule_event(MonotonicTime(1), "brew_cmd")

        async def run():
            await rt_sim.step_until(Duration(2))

        async def inject():
            await asyncio.sleep(1.5)
            await rt_sim.inject_event("brew_cmd")

        await asyncio.gather(run(), inject())
        assert await rt_sim.try_read_events("flow_rate") == [4.5e-06, 0.0]
