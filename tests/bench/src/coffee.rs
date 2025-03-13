//! Models for the coffee espresso machine example bench.

use std::time::Duration;

use serde::{Deserialize, Serialize};

use nexosim::model::{Context, InitializedModel, Model};
use nexosim::ports::Output;
use nexosim::simulation::ActionKey;
use nexosim::time::MonotonicTime;

/// Water pump.
pub(crate) struct Pump {
    /// Actual volumetric flow rate [m³·s⁻¹] -- output port.
    pub(crate) flow_rate: Output<f64>,

    /// Nominal volumetric flow rate in operation [m³·s⁻¹]  -- constant.
    nominal_flow_rate: f64,
}

impl Pump {
    /// Creates a pump with the specified nominal flow rate [m³·s⁻¹].
    pub(crate) fn new(nominal_flow_rate: f64) -> Self {
        Self {
            nominal_flow_rate,
            flow_rate: Output::default(),
        }
    }

    /// Main ON/OFF command -- input port.
    pub(crate) async fn command(&mut self, cmd: PumpCommand) {
        let flow_rate = match cmd {
            PumpCommand::On => self.nominal_flow_rate,
            PumpCommand::Off => 0.0,
        };

        self.flow_rate.send(flow_rate).await;
    }
}

impl Model for Pump {}

/// Espresso machine controller.
pub(crate) struct Controller {
    /// Pump command -- output port.
    pub(crate) pump_cmd: Output<PumpCommand>,

    /// Brew time setting [s] -- internal state.
    brew_time: Duration,
    /// Current water sense state.
    water_sense: WaterSenseState,
    /// Event key, which if present indicates that the machine is currently
    /// brewing -- internal state.
    stop_brew_key: Option<ActionKey>,
}

impl Controller {
    /// Default brew time [s].
    const DEFAULT_BREW_TIME: Duration = Duration::new(25, 0);

    /// Creates an espresso machine controller.
    pub(crate) fn new() -> Self {
        Self {
            brew_time: Self::DEFAULT_BREW_TIME,
            pump_cmd: Output::default(),
            stop_brew_key: None,
            water_sense: WaterSenseState::Empty, // will be overridden during init
        }
    }

    /// Signals a change in the water sensing state -- input port.
    pub(crate) async fn water_sense(&mut self, state: WaterSenseState) {
        // Check if the tank just got empty.
        if state == WaterSenseState::Empty && self.water_sense == WaterSenseState::NotEmpty {
            // If a brew was ongoing, we must cancel it.
            if let Some(key) = self.stop_brew_key.take() {
                key.cancel();
                self.pump_cmd.send(PumpCommand::Off).await;
            }
        }

        self.water_sense = state;
    }

    /// Sets the timing for the next brews [s] -- input port.
    pub(crate) async fn brew_time(&mut self, brew_time: Duration) {
        // Panic if the duration is null.
        assert!(!brew_time.is_zero());

        self.brew_time = brew_time;
    }

    /// Starts brewing or cancels the current brew -- input port.
    pub(crate) async fn brew_cmd(&mut self, _: (), context: &mut Context<Self>) {
        // If a brew was ongoing, sending the brew command is interpreted as a
        // request to cancel it.
        if let Some(key) = self.stop_brew_key.take() {
            self.pump_cmd.send(PumpCommand::Off).await;

            // Abort the scheduled call to `stop_brew()`.
            key.cancel();

            return;
        }

        // If there is no water, do nothing.
        if self.water_sense == WaterSenseState::Empty {
            return;
        }

        // Schedule the `stop_brew()` method and turn on the pump.
        self.stop_brew_key = Some(
            context
                .schedule_keyed_event(self.brew_time, Self::stop_brew, ())
                .unwrap(),
        );
        self.pump_cmd.send(PumpCommand::On).await;
    }

    /// Stops brewing.
    async fn stop_brew(&mut self) {
        if self.stop_brew_key.take().is_some() {
            self.pump_cmd.send(PumpCommand::Off).await;
        }
    }
}

impl Model for Controller {}

/// ON/OFF pump command.
#[derive(Copy, Clone, Deserialize, Eq, PartialEq, Serialize)]
pub(crate) enum PumpCommand {
    On,
    Off,
}

/// Water tank.
pub(crate) struct Tank {
    /// Water sensor -- output port.
    pub(crate) water_sense: Output<WaterSenseState>,

    /// Volume of water [m³] -- internal state.
    volume: f64,
    /// State that exists when the mass flow rate is non-zero -- internal state.
    dynamic_state: Option<TankDynamicState>,
}
impl Tank {
    /// Creates a new tank with the specified amount of water [m³].
    ///
    /// The initial flow rate is assumed to be zero.
    pub(crate) fn new(water_volume: f64) -> Self {
        assert!(water_volume >= 0.0);

        Self {
            volume: water_volume,
            dynamic_state: None,
            water_sense: Output::default(),
        }
    }

