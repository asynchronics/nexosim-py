use nexosim::ports::{EventQueue, EventSlot, EventSource};
use nexosim::registry::EndpointRegistry;
use nexosim::simulation::{Mailbox, SimInit, Simulation, SimulationError};
use nexosim::time::{AutoSystemClock, MonotonicTime};

use crate::coffee;
use crate::complex_types;

/// Create the bench assembly.
pub fn coffee_bench(
    init_tank_volume: Option<f64>,
) -> Result<(Simulation, EndpointRegistry), SimulationError> {
    let pump_flow_rate = 4.5e-6;
    let init_tank_volume = init_tank_volume.unwrap_or(1.5e-3);

    let mut pump = coffee::Pump::new(pump_flow_rate);
    let mut controller = coffee::Controller::new();
    let mut tank = coffee::Tank::new(init_tank_volume);

    // Mailboxes.
    let pump_mbox = Mailbox::new();
    let controller_mbox = Mailbox::new();
    let tank_mbox = Mailbox::new();

    // Connections.
    controller
        .pump_cmd
        .connect(coffee::Pump::command, &pump_mbox);
    tank.water_sense
        .connect(coffee::Controller::water_sense, &controller_mbox);
    pump.flow_rate
        .connect(coffee::Tank::set_flow_rate, &tank_mbox);

    // Endpoints.
    let mut registry = EndpointRegistry::new();

    let flow_rate = EventQueue::new();
    pump.flow_rate.connect_sink(&flow_rate);
    registry
        .add_event_sink(flow_rate.into_reader(), "flow_rate")
        .unwrap();

    let controller_addr = controller_mbox.address();
    let tank_addr = tank_mbox.address();

    let mut brew_cmd = EventSource::new();
    brew_cmd.connect(coffee::Controller::brew_cmd, &controller_addr);
    let mut brew_time = EventSource::new();
    brew_time.connect(coffee::Controller::brew_time, &controller_addr);
    let mut tank_fill = EventSource::new();
    tank_fill.connect(coffee::Tank::fill, &tank_addr);
    registry.add_event_source(brew_cmd, "brew_cmd").unwrap();
    registry.add_event_source(brew_time, "brew_time").unwrap();
    registry.add_event_source(tank_fill, "tank_fill").unwrap();

    // Assembly and initialization.
    let sim = SimInit::new()
        .add_model(controller, controller_mbox, "controller")
        .add_model(pump, pump_mbox, "pump")
        .add_model(tank, tank_mbox, "tank")
        .init(MonotonicTime::EPOCH)?
        .0;

    Ok((sim, registry))
}

/// Create the bench assembly.
pub fn rt_coffee_bench(
    init_tank_volume: Option<f64>,
) -> Result<(Simulation, EndpointRegistry), SimulationError> {
    let pump_flow_rate = 4.5e-6;
    let init_tank_volume = init_tank_volume.unwrap_or(1.5e-3);

    let mut pump = coffee::Pump::new(pump_flow_rate);
    let mut controller = coffee::Controller::new();
    let mut tank = coffee::Tank::new(init_tank_volume);

    // Mailboxes.
    let pump_mbox = Mailbox::new();
    let controller_mbox = Mailbox::new();
    let tank_mbox = Mailbox::new();

    // Connections.
    controller
        .pump_cmd
        .connect(coffee::Pump::command, &pump_mbox);
    tank.water_sense
        .connect(coffee::Controller::water_sense, &controller_mbox);
    pump.flow_rate
        .connect(coffee::Tank::set_flow_rate, &tank_mbox);

    // Endpoints.
    let mut registry = EndpointRegistry::new();

    let flow_rate = EventQueue::new();
    pump.flow_rate.connect_sink(&flow_rate);
    let water_sense = EventQueue::new();
    tank.water_sense.connect_sink(&water_sense);
    let pump_cmd = EventQueue::new();
    controller.pump_cmd.connect_sink(&pump_cmd);
    let latest_pump_cmd = EventSlot::new();
    controller.pump_cmd.connect_sink(&latest_pump_cmd);
    registry
        .add_event_sink(flow_rate.into_reader(), "flow_rate")
        .unwrap();
    registry
        .add_event_sink(water_sense.into_reader(), "water_sense")
        .unwrap();
    registry
        .add_event_sink(pump_cmd.into_reader(), "pump_cmd")
        .unwrap();
    registry
        .add_event_sink(latest_pump_cmd, "latest_pump_cmd")
        .unwrap();

    let controller_addr = controller_mbox.address();
    let tank_addr = tank_mbox.address();

    let mut brew_cmd = EventSource::new();
    brew_cmd.connect(coffee::Controller::brew_cmd, &controller_addr);
    let mut brew_time = EventSource::new();
    brew_time.connect(coffee::Controller::brew_time, &controller_addr);
    let mut tank_fill = EventSource::new();
    tank_fill.connect(coffee::Tank::fill, &tank_addr);
    registry.add_event_source(brew_cmd, "brew_cmd").unwrap();
    registry.add_event_source(brew_time, "brew_time").unwrap();
    registry.add_event_source(tank_fill, "tank_fill").unwrap();

    // Assembly and initialization.
    let sim = SimInit::new()
        .add_model(controller, controller_mbox, "controller")
        .add_model(pump, pump_mbox, "pump")
        .add_model(tank, tank_mbox, "tank")
        .set_clock(AutoSystemClock::new())
        .init(MonotonicTime::EPOCH)?
        .0;

    Ok((sim, registry))
}

pub fn types_bench(
    _cfg: complex_types::TestLoad,
) -> Result<(Simulation, EndpointRegistry), SimulationError> {
    let mut model = complex_types::MyModel::default();

    // Mailboxes.
    let model_mbox = Mailbox::new();
    let model_addr = model_mbox.address();

    // Endpoints.
    let mut registry = EndpointRegistry::new();

    let output = EventQueue::new();
    model.output.connect_sink(&output);
    registry
        .add_event_sink(output.into_reader(), "output")
        .unwrap();

    let mut input = EventSource::new();
    input.connect(complex_types::MyModel::my_input, &model_addr);
    registry.add_event_source(input, "input").unwrap();

    // Assembly and initialization.
    let sim = SimInit::new()
        .add_model(model, model_mbox, "model")
        .init(MonotonicTime::EPOCH)?
        .0;

    Ok((sim, registry))
}
