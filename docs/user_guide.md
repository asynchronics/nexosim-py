---
hide:
    - navigation
---

## Before you start

NeXosim-py provides both a [conventional API](reference/mod_root.md) and an
[asynchronous API](reference/mod_aio.md).

The asynchronous API makes it possible to concurrently advance simulation time,
schedule events and monitor simulation outputs.

Because the asynchronous API faithfully reflects the conventional API, however,
most examples in this guide use the conventional API. An example of concurrent
simulation management leveraging the asynchronous API is provided in a
[dedicated section](#asyncio-api).


## Setting up the simulation

The connection with the server is established through instantiation of a
[`Simulation`][nexosim.Simulation] object.

The client can communicate with the server over either a local Unix Domain
Socket or an HTTP/2 connection, depending on how the server is set up.

To connect over a unix socket the `address` provided to the
[`Simulation`][nexosim.Simulation] constructor should be the socket path
prefixed with the `unix:` scheme. The server should be started with the
`run_local` function.

=== "Client"
    ```python
    from nexosim import Simulation

    with Simulation("unix:/tmp/nexo") as sim:
        # ...
    ```
=== "Server"
    ```rust
    server::run_local(bench, "/tmp/nexo");
    ```

For a regular remote HTTP connection the address should omit the url scheme and
the server should be started using the `run` function.

=== "Client"
    ```python
    from nexosim import Simulation

    with Simulation("0.0.0.0:41633") as sim:
        # ...
    ```
=== "Server"
    ```rust
    server::run(bench, "0.0.0.0:41633".parse().unwrap());
    ```

### Starting the simulation

Before the server can run the simulation, the simulation must first be built
and initialized. The simulation is built using the
[`build()`][nexosim.Simulation.build] method. This constructs the bench,
finalizing its topology.
Attempting to send a request before the simulation is built will raise a
[`SimulationNotBuiltError`][nexosim.exceptions.SimulationNotBuiltError].

After the bench is built, the simulation can be initialized with the
[`init()`][nexosim.Simulation.init] method. During initialization the start time
is set, defaulting to 1970-01-01 00:00:00 TAI.

The [`build()`][nexosim.Simulation.build] method accepts a configuration object
as an argument that can be used in the bench builder function.

=== "Client"
    ```python
    from nexosim import Simulation

    with Simulation("0.0.0.0:41633") as sim:
            sim.build(123)
            sim.init()
            print(sim.process_query("replier"))

        # Prints:
        # [123]
    ```
=== "Server"
    ```rust
    use std::error::Error;

    use nexosim::model::Model;
    use nexosim::ports::QuerySource;
    use nexosim::server;
    use nexosim::simulation::{Mailbox, SimInit};
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize, Default)]
    pub(crate) struct MyModel {
        value: u16,
    }

    #[Model]
    impl MyModel {
        pub async fn my_replier(&mut self) -> u16 {
            self.value
        }

        pub(crate) fn new(value: u16) -> Self {
            Self { value }
        }
    }

    fn bench(cfg: u16) -> Result<SimInit, Box<dyn Error>> {
        // Pass the configuration object to the model constructor.
        let model = MyModel::new(cfg);

        // Create a mailbox for the model.
        let model_mbox = Mailbox::new();

        let mut bench = SimInit::new();

        QuerySource::new()
            .connect(MyModel::my_replier, &model_mbox)
            .bind_endpoint(&mut bench, "replier")?;

        Ok(bench.add_model(model, model_mbox, "model"))
    }

    fn main() {
        server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
    }
    ```

The configuration object can be any serializable type:

=== "Client"
    ```python
    from nexosim import Simulation
    from dataclasses import dataclass

    @dataclass
    class ModelConfig:
        foo: int
        bar: str

    with Simulation("0.0.0.0:41633") as sim:
        sim.build(ModelConfig(123, "string"))
        sim.init()
        print(sim.process_query("replier"))

    # Prints:
    # ['string']
    ```
=== "Server"
    ```rust
    use std::error::Error;

    use nexosim::model::Model;
    use nexosim::ports::QuerySource;
    use nexosim::server;
    use nexosim::simulation::{Mailbox, SimInit};
    use serde::{Deserialize, Serialize};

    #[derive(Deserialize)]
    struct ModelConfig {
        foo: u16,
        bar: String,
    }

    #[derive(Serialize, Deserialize, Default)]
    pub(crate) struct MyModel {
        foo: u16,
        bar: String,
    }

    #[Model]
    impl MyModel {
        pub async fn my_replier(&mut self) -> String {
            self.bar.clone()
        }

        pub(crate) fn new(cfg: ModelConfig) -> Self {
            let ModelConfig { foo, bar } = cfg;
            Self { foo, bar }
        }
    }

    fn bench(cfg: ModelConfig) -> Result<SimInit, Box<dyn Error>> {
        // Pass the configuration object to the model constructor.
        let model = MyModel::new(cfg);

        // Create a mailbox for the model.
        let model_mbox = Mailbox::new();

        let mut bench = SimInit::new();

        QuerySource::new()
            .connect(MyModel::my_replier, &model_mbox)
            .bind_endpoint(&mut bench, "replier")?;

        Ok(bench.add_model(model, model_mbox, "model"))
    }

    fn main() {
        server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
    }
    ```

If [`build()`][nexosim.Simulation.build] and then
[`init()`][nexosim.Simulation.init] is called again, the simulation is
reinitialized and its previous state is lost.

### Enabling and disabling sinks

The initial state of the simulation's individual sinks may be either enabled or
disabled, depending on the bench initializer. Disabled sinks do not receive new
events.

The [`enable_sink()`][nexosim.Simulation.enable_sink] and
[`disable_sink()`][nexosim.Simulation.disable_sink] methods can be used to
control the state of individual sinks.

```python
with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    sim.enable_sink("my_sink")
```

## Interacting with the simulation

Interacting with a running simulation for the most part involves:

* broadcasting events and queries to an `EventSource` or `QuerySource`
  respectively,
* scheduling events to occur at a later time,
* advancing the simulation time,
* reading events sent by the simulation to an `EventSink`.

### Processing events and queries

Events can be broadcast to an `EventSource` using the
[`process_event()`][nexosim.Simulation.process_event] method.

```python
with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    output = sim.process_event("my_input", 5)
```

To broadcast a query to a QuerySource use the
[`process_query()`][nexosim.Simulation.process_query] method. The type of the
returned value can be set using the `reply_type` parameter.

```python
with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    output = sim.process_query("my_replier", 5, reply_type=str)
    print(output)

# Prints out:
# ['5']
```

!!! note
    Both the [`process_event()`][nexosim.Simulation.process_event] and
    [`process_query()`][nexosim.Simulation.process_query] methods block
    until completion and do not affect the simulation time.

### Scheduling events

Events can be scheduled for a later simulation time with the
[`schedule_event()`][nexosim.Simulation.schedule_event] method. Use the `period`
argument to schedule a periodically recurring event.

To be able to cancel a scheduled event at a later time, the
[`schedule_event()`][nexosim.Simulation.schedule_event] method must be called
with `with_key = True`. The event can be then cancelled using the
[`cancel_event()`][nexosim.Simulation.cancel_event] method and the returned
event key.

```python
with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    event_key = sim.schedule_event(Duration(10), "my_event", with_key=True)
    sim.cancel_event(event_key)
```

The time at which an event is scheduled can be an absolute simulation time using
[`MonotonicTime`][nexosim.time.MonotonicTime] or relative to the current
simulation time using [`Duration`][nexosim.time.Duration].

### Injecting events

Injecting events is scheduling events to be processed at the nearest time
possible. This will be the time of the next tick (if the simulation was set up
with a ticker) or the time of the next scheduled event, whichever occurs first.

Events are injected using the [`inject_event()`][nexosim.Simulation.inject_event].

```python
with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    sim.inject_event("my_input", 5)
```

### Advancing the simulation

The current time of the simulation can be retrieved using the
[`time()`][nexosim.Simulation.time] method.

The simulation can be advanced to the time of the next scheduled events with the
[`step()`][nexosim.Simulation.step] method. All events scheduled for the same
time are processed as well. This method blocks until all the relevant events
are processed.

```python
from nexosim import Simulation
from nexosim.time import MonotonicTime

with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    sim.schedule_event(MonotonicTime(1), "input", 1)
    sim.step()
    print(sim.time())  # 1970-01-01 00:00:01
```

To advance the simulation to the specified time, processing all events scheduled
up to that time, use the [`step_until()`] [nexosim.Simulation.step_until]
method. This method blocks until all the relevant events are processed or, if
the simulation is synchronized with a `Clock`, until the specified simulation
time is reached. The time can be an absolute simulation time using
[`MonotonicTime`][nexosim.time.MonotonicTime] or relative to the current
simulation time using [`Duration`][nexosim.time.Duration].

```python
from nexosim import Simulation
from nexosim.time import MonotonicTime, Duration

with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    sim.step_until(MonotonicTime(1))
    sim.step_until(MonotonicTime(2))
    print(sim.time()) # 1970-01-01 00:00:02

    sim.step_until(Duration(2))
    print(sim.time()) # 1970-01-01 00:00:04
```

The [`run()`][nexosim.Simulation.run] method processes all
the scheduled events as if by calling the [`step()`][nexosim.Simulation.step]
method repeatedly. This method blocks until completed.

```python
from nexosim import Simulation
from nexosim.time import MonotonicTime

with Simulation("0.0.0.0:41633") as sim:
    sim.build()
    sim.init()
    sim.schedule_event(MonotonicTime(1), "input", 1)
    sim.schedule_event(MonotonicTime(3), "input", 1)
    sim.run()
    print(sim.time())  # 1970-01-01 00:00:03
```

The simulation can be stopped using the [`halt()`][nexosim.Simulation.halt]
method. After receiving a `halt` request, the simulation will stop at the next
attempt by the simulator to advance simulation time.

The next attempt to advance the simulation time, including if performed as part
of a concurrently executing `step_until()` and `run()` call, will
raise a [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError].

The following is an example using the asyncio API and a simulation bench
synchronized with the system clock:

=== "Client"
    ```python
    import asyncio
    from nexosim.aio import Simulation
    from nexosim.exceptions import SimulationNotStartedError
    from nexosim.time import MonotonicTime, Duration

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

    # Prints out:
    # Simulation halted at 1970-01-01 00:00:03
    # [1]
    ```
=== "Server"
    ```rust
    use std::error::Error;
    use std::time::Duration;

    use nexosim::model::Model;
    use nexosim::ports::{EventSource, Output, SinkState, event_queue_endpoint};
    use nexosim::server;
    use nexosim::simulation::{Mailbox, SimInit};
    use nexosim::time::{AutoSystemClock, PeriodicTicker};
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize, Default)]
    struct MyModel {
        output: Output<u16>,
    }

    #[Model]
    impl MyModel {
        pub async fn my_input(&mut self, value: u16) {
            self.output.send(value).await;
        }
    }

    fn bench(_: ()) -> Result<SimInit, Box<dyn Error>> {
        let mut model = MyModel::default();
        let model_mbox = Mailbox::new();

        let mut bench = SimInit::new();

        EventSource::new()
            .connect(MyModel::my_input, &model_mbox)
            .bind_endpoint(&mut bench, "input")?;

        let sink = event_queue_endpoint(&mut bench, SinkState::Enabled, "output")?;
        model.output.connect_sink(sink);

        Ok(bench.add_model(model, model_mbox, "model").with_clock(
            AutoSystemClock::new(),
            PeriodicTicker::new(Duration::from_millis(10)),
        ))
    }

    fn main() {
        server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
    }
    ```

In the above example the simulation is stopped after 2 seconds. After the first
event is processed the simulation time jumps to the time of the next event, but,
since the simulation is synchronized with a real-time clock, the simulation is
stopped before the next event can be processed.

!!!note
    For latency-sensitive simulations, concurrent
    [`Simulation.init_and_run`][nexosim.Simulation.init_and_run] or
    [`Simulation.restore_and_run`][nexosim.Simulation.restore_and_run] methods
    should be preferred over separate calls of
    [`Simulation.init`][nexosim.Simulation.init] or
    [`Simulation.restore`][nexosim.Simulation.restore], and
    [`Simulation.run`][nexosim.Simulation.run] to mitigate the risk of loss of
    synchronization between the invocations.

### Reading events

Events sent to sinks can be read using the
[`try_read_events()`][nexosim.Simulation.try_read_events] method. The `event_type`
parameter controls the type the read event will be mapped to.

=== "Client"
    ```py
    from dataclasses import dataclass
    from nexosim import Simulation

    @dataclass
    class OutputEvent:
        foo: int
        bar: str

    with Simulation(address='localhost:41633') as sim:
        sim.build()
        sim.init()

        sim.process_event("input", 1)
        outputs = sim.try_read_events("output", OutputEvent)
        print(f"Events mapped to the OutputEvent class: {outputs}")

        sim.process_event("input", 1)
        outputs = sim.try_read_events("output")
        print(f"Events without specifying the reply type: {outputs}")

    # Prints out:
    # Events mapped to the OutputEvent class: [OutputEvent(foo=1, bar='string')]
    # Events without specifying the reply type: [{'foo': 1, 'bar': 'string'}]
    ```
=== "Server"
    ```rust
    use std::error::Error;

    use nexosim::model::Model;
    use nexosim::ports::{EventSource, Output, SinkState, event_queue_endpoint};
    use nexosim::simulation::{Mailbox, SimInit};
    use nexosim::{Message, server};
    use serde::{Deserialize, Serialize};

    #[derive(Clone, Serialize, Message)]
    pub(crate) struct OutputEvent {
        pub(crate) foo: u16,
        pub(crate) bar: String,
    }

    #[derive(Serialize, Deserialize, Default)]
    struct MyModel {
        output: Output<OutputEvent>,
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

    fn bench(_: ()) -> Result<SimInit, Box<dyn Error>> {
        let mut model = MyModel::default();
        let model_mbox = Mailbox::new();

        let mut bench = SimInit::new();

        EventSource::new()
            .connect(MyModel::my_input, &model_mbox)
            .bind_endpoint(&mut bench, "input")?;

        let sink = event_queue_endpoint(&mut bench, SinkState::Enabled, "output")?;
        model.output.connect_sink(sink);

        Ok(bench.add_model(model, model_mbox, "model"))
    }

    fn main() {
        server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
    }
    ```

Events can be awaited using the [`read_event()`][nexosim.Simulation.read_event]
method. The method will block until an event is received or the call times out.

```py
from dataclasses import dataclass
from nexosim import Simulation
from nexosim.time import Duration

@dataclass
class OutputEvent:
    foo: int
    bar: str

with Simulation(address='localhost:41633') as sim:
    sim.build()
    sim.init()

    sim.process_event("input", 1)
    output = sim.read_event("output", Duration(1), OutputEvent)
    print(output)

# Prints out:
# OutputEvent(foo=1, bar='string')
```

The `EventSink` must be [enabled](#enabling-and-disabling-sinks) to receive events
from the simulation.

## Saving and restoring simulation state

The current state of the simulation can be serialized using the
[`save()`][nexosim.Simulation.save] method, and later restored using
the [`restore()`][nexosim.Simulation.restore] method.

!!! note
    The simulation state does not include events already sent to a sink.

Before the state can be restored the simulation must be rebuilt.

=== "Client"
    ```python
    from nexosim import Simulation

    with Simulation(address='localhost:41633') as sim:
        sim.build()
        sim.init()

        sim.process_event("input")

        state = sim.save()
        sim.terminate()
        sim.build()
        sim.restore(state)

        sim.process_event("input")
        outputs = sim.try_read_events("output")
        print(outputs)

    # Prints:
    # [2]
    ```
=== "Server"
    ```rust
    use std::error::Error;

    use nexosim::model::Model;
    use nexosim::ports::{EventSource, Output, SinkState, event_queue_endpoint};
    use nexosim::server;
    use nexosim::simulation::{Mailbox, SimInit};
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize, Default)]
    struct MyModel {
        output: Output<u16>,
        count: u16,
    }

    #[Model]
    impl MyModel {
        pub async fn my_input(&mut self) {
            self.count += 1;
            self.output.send(self.count).await;
        }
    }

    fn bench(_: ()) -> Result<SimInit, Box<dyn Error>> {
        let mut model = MyModel::default();
        let model_mbox = Mailbox::new();

        let mut bench = SimInit::new();

        EventSource::new()
            .connect(MyModel::my_input, &model_mbox)
            .bind_endpoint(&mut bench, "input")?;

        let sink = event_queue_endpoint(&mut bench, SinkState::Enabled, "output")?;
        model.output.connect_sink(sink);

        Ok(bench.add_model(model, model_mbox, "model"))
    }

    fn main() {
        server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
    }
    ```

## Serializable types

The NeXosim-Py package provides a convenient API for constructing Python
counterparts to rust's `struct` and `enum` types that can be (de)serialized as
events, requests, or replies within a [`Simulation`][nexosim.Simulation].

A detailed description of how to use serializable types can be found in the
[types module reference][nexosim.types].

## Asyncio API

The [aio][nexosim.aio] module provides the asynchronous
[`Simulation`][nexosim.aio.Simulation] class, with an interface mirroring that
of the regular [`Simulation`][nexosim.Simulation] class. The asynchronous
version can be used with `asyncio` to perform concurrent calls to the
simulation.

!!! note
    Note that `step*` and `process*` requests are mutually blocking when using
    the asynchronous [`Simulation`][nexosim.aio.Simulation].

Here's an example usage of the `aio` API with concurrent requests and a simulation
synchronized with the system clock:

=== "Client"
    ```python
    import asyncio
    from nexosim.aio import Simulation
    from nexosim.time import MonotonicTime, Duration

    async def run():
        async with Simulation("0.0.0.0:41633") as sim:
            await sim.build()
            await sim.init()

            await sim.schedule_event(MonotonicTime(1), "input", 1)
            await sim.schedule_event(MonotonicTime(3), "input", 2)

            print("step_until started")
            await sim.step_until(Duration(4))
            print("step_until finished")


    async def read():
        async with Simulation("0.0.0.0:41633") as sim:
            await asyncio.sleep(2)
            print(await sim.try_read_events("output"))
            await asyncio.sleep(3)
            print(await sim.try_read_events("output"))

    async def main():
        await asyncio.gather(run(), read())

    asyncio.run(main())

    # Prints out
    # step_until started
    # [1]
    # step_until finished
    # [2]
    ```
=== "Server"
    ```rust
    use std::error::Error;
    use std::time::Duration;

    use nexosim::model::Model;
    use nexosim::ports::{EventSource, Output, SinkState, event_queue_endpoint};
    use nexosim::server;
    use nexosim::simulation::{Mailbox, SimInit};
    use nexosim::time::{AutoSystemClock, PeriodicTicker};
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize, Default)]
    struct MyModel {
        output: Output<u16>,
    }

    #[Model]
    impl MyModel {
        pub async fn my_input(&mut self, value: u16) {
            self.output.send(value).await;
        }
    }

    fn bench(_: ()) -> Result<SimInit, Box<dyn Error>> {
        let mut model = MyModel::default();
        let model_mbox = Mailbox::new();

        let mut bench = SimInit::new();

        EventSource::new()
            .connect(MyModel::my_input, &model_mbox)
            .bind_endpoint(&mut bench, "input")?;

        let sink = event_queue_endpoint(&mut bench, SinkState::Enabled, "output")?;
        model.output.connect_sink(sink);

        Ok(bench.add_model(model, model_mbox, "model").with_clock(
            AutoSystemClock::new(),
            PeriodicTicker::new(Duration::from_millis(10)),
        ))
    }

    fn main() {
        server::run(bench, "0.0.0.0:41633".parse().unwrap()).unwrap();
    }
    ```

## Bench schema

[`Simulation`][nexosim.Simulation] has methods for retrieving information about
endpoints exposed by the simulation server. These include:

- [`list_event_sources()`][nexosim.Simulation.list_event_sources]
- [`get_event_source_schemas()`][nexosim.Simulation.get_event_source_schemas]
- [`list_query_sources()`][nexosim.Simulation.list_query_sources]
- [`get_query_source_schemas()`][nexosim.Simulation.get_query_source_schemas]
- [`list_event_sinks()`][nexosim.Simulation.list_event_sinks]
- [`get_event_sink_schemas()`][nexosim.Simulation.get_event_sink_schemas]

The simulation does not have to be initialized for these methods to be used.