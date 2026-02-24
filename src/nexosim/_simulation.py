import inspect
import json
import typing

import cbor2
import grpc  # type: ignore
from google.protobuf.duration_pb2 import Duration as PbDuration
from google.protobuf.timestamp_pb2 import Timestamp as PbTimestamp

from . import exceptions
from ._config import cbor2_converter
from ._proto import simulation_pb2, simulation_pb2_grpc
from ._proto.simulation_pb2 import EventKey as PbEventKey
from .time import Duration, MonotonicTime

T = typing.TypeVar("T")

if typing.TYPE_CHECKING:
    from typing_extensions import TypeForm
else:
    from typing import Type as TypeForm


class EventKey:
    """A handle to a scheduled event.

    Event keys are opaque objects. They are meant to be created by the
    [`Simulation.schedule_event`][nexosim.Simulation.schedule_event] method
    and consumed by the
    [`Simulation.cancel_event`][nexosim.Simulation.cancel_event] method.
    """

    __slots__ = "_key"

    _key: PbEventKey


class Simulation:
    """A handle to the remote simulation bench.

    Creates a handle to the remote simulation bench running at the
    specified address.

    A gRPC NeXosim server must be running at the specified address.

    For a regular remote gRPC connection via HTTP/2, the address should omit the
    URL scheme and the double-slash prefix (e.g. `localhost:41633`).

    For a local Unix Domain Socket connection, the address is the socket path
    prefixed with the `unix:` scheme (e.g. `unix:relative/path/to/socket`,
    `unix:/absolute/path/to/socket` or alternatively
    `unix:///absolute/path/to/socket`).

    `Simulation` is a context manager. If not used in a `with` statement,
    the `close()` method should be called after use.

    Args:
        address: the address at which the NeXosim server is running.
    """

    def __init__(self, address: str):
        # Work around gRPC's weird behavior (a.k.a. bug) with Unix Domain
        # Sockets.
        #
        # See https://github.com/grpc/grpc/issues/34305
        options = (
            (("grpc.default_authority", "localhost"),)
            if address.lstrip().startswith("unix:")
            else None
        )

        self._channel = grpc.insecure_channel(address, options)  # type: ignore
        self._stub = simulation_pb2_grpc.SimulationStub(self._channel)

    def __enter__(self) -> typing.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Closes the gRPC channel."""
        self._channel.close()

    def build(self, cfg: typing.Any = None) -> None:
        """
        Builds a simulation bench.

        Args:
            cfg: A bench configuration object which can be
                serialized/deserialized to the expected bench configuration
                type. The `None` default is appropriate if the bench builder
                expects the Rust type `()`, accepts an `Option::None`.

            Raises:
                exceptions.SimulationError: One of the exceptions derived from
                    [`SimulationError`][nexosim.exceptions.SimulationError] may be
                    raised, such as:

                    - [`BenchPanicError`][nexosim.exceptions.BenchPanicError]
                    - [`BenchError`][nexosim.exceptions.BenchError]
                    - [`DuplicateEventSourceError`][nexosim.exceptions.DuplicateEventSourceError]
                    - [`DuplicateQuerySourceError`][nexosim.exceptions.DuplicateQuerySourceError]
                    - [`DuplicateEventSinkError`][nexosim.exceptions.DuplicateEventSinkError]
                    - [`InvalidBenchConfigError`][nexosim.exceptions.InvalidBenchConfigError]
        """
        request = simulation_pb2.BuildRequest(cfg=cbor2_converter.dumps(cfg))
        reply = self._stub.Build(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def init(self, time: MonotonicTime = MonotonicTime.EPOCH) -> None:
        """
        Initializes a simulation bench.

        The simulation must be built using the [`Simulation.build`][nexosim.Simulation.build]
        method before it can be initialized.

        If a simulation bench is already running, it is replaced by the newly
        initialized bench. In such case, events that have not yet been retrieved
        from the sinks will be lost and the sinks are reset to their default
        enabled/disabled state.

        Args:
            time: The time at which the simulation will be initialized.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]

        """

        request = simulation_pb2.InitRequest(
            time=PbTimestamp(seconds=time.secs, nanos=time.nanos),
        )
        reply = self._stub.Init(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def init_and_run(self, time: MonotonicTime = MonotonicTime.EPOCH) -> MonotonicTime:
        """
        Initializes and runs a simulation.

        This is functionally equivalent to calling [`Simulation.init`][nexosim.Simulation.init] followed by [`Simulation.run`][nexosim.Simulation.run], but is
        implemented as a single gRPC request. This method should be preferred in
        latency-sensitive simulations to mitigate the risk of loss of
        synchronization between the invocations of [`Simulation.init`][nexosim.Simulation.init]
        and [`Simulation.run`][nexosim.Simulation.run].

        The simulation must be built using the [`Simulation.build`][nexosim.Simulation.build]
        method before it can be initialized.

        If a simulation bench is already running, it is replaced by the newly
        initialized bench in the restored state. In such case, events that have
        not yet been retrieved from the sinks will be lost and the sinks are
        reset to their default enabled/disabled state.

        Args:
            time: The time at which the simulation will be initialized.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
        """

        request = simulation_pb2.InitAndRunRequest(
            time=PbTimestamp(seconds=time.secs, nanos=time.nanos),
        )
        reply = self._stub.InitAndRun(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def terminate(self) -> None:
        """
        Terminates a simulation.
        """
        request = simulation_pb2.TerminateRequest()
        reply = self._stub.Terminate(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def halt(self) -> None:
        """
        Requests the simulation to stop at the earliest opportunity.

        If a stepping method such as
        [`Simulation.step`][nexosim.aio.Simulation.step] or
        [`Simulation.run`][nexosim.aio.Simulation.run] is concurrently
        being executed, this will cause such method to raise a
        [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        before it steps to next scheduler deadline or simulation tick.

        Otherwise, this will cause the next call to a `Simulation.step_*` or
        `Simulation.process_*` method to return immediately with
        [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError].

        Once halted, the simulation can be resumed with another stepping method
        or a `Simulation.process_*` call.

        Note that the request will only become effective on the next attempt by
        the simulator to advance the simulation time.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        request = simulation_pb2.HaltRequest()
        reply = self._stub.Halt(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def save(self) -> bytes:
        """
        Saves and returns the current simulation state in a serialized form.

        Returns:
            The serialized simulation state.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
                - [`SaveError`][nexosim.exceptions.SaveError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        request = simulation_pb2.SaveRequest()
        reply = self._stub.Save(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return reply.state

    def restore(self, state: bytes) -> None:
        """
        Restores the simulation from a serialized state.

        The simulation must be built using the [`Simulation.build`][nexosim.Simulation.build]
        method before it can be initialized.

        If a simulation bench is already running, it is replaced by the newly
        initialized bench in the restored state. In such case, events that have
        not yet been retrieved from the sinks will be lost and the sinks are
        reset to their default enabled/disabled state.

        Args:
            state: The serialized state of the bench.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
                - [`RestoreError`][nexosim.exceptions.RestoreError]

        """
        request = simulation_pb2.RestoreRequest(state=state)
        reply = self._stub.Restore(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def restore_and_run(self, state: bytes) -> MonotonicTime:
        """
        Restores the simulation from a serialized state and runs the simulation.

        This is functionally equivalent to calling
        [`Simulation.restore`][nexosim.Simulation.restore] followed by
        [`Simulation.run`][nexosim.Simulation.run], but is
        implemented as a single gRPC request. This method should be preferred in
        latency-sensitive simulations to mitigate the risk of loss of
        synchronization between the invocations of
        [`Simulation.restore`][nexosim.Simulation.restore] and
        [`Simulation.run`][nexosim.Simulation.run].

        The simulation must be built using the [`Simulation.build`][nexosim.Simulation.build]
        method before it can be initialized.

        If a simulation bench is already running, it is replaced by the newly
        initialized bench in the restored state. In such case, events that have
        not yet been retrieved from the sinks will be lost and the sinks are
        reset to their default enabled/disabled state.

        Args:
            state: The serialized state of the bench.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
                - [`RestoreError`][nexosim.exceptions.RestoreError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
        """

        request = simulation_pb2.RestoreAndRunRequest(state=state)
        reply = self._stub.RestoreAndRun(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def time(self) -> MonotonicTime:
        """Returns the current simulation time.

        Returns:
            The current simulation time.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        request = simulation_pb2.TimeRequest()
        reply = self._stub.Time(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def step(self) -> MonotonicTime:
        """Advances simulation time to that of the next scheduled event,
        processing that event as well as all other events scheduled for the same
        time.

        This method blocks until all newly processed events have completed and
        returns the final simulation time.

        Returns:
            The final simulation time.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
        """

        request = simulation_pb2.StepRequest()
        reply = self._stub.Step(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def run(self) -> MonotonicTime:
        """Iteratively advances the simulation time until the simulation end, as
        if by calling [Simulation.step][nexosim.Simulation.step] repeatedly.

        The request blocks until all scheduled events are processed or
        the simulation is halted.

        The simulation time upon completion is returned.

        Returns:
            The final simulation time.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]

        """

        request = simulation_pb2.RunRequest()
        reply = self._stub.Run(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def step_until(self, deadline: MonotonicTime | Duration) -> MonotonicTime:
        """Iteratively advances the simulation time until the specified
        deadline, as if by calling [Simulation.step][nexosim.Simulation.step]
        repeatedly.

        This method blocks until all events scheduled up to the specified target
        time have completed. The simulation time upon completion is returned and
        is always equal to the specified target time, whether or not an event
        was scheduled for that time.

        Args:
            deadline: The target time, specified either as an absolute time
                reference or as a positive duration relative to the current
                simulation time.

        Returns:
            The final simulation time.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidDeadlineError`][nexosim.exceptions.InvalidDeadlineError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
        """

        kwargs = {}

        if isinstance(deadline, MonotonicTime):
            kwargs["time"] = PbTimestamp(seconds=deadline.secs, nanos=deadline.nanos)
        else:
            kwargs["duration"] = PbDuration(seconds=deadline.secs, nanos=deadline.nanos)

        request = simulation_pb2.StepUntilRequest(**kwargs)  # type: ignore
        reply = self._stub.StepUntil(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def list_event_sources(self) -> list[list[str]]:
        """Lists available event sources.

        Returns:
            A list of event source names.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
        """
        request = simulation_pb2.ListEventSourcesRequest()
        reply = self._stub.ListEventSources(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return [list(path.segments) for path in reply.sources]

    def get_event_source_schemas(
        self, sources: typing.Iterable[str | typing.Iterable[str]]
    ) -> dict[tuple[str], dict]:
        """Retrieves the schema of the event sources specified in `sources`.

        This method requires the simulation bench to be built with the
        [`Simulation.build`][nexosim.Simulation.build] method beforehand, but
        can be used without initialization.

        Args:
            source_names: The names of the event sources.

        Returns:
            A mapping of event source schemas to their names.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
        """
        request = simulation_pb2.GetEventSourceSchemasRequest(
            sources=[
                simulation_pb2.Path(segments=path)
                if not isinstance(path, str)
                else simulation_pb2.Path(segments=(path,))
                for path in sources
            ]
        )
        reply = self._stub.GetEventSourceSchemas(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return {
            tuple(schema.source.segments): json.loads(schema.event)
            for schema in reply.schemas
            if schema.event
        }  # type: ignore

    def list_query_sources(self) -> list[list[str]]:
        """Lists available query sources.

        This method requires the simulation bench to be built with the
        [`Simulation.build`][nexosim.Simulation.build] method beforehand, but
        can be used without initialization.

        Returns:
            A list of query source names.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
        """
        request = simulation_pb2.ListQuerySourcesRequest()
        reply = self._stub.ListQuerySources(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return [list(path.segments) for path in reply.sources]

    def get_query_source_schemas(
        self, sources: typing.Iterable[str | typing.Iterable[str]]
    ) -> dict[str, dict]:
        """Retrieves the schema of the query sources specified in `sources`.

        This method requires the simulation bench to be built with the
        [`Simulation.build`][nexosim.Simulation.build] method beforehand, but
        can be used without initialization.

        Args:
            source_names: The names of the query sources.

        Returns:
            A mapping of query source schemas to their names.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
        """
        request = simulation_pb2.GetQuerySourceSchemasRequest(
            sources=[
                simulation_pb2.Path(segments=path)
                if not isinstance(path, str)
                else simulation_pb2.Path(segments=(path,))
                for path in sources
            ]
        )
        reply = self._stub.GetQuerySourceSchemas(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return {
            tuple(schema.source.segments): {
                "request": json.loads(schema.request),
                "reply": json.loads(schema.reply),
            }
            for schema in reply.schemas
        }  # type: ignore

    def list_event_sinks(self) -> list[list[str]]:
        """Lists available event sinks.

        This method requires the simulation bench to be built with the
        [`Simulation.build`][nexosim.Simulation.build] method beforehand, but
        can be used without initialization.

        Returns:
            A list of event sink names.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
        """
        request = simulation_pb2.ListEventSinksRequest()
        reply = self._stub.ListEventSinks(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return [list(path.segments) for path in reply.sinks]

    def get_event_sink_schemas(
        self, sinks: typing.Iterable[str | typing.Iterable[str]]
    ):
        #  -> dict[str, dict]:
        """Retrieves the schema of the event sinks specified in `sinks`.

        This method requires the simulation bench to be built with the
        [`Simulation.build`][nexosim.Simulation.build] method beforehand, but
        can be used without initialization.

        Args:
            sink_names: The names of the event sinks.

        Returns:
            A mapping of event sinks schemas to their names.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`BenchNotBuiltError`][nexosim.exceptions.BenchNotBuiltError]
        """
        request = simulation_pb2.GetEventSinkSchemasRequest(
            sinks=[
                simulation_pb2.Path(segments=path)
                if not isinstance(path, str)
                else simulation_pb2.Path(segments=(path,))
                for path in sinks
            ]
        )
        reply = self._stub.GetEventSinkSchemas(request)  # type: ignore

        if reply.HasField("error"):
            raise _to_error(reply.error)

        return {
            tuple(schema.sink.segments): json.loads(schema.event)
            for schema in reply.schemas
            if schema.event
        }  # type: ignore

    def inject_event(
        self, source: str | typing.Iterable[str], event: typing.Any = None
    ) -> None:
        """Injects an event to be processed as soon as possible.

        If a stepping method such as [Simulation.step][nexosim.Simulation.step]
        or [Simulation.run][nexosim.Simulation.run] is executed concurrently,
        the event will be processed at the deadline set by the scheduler event
        or simulation tick that directly follows the one that is being stepped
        into.

        If the event is injected while the simulation is at rest, the event will
        be processed at the lapse of the next simulation step (next scheduler
        event or simulation tick).


        Args:
            source: The path of the event source.

            event: an object that can be serialized/deserialized to the expected
                event type. The `None` default may be used if the Rust event
                type is `()` or `Option`.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`EventSourceNotFoundError`][nexosim.exceptions.EventSourceNotFoundError]
                - [`InvalidEventTypeError`][nexosim.exceptions.InvalidEventTypeError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
        """
        source = source if not isinstance(source, str) else (source,)
        request = simulation_pb2.InjectEventRequest(
            source=simulation_pb2.Path(segments=source),
            event=cbor2_converter.dumps(event),
        )
        reply = self._stub.InjectEvent(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    @typing.overload
    def schedule_event(
        self,
        deadline: MonotonicTime | Duration,
        source: str | typing.Iterable[str],
        event: object = None,
        period: None | Duration = None,
        with_key: typing.Literal[False] = False,
    ) -> None: ...

    @typing.overload
    def schedule_event(
        self,
        deadline: MonotonicTime | Duration,
        source: str | typing.Iterable[str],
        event: object,
        period: None | Duration,
        with_key: typing.Literal[True],
    ) -> EventKey: ...

    def schedule_event(
        self,
        deadline: MonotonicTime | Duration,
        source: str | typing.Iterable[str],
        event: object = None,
        period: None | Duration = None,
        with_key: bool = False,
    ) -> EventKey | None:
        """Schedules an event at a future time.

        Events scheduled for the same time and targeting the same model are
        guaranteed to be processed according to the scheduling order.

        Args:
            deadline: The target time, specified either as an absolute time
                set in the future of the current simulation time or as a strictly
                positive duration relative to the current simulation time.

            source: The path of the event source.

            event: an object that can be serialized/deserialized to the expected
                event type. The `None` default may be used if the Rust event
                type is `()` or `Option`.

            period: An optional, strictly positive duration expressing the
                repetition period of the event. If left to `None`, the event is
                scheduled only once. Otherwise, the first event is scheduled at
                the specified deadline and repeated periodically from then on
                until it is cancelled.

            with_key: Optionally requests an event key to be returned, which may
                be used to cancel the event with
                [`Simulation.cancel_event`][nexosim.Simulation.cancel_event].

        Returns:
            If `with_key` is set then a key for the scheduled event is returned.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidDeadlineError`][nexosim.exceptions.InvalidDeadlineError]
                - [`InvalidPeriodError`][nexosim.exceptions.InvalidPeriodError]
                - [`EventSourceNotFoundError`][nexosim.exceptions.EventSourceNotFoundError]
                - [`InvalidEventTypeError`][nexosim.exceptions.InvalidEventTypeError]
                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        kwargs = {}

        if isinstance(deadline, MonotonicTime):
            kwargs["time"] = PbTimestamp(seconds=deadline.secs, nanos=deadline.nanos)
        else:
            kwargs["duration"] = PbDuration(seconds=deadline.secs, nanos=deadline.nanos)

        source = source if not isinstance(source, str) else (source,)
        kwargs["source"] = simulation_pb2.Path(segments=source)

        if inspect.isclass(type(event)):
            event_bytes = cbor2_converter.dumps(event)
        else:
            event_bytes = cbor2.dumps(event)
        kwargs["event"] = event_bytes

        if period is not None:
            kwargs["period"] = PbDuration(seconds=period.secs, nanos=period.nanos)

        kwargs["with_key"] = with_key

        request = simulation_pb2.ScheduleEventRequest(**kwargs)
        reply = self._stub.ScheduleEvent(request)

        if reply.HasField("key"):
            key = EventKey()
            key._key = reply.key

            return key

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def cancel_event(self, key: EventKey) -> None:
        """Cancels a previously schedule event.

        Args:
            key: The key for an event that is currently scheduled.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidKeyError`][nexosim.exceptions.InvalidKeyError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        request = simulation_pb2.CancelEventRequest(key=key._key)  # type: ignore
        reply = self._stub.CancelEvent(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def process_event(
        self, source: str | typing.Iterable[str], event: typing.Any = None
    ) -> None:
        """Broadcasts an event from an event source immediately, blocking until
        completion.

        Simulation time remains unchanged.

        Args:
            source: The path of the event source.

            event: an object that can be serialized/deserialized to the expected
                event type. The `None` default may be used if the Rust event
                type is `()` or `Option`.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`EventSourceNotFoundError`][nexosim.exceptions.EventSourceNotFoundError]
                - [`InvalidEventTypeError`][nexosim.exceptions.InvalidEventTypeError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
        """
        source = source if not isinstance(source, str) else (source,)
        request = simulation_pb2.ProcessEventRequest(
            source=simulation_pb2.Path(segments=source),
            event=cbor2_converter.dumps(event),
        )
        reply = self._stub.ProcessEvent(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def process_query(
        self,
        source: str | typing.Iterable[str],
        request: typing.Any = None,
        reply_type: TypeForm[T] = object,
    ) -> list[T]:
        """Broadcasts a query from a query source immediately, blocking until
        completion.

        Simulation time remains unchanged.

        Args:
            source: The path of the query source.

            request: An object that can be serialized/deserialized to the expected
                request type. The `None` default may be used if the Rust request
                type is `()` or `Option`.

            reply_type: The Python type to which replies to the query should
                be mapped. If left unspecified, replies are mapped to their
                canonical representation in terms of built-in Python types such
                as `bool`, `int`, `float`, `str`, `bytes`, `dict` and `list`.

        Returns:
            An ordered list of replies to the query.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`QuerySourceNotFoundError`][nexosim.exceptions.QuerySourceNotFoundError]
                - [`InvalidQueryTypeError`][nexosim.exceptions.InvalidQueryTypeError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
                - [`SimulationBadQueryError`][nexosim.exceptions.SimulationBadQueryError]
        """
        source = source if not isinstance(source, str) else (source,)
        request = simulation_pb2.ProcessQueryRequest(
            source=simulation_pb2.Path(segments=source),
            request=cbor2_converter.dumps(request),
        )
        reply = self._stub.ProcessQuery(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        if reply_type is object:
            return [cbor2.loads(r) for r in reply.replies]
        else:
            return [cbor2_converter.loads(r, reply_type) for r in reply.replies]  # type: ignore

    def try_read_events(
        self, sink: str | typing.Iterable[str], event_type: TypeForm[T] = object
    ) -> list[T]:
        """Reads all events from an event sink.

        Args:
            sink: The path of the event sink.

            event_type: The Python type to which events should be mapped. If
                left unspecified, events are mapped to their canonical
                representation in terms of built-in Python types such as `bool`,
                `int`, `float`, `str`, `bytes`, `dict` and `list`.

        Returns:
            An ordered list of events.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`SinkNotFoundError`][nexosim.exceptions.SinkNotFoundError]
                - [`SinkTerminatedError`][nexosim.exceptions.SinkTerminatedError]
                - [`SinkReadRaceError`][nexosim.exceptions.SinkReadRaceError]
                - [`SinkReadTimeoutError`][nexosim.exceptions.SinkReadTimeoutError]
                - [`InvalidEventTypeError`][nexosim.exceptions.InvalidEventTypeError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        sink = sink if not isinstance(sink, str) else (sink,)
        request = simulation_pb2.TryReadEventsRequest(
            sink=simulation_pb2.Path(segments=sink)
        )
        reply = self._stub.TryReadEvents(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        if event_type is object:
            return [cbor2.loads(reply) for reply in reply.events]
        else:
            return [cbor2_converter.loads(r, event_type) for r in reply.events]  # type: ignore

    def read_event(
        self,
        sink: str | typing.Iterable[str],
        timeout: Duration,
        event_type: TypeForm[T] = object,
    ) -> T:
        """Waits for the next event from an event sink.

        The call is blocking.

        Args:
            sink: The path of the event sink.

            event_type: The Python type to which events should be mapped. If
                left unspecified, events are mapped to their canonical
                representation in terms of built-in Python types such as `bool`,
                `int`, `float`, `str`, `bytes`, `dict` and `list`.

        Returns:
            An event.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`SinkNotFoundError`][nexosim.exceptions.SinkNotFoundError]
                - [`SinkTerminatedError`][nexosim.exceptions.SinkTerminatedError]
                - [`SinkReadRaceError`][nexosim.exceptions.SinkReadRaceError]
                - [`SinkReadTimeoutError`][nexosim.exceptions.SinkReadTimeoutError]
                - [`InvalidEventTypeError`][nexosim.exceptions.InvalidEventTypeError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        sink = sink if not isinstance(sink, str) else (sink,)

        request = simulation_pb2.ReadEventRequest(
            sink=simulation_pb2.Path(segments=sink),
            timeout=PbDuration(seconds=timeout.secs, nanos=timeout.nanos),
        )
        reply = self._stub.ReadEvent(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        if event_type is object:
            return cbor2.loads(reply.event)
        else:
            return cbor2_converter.loads(reply.event, event_type)  # type: ignore

    def enable_sink(self, sink: str | typing.Iterable[str]) -> None:
        """Enables the reception of new events by the specified sink.

        Note that the initial state of a sink may be either `enabled`
        or `disabled` depending on the bench initializer.

        Args:
            sink: The path of the event sink.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SinkNotFoundError`][nexosim.exceptions.SinkNotFoundError]
                - [`SinkReadRaceError`][nexosim.exceptions.SinkReadRaceError]
                - [`MissingArgumentError`][nexosim.exceptions.MissingArgumentError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        sink = sink if not isinstance(sink, str) else (sink,)
        request = simulation_pb2.EnableSinkRequest(
            sink=simulation_pb2.Path(segments=sink)
        )
        reply = self._stub.EnableSink(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def disable_sink(self, sink: str | typing.Iterable[str]) -> None:
        """Disables the reception of new events by the specified sink.

        Note that the initial state of a sink may be either `enabled`
        or `disabled` depending on the bench initializer.

        Args:
            sink: The path of the event sink.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SinkNotFoundError`][nexosim.exceptions.SinkNotFoundError]
                - [`SinkReadRaceError`][nexosim.exceptions.SinkReadRaceError]
                - [`MissingArgumentError`][nexosim.exceptions.MissingArgumentError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        sink = sink if not isinstance(sink, str) else (sink,)
        request = simulation_pb2.DisableSinkRequest(
            sink=simulation_pb2.Path(segments=sink)
        )
        reply = self._stub.DisableSink(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)


def _to_error(error: simulation_pb2.Error) -> exceptions.SimulationError:
    match error.code:
        # Generic errors.
        case 0:
            return exceptions.InternalError(error.message)
        case 1:
            return exceptions.MissingArgumentError(error.message)
        case 2:
            return exceptions.InvalidTimeError(error.message)
        case 3:
            return exceptions.InvalidPeriodError(error.message)
        case 4:
            return exceptions.InvalidDeadlineError(error.message)
        case 5:
            return exceptions.InvalidMessageError(error.message)
        case 6:
            return exceptions.InvalidKeyError(error.message)
        case 7:
            return exceptions.InvalidTimeoutError(error.message)

        # Bench building and initialization errors.
        case 20:
            return exceptions.BenchPanicError(error.message)
        case 21:
            return exceptions.BenchError(error.message)
        case 22:
            return exceptions.BenchNotBuiltError(error.message)
        case 23:
            return exceptions.DuplicateEventSourceError(error.message)
        case 24:
            return exceptions.DuplicateQuerySourceError(error.message)
        case 25:
            return exceptions.DuplicateEventSinkError(error.message)
        case 26:
            return exceptions.InvalidBenchConfigError(error.message)

        # Simulation runtime errors.
        case 40:
            return exceptions.SimulationPanicError(error.message)
        case 42:
            return exceptions.SimulationNotStartedError(error.message)
        case 43:
            return exceptions.SimulationTerminatedError(error.message)
        case 44:
            return exceptions.SimulationDeadlockError(error.message)
        case 45:
            return exceptions.SimulationMessageLossError(error.message)
        case 46:
            return exceptions.SimulationNoRecipientError(error.message)
        case 47:
            return exceptions.SimulationTimeoutError(error.message)
        case 48:
            return exceptions.SimulationOutOfSyncError(error.message)
        case 49:
            return exceptions.SimulationBadQueryError(error.message)
        case 50:
            return exceptions.SimulationTimeOutOfRangeError(error.message)

        # Monitoring errors.
        case 60:
            return exceptions.EventSourceNotFoundError(error.message)
        case 61:
            return exceptions.QuerySourceNotFoundError(error.message)
        case 62:
            return exceptions.SinkNotFoundError(error.message)
        case 63:
            return exceptions.SinkTerminatedError(error.message)
        case 64:
            return exceptions.SinkReadRaceError(error.message)
        case 65:
            return exceptions.SinkReadTimeoutError(error.message)
        case 66:
            return exceptions.InvalidEventTypeError(error.message)
        case 67:
            return exceptions.InvalidQueryTypeError(error.message)

        # Serialization errors.
        case 80:
            return exceptions.SaveError(error.message)
        case 81:
            return exceptions.RestoreError(error.message)
        case _:
            return exceptions.UnexpectedError(error.message)
