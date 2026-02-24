# 0.2.0

- Rename methods to match the simulator counterparts:
    - `start()` to `init()`
    - `step_unbounded()` to `run()`
    - `read_events()` to `try_read_events()`
    - `await_event()` to `read_event()`
    - `open_sink()` to `enable_sink()`
    - `close_sink()` to `disable_sink()`

- Add the `build()` and `init_and_run()` methods.

- Modify the `init()` method to allow setting initialization time. The bench config is no longer an `init` argument. Instead, the config is provided with the new `build()` method.

- Introduce methods to accommodate state serialization / deserialization functionality

- Add methods for bench schema retrieval functionality

- Accommodate event injection

# 0.1.0

Initial release