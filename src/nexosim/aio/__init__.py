"""Asyncio version of the simulation API.

This module defines an asynchronous version of the
[`Simulation`][nexosim.Simulation] class.

!!! example "Example usage"
    === "Client"
        ```py
        import asyncio
        from nexosim.aio import Simulation
        from nexosim.time import MonotonicTime, Duration
        from nexosim.exceptions import SimulationHaltedError

        async def run():
            async with Simulation("0.0.0.0:41633") as sim:
                await sim.start()

                await sim.schedule_event(MonotonicTime(1), "input", 1)
                await sim.schedule_event(MonotonicTime(3), "input", 2)
                try:
                    await sim.step_until(Duration(5))
                except SimulationHaltedError:
                    time = await sim.time()
                    print(f"Simulation halted at {time}")
                    print(await sim.read_events("output"))

        async def halt():
            async with Simulation("0.0.0.0:41633") as sim:
                await asyncio.sleep(2)
                await sim.halt()

        async def main():
            await asyncio.gather(run(), halt())

        asyncio.run(main())
        ```
    === "Server"
        ```rust
        use nexosim::model::Model;
        use nexosim::ports::{EventSource, EventBuffer, Output};
        use nexosim::registry::EndpointRegistry;
        use nexosim::simulation::{Mailbox, SimInit, Simulation, SimulationError};
        use nexosim::time::{MonotonicTime, AutoSystemClock};
        use nexosim::server;

        #[derive(Default)]
        pub(crate) struct MyModel {
            pub(crate) output: Output<OutputEvent>
        }

        impl MyModel {
            pub async fn my_input(&mut self, value: u16) {
                self.output.send(value).await;
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
                .set_clock(AutoSystemClock::new())
                .init(MonotonicTime::EPOCH)?
                .0;

            Ok((sim, registry))
        }


        fn main() {
            server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
        }
        ```
"""

from ._simulation import Simulation

__all__ = ["Simulation"]