    /// Water volume added [m³] -- input port.
    pub(crate) async fn fill(&mut self, added_volume: f64, context: &mut Context<Self>) {
        // Ignore zero and negative values. We could also impose a maximum based
        // on tank capacity.
        if added_volume <= 0.0 {
            return;
        }
        let was_empty = self.volume == 0.0;

        // Account for the added water.
        self.volume += added_volume;

        // If the current flow rate is non-zero, compute the current volume and
        // schedule a new update.
        if let Some(state) = self.dynamic_state.take() {
            // Abort the scheduled call to `set_empty()`.
            state.set_empty_key.cancel();

            // Update the volume, saturating at 0 in case of rounding errors.
            let time = context.time();
            let elapsed_time = time.duration_since(state.last_volume_update).as_secs_f64();
            self.volume = (self.volume - state.flow_rate * elapsed_time).max(0.0);

            self.schedule_empty(state.flow_rate, time, context).await;

            // There is no need to broadcast the state of the water sense since
            // it could not be previously `Empty` (otherwise the dynamic state
            // would not exist).
            return;
        }

        if was_empty {
            self.water_sense.send(WaterSenseState::NotEmpty).await;
        }
    }

    /// Flow rate [m³·s⁻¹] -- input port.
    ///
    /// # Panics
    ///
    /// This method will panic if the flow rate is negative.
    pub(crate) async fn set_flow_rate(&mut self, flow_rate: f64, context: &mut Context<Self>) {
        assert!(flow_rate >= 0.0);

        let time = context.time();

        // If the flow rate was non-zero up to now, update the volume.
        if let Some(state) = self.dynamic_state.take() {
            // Abort the scheduled call to `set_empty()`.
            state.set_empty_key.cancel();

            // Update the volume, saturating at 0 in case of rounding errors.
            let elapsed_time = time.duration_since(state.last_volume_update).as_secs_f64();
            self.volume = (self.volume - state.flow_rate * elapsed_time).max(0.0);
        }

        self.schedule_empty(flow_rate, time, context).await;
    }

    /// Schedules a callback for when the tank becomes empty.
    ///
    /// Pre-conditions:
    /// - `flow_rate` cannot be negative.
    /// - `self.volume` should be up to date,
    /// - `self.dynamic_state` should be `None`.
    async fn schedule_empty(
        &mut self,
        flow_rate: f64,
        time: MonotonicTime,
        context: &Context<Self>,
    ) {
        // Determine when the tank will be empty at the current flow rate.
        let duration_until_empty = if self.volume == 0.0 {
            0.0
        } else {
            self.volume / flow_rate
        };
        if duration_until_empty.is_infinite() {
            // The flow rate is zero or very close to zero, so there is not
            // need to plan an update since the tank will never become
            // empty.
            return;
        }
        let duration_until_empty = Duration::from_secs_f64(duration_until_empty);

        // Schedule the next update.
        match context.schedule_keyed_event(duration_until_empty, Self::set_empty, ()) {
            Ok(set_empty_key) => {
                let state = TankDynamicState {
                    last_volume_update: time,
                    set_empty_key,
                    flow_rate,
                };
                self.dynamic_state = Some(state);
            }
            Err(_) => {
                // The duration was null so the tank is already empty.
                self.volume = 0.0;
                self.water_sense.send(WaterSenseState::Empty).await;
            }
        }
    }

    /// Updates the state of the tank to indicate that there is no more water.
    async fn set_empty(&mut self) {
        self.volume = 0.0;
        self.dynamic_state = None;
        self.water_sense.send(WaterSenseState::Empty).await;
    }
}

impl Model for Tank {
    /// Broadcasts the initial state of the water sense.
    async fn init(mut self, _: &mut Context<Self>) -> InitializedModel<Self> {
        self.water_sense
            .send(if self.volume == 0.0 {
                WaterSenseState::Empty
            } else {
                WaterSenseState::NotEmpty
            })
            .await;

        self.into()
    }
}

/// Dynamic state of the tank that exists when and only when the mass flow rate
/// is non-zero.
struct TankDynamicState {
    last_volume_update: MonotonicTime,
    set_empty_key: ActionKey,
    flow_rate: f64,
}

/// Water level in the tank.
#[derive(Copy, Clone, Deserialize, Eq, PartialEq, Serialize)]
pub(crate) enum WaterSenseState {
    Empty,
    NotEmpty,
}
