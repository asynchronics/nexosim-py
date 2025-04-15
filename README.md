<!-- index start -->
# NeXosim-py

NeXosim-py is a python interface for the [NeXosim](https://github.com/asynchronics/nexosim) simulation server.

The library provides:

* an interface to control and monitor simulations over HTTP/2 or unix
  domain sockets,
* an API for the (de)serialization of Rust types,
* `asyncio` support.

## Compatibility

The package is compatible with NeXosim 0.3.2 and later 0.3.x versions.

## Installation

To install the package, use pip:
```
pip install nexosim-py
```
<!-- index end -->

## Example

Given a server implementation:
<!-- example server start -->
```rust
use nexosim::model::Model;
use nexosim::ports::{EventSource, EventBuffer, Output};
use nexosim::registry::EndpointRegistry;
use nexosim::simulation::{Mailbox, SimInit, Simulation, SimulationError};
use nexosim::time::MonotonicTime;
use nexosim::server;

#[derive(Default)]
pub(crate) struct AddOne {
    pub(crate) output: Output<u16>
}

impl AddOne {
    pub async fn input(&mut self, value: u16) {
        self.output.send(value + 1).await;
    }
}

impl Model for AddOne {}

fn bench(_cfg: ()) -> Result<(Simulation, EndpointRegistry), SimulationError> {
    let mut model = AddOne::default();

    let model_mbox = Mailbox::new();
    let model_addr = model_mbox.address();

    let mut registry = EndpointRegistry::new();

    let output = EventBuffer::new();
    model.output.connect_sink(&output);
    registry.add_event_sink(output, "add_1_output").unwrap();

    let mut input = EventSource::new();
    input.connect(AddOne::input, &model_addr);
    registry.add_event_source(input, "add_1_input").unwrap();

    let sim = SimInit::new()
        .add_model(model, model_mbox, "Adder")
        .init(MonotonicTime::EPOCH)?
        .0;

    Ok((sim, registry))
}


fn main() {
    server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
}
```
<!-- example server end -->

You can interact with the simulation using this library like this:

<!-- example client start -->
```py
from nexosim import Simulation

with Simulation("0.0.0.0:41633") as sim:
    sim.start()
    sim.process_event("add_1_input", 5)

    print(sim.read_events("add_1_output"))

# Prints out:
# [6]
```
<!-- example client end -->