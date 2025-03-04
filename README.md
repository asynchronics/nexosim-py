<!-- index start -->
# NeXosimPy

NeXosimPy is the python interface for the [NeXosim](https://github.com/asynchronics/nexosim) simulation server.

The library's features include:

* an interface for controlling and monitoring simulations,
* communication with the server over HTTP or unix domain sockets,
* API for for using (de)serializing rust types,
* asyncio support.


## Installation

To install the package use pip:
```
pip install nexosim
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
pub(crate) struct MyModel {
    pub(crate) output: Output<u16>
}

impl MyModel {
    pub async fn my_input(&mut self, value: u16) {
        self.output.send(value).await;
    }
}

impl Model for MyModel {}

fn bench(_cfg: ()) -> Result<(Simulation, EndpointRegistry), SimulationError> {
    let mut model = MyModel::default();

    let model_mbox = Mailbox::new();
    let model_addr = model_mbox.address();

    let mut registry = EndpointRegistry::new();

    let output = EventBuffer::new();
    model.output.connect_sink(&output);
    registry.add_event_sink(output, "output").unwrap();

    let mut input = EventSource::new();
    input.connect(MyModel::my_input, &model_addr);
    registry.add_event_source(input, "input").unwrap();

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
<!-- example server end -->

You can interact with the simulation using this library like this:

<!-- example client start -->
```py
from nexosim import Simulation

with Simulation("0.0.0.0:41633") as sim:
    sim.start()
    sim.process_event("input", 5)

    print(sim.read_events("output"))

# Prints out:
# [5]

```
<!-- example client end -->