"""The root module.

This module defines the `Simulation` type, which acts as a front-end to a
NeXosim gRPC simulation server.

!!! example "Example usage"
    === "Client"
        ```py
        from dataclasses import dataclass
        from nexosim import Simulation
        from nexosim.time import Duration

        # We could read simulation events as dictionaries, but it is often more
        # convenient to use classes that mirror their Rust counterpart.
        @dataclass
        class OutputEvent:
            foo: int
            bar: str

        # Connect to a local server listening on the 41633 port.
        with Simulation(address='localhost:41633') as sim:

            # Initialize the simulation.
            sim.build()
            sim.init()

            # Schedule an event on the "input" event source
            sim.schedule_event(Duration(1), "input", 1)

            # Advance the simulation to the next scheduled timestamp.
            sim.step()

            # Read a list of `OutputEvent` objects from the "output" event sink.
            outputs = sim.try_read_events("output", OutputEvent)
            print(outputs)

            # Advance the simulation by 3s and read the final simulation time.
            t = sim.step_until(Duration(3))

            print(t)
        ```
    === "Server"
        ```rust
        use std::error::Error;

        use serde::{Deserialize, Serialize};

        use nexosim::model::Model;
        use nexosim::ports::{EventSource, Output, SinkState, event_queue_endpoint};
        use nexosim::simulation::{Mailbox, SimInit};
        use nexosim::{Message, server};

        #[derive(Clone, Message, Serialize, Deserialize)]
        pub(crate) struct OutputEvent {
            pub(crate) foo: u16,
            pub(crate) bar: String,
        }

        #[derive(Default, Serialize, Deserialize)]
        pub(crate) struct MyModel {
            pub(crate) output: Output<OutputEvent>,
        }

        #[Model]
        impl MyModel {
            pub async fn my_input(&mut self, value: u16) {
                let event = OutputEvent {
                    foo: value,
                    bar: String::from("string"),
                };
                self.output.send(event).await;
            }
        }

        fn bench(_cfg: ()) -> Result<SimInit, Box<dyn Error>> {
            let mut model = MyModel::default();
            let mbox = Mailbox::new();

            let mut bench = SimInit::new();

            let sink = event_queue_endpoint(&mut bench, SinkState::Enabled, "output")?;
            model.output.connect_sink(sink);

            EventSource::new()
                .connect(MyModel::my_input, &mbox)
                .bind_endpoint(&mut bench, "input")?;

            // Assembly.
            Ok(bench.add_model(model, mbox, "model"))
        }

        fn main() {
            server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
        }
        ```
"""

__all__ = ["Simulation", "EventKey", "time", "types", "exceptions"]

from . import exceptions, time, types
from ._simulation import EventKey, Simulation
