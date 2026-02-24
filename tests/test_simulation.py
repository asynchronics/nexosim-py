import pytest

from nexosim import Simulation
from nexosim.exceptions import BenchNotBuiltError, SimulationNotStartedError
from nexosim.time import Duration, MonotonicTime


@pytest.fixture
def sim(coffee):
    """A started coffee bench simulation object."""
    with Simulation(coffee) as sim:
        sim.build()
        sim.init()
        yield sim


def test_reinitialize_sim_losses_state(sim):
    sim.step_until(Duration(1))
    sim.build()
    sim.init()

    assert sim.time() == MonotonicTime(0, 0)


def test_terminate_start(sim):
    sim.step_until(Duration(1))
    assert sim.time() == MonotonicTime(1, 0)
    sim.terminate()
    with pytest.raises(SimulationNotStartedError):
        sim.time()
    sim.build()
    sim.init()

    assert sim.time() == MonotonicTime(0, 0)


def test_step_sets_time_to_scheduled_event(sim):
    sim.schedule_event(MonotonicTime(1, 0), "brew_cmd")
    sim.step()

    assert sim.time() == MonotonicTime(1, 0)


def test_step_no_event_scheduled(sim):
    sim.step()

    assert sim.time() == MonotonicTime(0, 0)


def test_step_until_changes_time(sim):
    sim.step_until(MonotonicTime(1))

    assert sim.time() == MonotonicTime(1, 0)


def test_step_until_duration(sim):
    sim.step_until(MonotonicTime(1))
    sim.step_until(Duration(1))

    assert sim.time() == MonotonicTime(2, 0)


def test_schedule_event_relative_time(sim):
    sim.step_until(MonotonicTime(1))
    sim.schedule_event(Duration(1), "brew_cmd")
    sim.step()

    assert sim.time() == MonotonicTime(2)


def test_schedule_event_period(sim):
    sim.schedule_event(MonotonicTime(1), "brew_time", Duration(1), period=Duration(1))
    for _ in range(10):
        sim.step()

    assert sim.time() == MonotonicTime(10)


def test_cancel_event(sim):
    key = sim.schedule_event(MonotonicTime(1), "brew_time", Duration(1), with_key=True)
    sim.cancel_event(key)
    sim.step()

    assert sim.time() == MonotonicTime(0)


def test_cancel_periodic_event(sim):
    key = sim.schedule_event(
        MonotonicTime(1), "brew_time", Duration(1), period=Duration(1), with_key=True
    )
    sim.step()
    sim.step()

    sim.cancel_event(key)
    sim.step()

    assert sim.time() == MonotonicTime(2)


def test_process_event(sim):
    sim.process_event("brew_cmd")

    assert sim.try_read_events("flow_rate") == [4.5e-6]


def test_read_event_as_str(sim):
    sim.process_event("brew_cmd")

    assert sim.try_read_events("flow_rate", str) == ["4.5e-06"]


def test_run(sim):
    for i in range(1, 11):
        sim.schedule_event(MonotonicTime(i), "brew_cmd")

    sim.run()

    assert sim.try_read_events("flow_rate") == [4.5e-6, 0.0] * 5


def test_close_sink(sim):
    sim.disable_sink("flow_rate")

    sim.process_event("brew_cmd")

    assert sim.try_read_events("flow_rate") == []


def test_open_sink(sim):
    sim.disable_sink("flow_rate")
    sim.enable_sink("flow_rate")

    sim.process_event("brew_cmd")

    assert sim.try_read_events("flow_rate") == [4.5e-6]


def test_init_sim_not_built(coffee):
    with Simulation(coffee) as sim:
        with pytest.raises(BenchNotBuiltError):
            sim.init()


def test_init_time(coffee):
    with Simulation(coffee) as sim:
        sim.build()
        t0 = MonotonicTime(1, 0)
        sim.init(t0)

        assert sim.time() == t0


def test_save_and_restore(sim):
    sim.process_event("brew_cmd")
    state = sim.save()

    #
    sim.step()
    assert sim.try_read_events("flow_rate") == [4.5e-6, 0.0]
    assert sim.time() == MonotonicTime(25, 0)

    # Restore the simulation state to before the step
    sim.build()
    sim.restore(state)
    assert sim.time() == MonotonicTime(0, 0)

    sim.step()
    assert sim.time() == MonotonicTime(25, 0)
    assert sim.try_read_events("flow_rate") == [0.0]


def test_save_restore_and_run(sim):
    sim.process_event("brew_cmd")
    state = sim.save()

    sim.step()
    assert sim.try_read_events("flow_rate") == [4.5e-6, 0.0]
    assert sim.time() == MonotonicTime(25, 0)

    # Restore the simulation state to before the step
    sim.build()
    sim.restore_and_run(state)

    assert sim.time() == MonotonicTime(25, 0)
    assert sim.try_read_events("flow_rate") == [0.0]


def test_list_event_sources(sim):
    result = sim.list_event_sources()
    assert isinstance(result, list)
    assert set(*zip(*result, strict=False)) == {
        "brew_time",
        "brew_cmd",
        "tank_fill",
        "raw_tank_fill",
    }


def test_list_query_sources(sim):
    result = sim.list_query_sources()
    assert isinstance(result, list)
    assert result == [["test_pump"]]


def test_list_event_sinks(sim):
    result = sim.list_event_sinks()
    assert isinstance(result, list)
    assert set(*zip(*result, strict=False)) == {
        "flow_rate",
        "latest_pump_cmd",
        "water_sense",
        "pump_cmd",
    }


def test_get_event_source_schemas(sim):
    result = sim.get_event_source_schemas(["brew_cmd"])

    assert isinstance(result, dict)
    assert ("brew_cmd",) in result


def test_get_event_source_schemas_raw_endpoint(sim):
    result = sim.get_event_source_schemas(["raw_tank_fill"])

    assert len(result) == 0


def test_get_query_source_schemas(sim):
    result = sim.get_query_source_schemas(["test_pump"])

    assert isinstance(result, dict)
    assert ("test_pump",) in result
    assert "request" in result[("test_pump",)]
    assert "reply" in result[("test_pump",)]


def test_get_event_sink_schemas(sim):
    result = sim.get_event_sink_schemas(["flow_rate"])

    assert isinstance(result, dict)
    assert ("flow_rate",) in result


def test_inject_event_schedules_asap(sim):
    sim.inject_event("brew_cmd")
    sim.schedule_event(MonotonicTime(1), "tank_fill", 5.0)
    sim.step()
    assert sim.try_read_events("flow_rate") == [4.5e-6]
