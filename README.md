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
Supported python versions: 3.11, 3.12, 3.13, 3.14

## Installation

To install the package, use pip:
```
pip install nexosim-py
```
<!-- index end -->

## Documentation

The latest documentation and the user guide can be found [here](https://nexosim-py.readthedocs.io/).

## Example

Given a server implementation:
<!-- example server start -->
```rust
use std::error::Error;

use nexosim::model::Model;
use nexosim::ports::{EventSource, Output, SinkState, event_queue_endpoint};
use nexosim::server;
use nexosim::simulation::{Mailbox, SimInit};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Default)]
pub(crate) struct AddOne {
    pub(crate) output: Output<u16>,
}

#[Model]
impl AddOne {
    pub async fn input(&mut self, value: u16) {
        self.output.send(value + 1).await;
    }
}

fn bench(_cfg: ()) -> Result<SimInit, Box<dyn Error>> {
    let mut model = AddOne::default();
    let model_mbox = Mailbox::new();

    let mut bench = SimInit::new();

    let output = event_queue_endpoint(&mut bench, SinkState::Enabled, "add_1_output")?;
    model.output.connect_sink(output);

    EventSource::new()
        .connect(AddOne::input, &model_mbox)
        .bind_endpoint(&mut bench, "add_1_input")?;

    Ok(bench.add_model(model, model_mbox, "Adder"))
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
    sim.build()
    sim.init()
    sim.process_event("add_1_input", 5)

    print(sim.try_read_events("add_1_output"))

# Prints out:
# [6]
```
<!-- example client end -->
