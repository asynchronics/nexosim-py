import pytest

from nexosim import Simulation
from nexosim.exceptions import SimulationNotStartedError
from nexosim.time import Duration, MonotonicTime


@pytest.fixture
def sim(coffee):
    """A started coffee bench simulation object."""
    with Simulation(coffee) as sim:
        sim.start()
        yield sim


def test_reinitialize_sim_losses_state(sim):
    sim.step_until(Duration(1))
    sim.start()

    assert sim.time() == MonotonicTime(0, 0)


def test_terminate_start(sim):
    sim.step_until(Duration(1))
    assert sim.time() == MonotonicTime(1, 0)
    sim.terminate()
    with pytest.raises(SimulationNotStartedError):
        sim.time()
    sim.start()

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

    assert sim.read_events("flow_rate") == [4.5e-6]


def test_read_event_as_str(sim):
    sim.process_event("brew_cmd")

    assert sim.read_events("flow_rate", str) == ["4.5e-06"]


def test_step_unbounded(sim):
    for i in range(1, 11):
        sim.schedule_event(MonotonicTime(i), "brew_cmd")

    sim.step_unbounded()

    assert sim.read_events("flow_rate") == [4.5e-6, 0.0] * 5


def test_close_sink(sim):
    sim.close_sink("flow_rate")

    sim.process_event("brew_cmd")

    assert sim.read_events("flow_rate") == []


def test_open_sink(sim):
    sim.close_sink("flow_rate")
    sim.open_sink("flow_rate")

    sim.process_event("brew_cmd")

    assert sim.read_events("flow_rate") == [4.5e-6]


def test_list_event_sources(sim):
    result = sim.list_event_sources()
    assert isinstance(result, list)
    assert set(result) == {"brew_time", "brew_cmd", "tank_fill", "raw_tank_fill"}


def test_list_query_sources(sim):
    result = sim.list_query_sources()
    assert isinstance(result, list)
    assert result == ["test_pump"]


def test_list_event_sinks(sim):
    result = sim.list_event_sinks()
    assert isinstance(result, list)
    assert result == ["flow_rate"]


def test_get_event_source_schemas(sim):
    result = sim.get_event_source_schemas(["brew_cmd"])

    assert isinstance(result, dict)
    assert "brew_cmd" in result


def test_get_event_source_schemas_raw_endpoint(sim):
    result = sim.get_event_source_schemas(["raw_tank_fill"])

    assert len(result) == 0


def test_get_query_source_schemas(sim):
    result = sim.get_query_source_schemas(["test_pump"])

    assert isinstance(result, dict)
    assert "test_pump" in result
    assert "request" in result["test_pump"]
    assert "reply" in result["test_pump"]


def test_get_event_sink_schemas(sim):
    result = sim.get_event_sink_schemas(["flow_rate"])

    assert isinstance(result, dict)
    assert "flow_rate" in result
