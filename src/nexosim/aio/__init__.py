"""Asyncio version of the simulation API.

This module defines an asynchronous version of the
[`Simulation`][nexosim.Simulation] class.

!!! example "Example usage"
    === "Client"
        ```py
        import asyncio
        from nexosim.aio import Simulation
        from nexosim.time import MonotonicTime, Duration
        from nexosim.exceptions import SimulationNotStartedError

        async def run():
            async with Simulation("0.0.0.0:41633") as sim:
                await sim.build()
                await sim.init()

                await sim.schedule_event(MonotonicTime(1), "input", 1)
                await sim.schedule_event(MonotonicTime(3), "input", 2)
                try:
                    await sim.step_until(Duration(5))
                except SimulationNotStartedError:
                    time = await sim.time()
                    print(f"Simulation halted at {time}")
                    print(await sim.try_read_events("output"))

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
        use std::error::Error;
        use std::time::Duration;

        use nexosim::time::{AutoSystemClock, PeriodicTicker};
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
            Ok(bench.add_model(model, mbox, "model").with_clock(
                AutoSystemClock::new(),
                PeriodicTicker::new(Duration::from_millis(10)),
            ))
        }

        fn main() {
            server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
        }
        ```
"""

from ._simulation import Simulation

__all__ = ["Simulation"]
