use nexosim::ports::{
    event_queue_endpoint, event_slot_endpoint, EventSource, QuerySource, SinkState,
};
use nexosim::simulation::{Mailbox, SimInit};
use nexosim::time::{AutoSystemClock, PeriodicTicker};
use std::error::Error;
use std::time::Duration;

use crate::coffee;
use crate::complex_types;

/// Create the bench assembly.
pub fn coffee_bench(init_tank_volume: Option<f64>) -> Result<SimInit, Box<dyn Error>> {
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

    let mut bench = SimInit::new();

    // Endpoints.

    let flow_rate = event_queue_endpoint(&mut bench, SinkState::Enabled, "flow_rate")?;
    pump.flow_rate.connect_sink(flow_rate);
    let water_sense = event_queue_endpoint(&mut bench, SinkState::Enabled, "water_sense").unwrap();
    tank.water_sense.connect_sink(water_sense);
    let pump_cmd = event_queue_endpoint(&mut bench, SinkState::Enabled, "pump_cmd").unwrap();
    controller.pump_cmd.connect_sink(pump_cmd);
    let latest_pump_cmd =
        event_slot_endpoint(&mut bench, SinkState::Enabled, "latest_pump_cmd").unwrap();
    controller.pump_cmd.connect_sink(latest_pump_cmd);

    EventSource::new()
        .connect(coffee::Controller::brew_cmd, &controller_mbox)
        .bind_endpoint(&mut bench, "brew_cmd")?;
    EventSource::new()
        .connect(coffee::Controller::brew_time, &controller_mbox)
        .bind_endpoint(&mut bench, "brew_time")?;
    EventSource::new()
        .connect(coffee::Tank::fill, &tank_mbox)
        .bind_endpoint(&mut bench, "tank_fill")?;
    EventSource::new()
        .connect(coffee::Tank::fill, &tank_mbox)
        .bind_endpoint_raw(&mut bench, "raw_tank_fill")?;

    QuerySource::new()
        .connect(coffee::Pump::test_cmd, &pump_mbox)
        .bind_endpoint(&mut bench, "test_pump")?;

    // Assembly and initialization.

    Ok(bench
        .add_model(controller, controller_mbox, "controller")
        .add_model(pump, pump_mbox, "pump")
        .add_model(tank, tank_mbox, "tank"))
}

/// Real time coffee simulation bench without ticker.
pub fn rt_coffee_bench(init_tank_volume: Option<f64>) -> Result<SimInit, Box<dyn Error>> {
    Ok(coffee_bench(init_tank_volume)?.with_tickless_clock(AutoSystemClock::new()))
}

/// Real time coffee simulation bench with ticker.
pub fn rt_coffee_bench_ticker(init_tank_volume: Option<f64>) -> Result<SimInit, Box<dyn Error>> {
    Ok(coffee_bench(init_tank_volume)?.with_clock(
        AutoSystemClock::new(),
        PeriodicTicker::new(Duration::from_millis(100)),
    ))
}

pub fn types_bench(_cfg: complex_types::TestLoad) -> Result<SimInit, Box<dyn Error>> {
    let mut model = complex_types::MyModel::default();

    // Mailboxes.
    let model_mbox = Mailbox::new();
    let model_addr = model_mbox.address();

    let mut bench = SimInit::new();

    // Endpoints.

    let output = event_queue_endpoint(&mut bench, SinkState::Enabled, "output").unwrap();
    model.output.connect_sink(output);

    EventSource::new()
        .connect(complex_types::MyModel::my_input, &model_addr)
        .bind_endpoint(&mut bench, "input")
        .unwrap();

    // Assembly and initialization.
    Ok(bench.add_model(model, model_mbox, "model"))
}
