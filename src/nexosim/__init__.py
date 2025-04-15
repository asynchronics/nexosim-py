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
            sim.start()

            # Schedule an event on the "input" event source
            sim.schedule_event(Duration(1), "input", 1)

            # Advance the simulation to the next scheduled timestamp.
            sim.step()

            # Read a list of `OutputEvent` objects from the "output" event sink.
            outputs = sim.read_events("output", OutputEvent)
            print(outputs)

            # Advance the simulation by 3s and read the final simulation time.
            t = sim.step_until(Duration(3))

            print(t)
        ```
    === "Server"
        ```rust
        use serde::Serialize;

        use nexosim::model::Model;
        use nexosim::ports::{EventSource, EventBuffer, Output};
        use nexosim::registry::EndpointRegistry;
        use nexosim::simulation::{Mailbox, SimInit, Simulation, SimulationError};
        use nexosim::time::MonotonicTime;
        use nexosim::server;

        #[derive(Clone, Serialize)]
        pub(crate) struct OutputEvent {
            pub(crate) foo: u16,
            pub(crate) bar: String,
        }

        #[derive(Default)]
        pub(crate) struct MyModel {
            pub(crate) output: Output<OutputEvent>
        }

        impl MyModel {
            pub async fn my_input(&mut self, value: u16) {
                let event = OutputEvent{foo: value, bar: String::from("string")};
                self.output.send(event).await;
            }
        }

        impl Model for MyModel {}

        fn bench(_cfg: ()) -> Result<(Simulation, EndpointRegistry), SimulationError> {
            let mut model = MyModel::default();

            // Mailboxes.
            let model_mbox = Mailbox::new();
            let model_addr = model_mbox.address();

            // Endpoints.
            let mut registry = EndpointRegistry::new();

            let output = EventBuffer::new();
            model.output.connect_sink(&output);
            registry.add_event_sink(output, "output").unwrap();

            let mut input = EventSource::new();
            input.connect(MyModel::my_input, &model_addr);
            registry.add_event_source(input, "input").unwrap();

            // Assembly and initialization.
            let sim = SimInit::new()
                .add_model(model, model_mbox, "model")
                .init(MonotonicTime::EPOCH)?
                .0;

            Ok((sim, registry))
        }


        fn main() {
            server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
        }
        ```
"""

from ._simulation import EventKey, Simulation

__all__ = ["Simulation", "EventKey"]
