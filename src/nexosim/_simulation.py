import inspect
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

    def start(self, cfg: typing.Any = None) -> None:
        """
        Creates a simulation bench.

        If a simulation bench is already running, it is replaced by the newly
        initialized bench. In such case, events that have not yet been retrieved
        from the sinks will be lost and the sinks are reset to their default
        open/close state.

        Args:
            cfg: A bench configuration object which can be
                serialized/deserialized to the expected bench configuration
                type. The `None` default is appropriate if the bench initializer
                expects the Rust type `()` or accepts an `Option::None`.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`SimulationOutOfSyncError`][nexosim.exceptions.SimulationOutOfSyncError]
        """
        request = simulation_pb2.InitRequest(cfg=cbor2_converter.dumps(cfg))
        reply = self._stub.Init(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def terminate(self) -> None:
        """
        Terminates a simulation.
        """
        request = simulation_pb2.TerminateRequest()
        reply = self._stub.Terminate(request)  # type: ignore

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def halt(self) -> None:
        """
        Requests the simulation to stop at the earliest opportunity.

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
                - [`SimulationHaltedError`][nexosim.exceptions.SimulationHaltedError]
        """

        request = simulation_pb2.StepRequest()
        reply = self._stub.Step(request)

        if reply.HasField("time"):
            return MonotonicTime(reply.time.seconds, reply.time.nanos)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        raise exceptions.UnexpectedError("unexpected response")

    def step_unbounded(self) -> MonotonicTime:
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
                - [`SimulationHaltedError`][nexosim.exceptions.SimulationHaltedError]

        """

        request = simulation_pb2.StepUnboundedRequest()
        reply = self._stub.StepUnbounded(request)  # type: ignore
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
                - [`SimulationHaltedError`][nexosim.exceptions.SimulationHaltedError]
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

    @typing.overload
    def schedule_event(
        self,
        deadline: MonotonicTime | Duration,
        source_name: str,
        event: object = None,
        period: None | Duration = None,
        with_key: typing.Literal[False] = False,
    ) -> None: ...

    @typing.overload
    def schedule_event(
        self,
        deadline: MonotonicTime | Duration,
        source_name: str,
        event: object,
        period: None | Duration,
        with_key: typing.Literal[True],
    ) -> EventKey: ...

    def schedule_event(
        self,
        deadline: MonotonicTime | Duration,
        source_name: str,
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

            source_name: The name of the event source.

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
                - [`SourceNotFoundError`][nexosim.exceptions.SourceNotFoundError]
                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        kwargs = {}

        if isinstance(deadline, MonotonicTime):
            kwargs["time"] = PbTimestamp(seconds=deadline.secs, nanos=deadline.nanos)
        else:
            kwargs["duration"] = PbDuration(seconds=deadline.secs, nanos=deadline.nanos)

        kwargs["source_name"] = source_name

        if inspect.isclass(type(event)):
            event_bytes = cbor2_converter.dumps(event)
        else:
            event_bytes = cbor2.dumps(event)
        kwargs["event"] = event_bytes

        if period is not None:
            kwargs["period"] = PbDuration(seconds=period.secs, nanos=period.nanos)

        kwargs["with_key"] = with_key

        request = simulation_pb2.ScheduleEventRequest(**kwargs)  # type: ignore
        reply = self._stub.ScheduleEvent(request)

        if reply.HasField("key"):
            key = EventKey()
            key._key = reply.key  # type: ignore

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

    def process_event(self, source_name: str, event: typing.Any = None) -> None:
        """Broadcasts an event from an event source immediately, blocking until
        completion.

        Simulation time remains unchanged.

        Args:
            source_name: The name of the event source.

            event: an object that can be serialized/deserialized to the expected
                event type. The `None` default may be used if the Rust event
                type is `()` or `Option`.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`InvalidMessageError`][nexosim.exceptions.InvalidMessageError]
                - [`SourceNotFoundError`][nexosim.exceptions.SourceNotFoundError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
        """

        request = simulation_pb2.ProcessEventRequest(
            source_name=source_name, event=cbor2_converter.dumps(event)
        )
        reply = self._stub.ProcessEvent(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def process_query(
        self,
        source_name: str,
        request: typing.Any = None,
        reply_type: TypeForm[T] = object,
    ) -> list[T]:
        """Broadcasts a query from a query source immediately, blocking until
        completion.

        Simulation time remains unchanged.

        Args:
            source_name: The name of the query source.

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
                - [`SourceNotFoundError`][nexosim.exceptions.SourceNotFoundError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
                - [`SimulationTerminatedError`][nexosim.exceptions.SimulationTerminatedError]
                - [`SimulationDeadlockError`][nexosim.exceptions.SimulationDeadlockError]
                - [`SimulationMessageLossError`][nexosim.exceptions.SimulationMessageLossError]
                - [`SimulationNoRecipientError`][nexosim.exceptions.SimulationNoRecipientError]
                - [`SimulationPanicError`][nexosim.exceptions.SimulationPanicError]
                - [`SimulationTimeoutError`][nexosim.exceptions.SimulationTimeoutError]
                - [`SimulationBadQueryError`][nexosim.exceptions.SimulationBadQueryError]
        """
        request = simulation_pb2.ProcessQueryRequest(
            source_name=source_name, request=cbor2_converter.dumps(request)
        )
        reply = self._stub.ProcessQuery(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        if reply_type is object:
            return [cbor2.loads(r) for r in reply.replies]
        else:
            return [cbor2_converter.loads(r, reply_type) for r in reply.replies]  # type: ignore

    def read_events(self, sink_name: str, event_type: TypeForm[T] = object) -> list[T]:
        """Reads all events from an event sink.

        Args:
            sink_name: The name of the event sink.

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
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        request = simulation_pb2.ReadEventsRequest(sink_name=sink_name)
        reply = self._stub.ReadEvents(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

        if event_type is object:
            return [cbor2.loads(reply) for reply in reply.events]
        else:
            return [cbor2_converter.loads(r, event_type) for r in reply.events]  # type: ignore

    def await_event(
        self, sink_name: str, timeout: Duration, event_type: TypeForm[T] = object
    ) -> T:
        """Waits for the next event from an event sink.

        The call is blocking.

        Args:
            sink_name: The name of the event sink.

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
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        request = simulation_pb2.AwaitEventRequest(
            sink_name=sink_name,
            timeout=PbDuration(seconds=timeout.secs, nanos=timeout.nanos),
        )
        reply = self._stub.AwaitEvent(request)  # type: ignore

        if reply.HasField("error"):
            raise _to_error(reply.error)

        if event_type is object:
            return cbor2.loads(reply.event)
        else:
            return cbor2_converter.loads(reply.event, event_type)  # type: ignore

    def open_sink(self, sink_name: str) -> None:
        """Enables the reception of new events by the specified sink.

        Note that the initial state of a sink may be either `open` or `closed`
        depending on the bench initializer.

        Args:
            sink_name: The name of the event sink.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SinkNotFoundError`][nexosim.exceptions.SinkNotFoundError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """
        request = simulation_pb2.OpenSinkRequest(sink_name=sink_name)
        reply = self._stub.OpenSink(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)

    def close_sink(self, sink_name: str) -> None:
        """Disables the reception of new events by the specified sink.

        Note that the initial state of a sink may be either `open` or `closed`
        depending on the bench initializer.

        Args:
            sink_name: The name of the event sink.

        Raises:
            exceptions.SimulationError: One of the exceptions derived from
                [`SimulationError`][nexosim.exceptions.SimulationError] may be
                raised, such as:

                - [`SinkNotFoundError`][nexosim.exceptions.SinkNotFoundError]
                - [`SimulationNotStartedError`][nexosim.exceptions.SimulationNotStartedError]
        """

        request = simulation_pb2.CloseSinkRequest(sink_name=sink_name)
        reply = self._stub.CloseSink(request)

        if reply.HasField("error"):
            raise _to_error(reply.error)


def _to_error(error: simulation_pb2.Error) -> exceptions.SimulationError:
    match error.code:
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
        case 11:
            return exceptions.SimulationNotStartedError(error.message)
        case 12:
            return exceptions.SimulationHaltedError(error.message)
        case 13:
            return exceptions.SimulationTerminatedError(error.message)
        case 14:
            return exceptions.SimulationDeadlockError(error.message)
        case 15:
            return exceptions.SimulationMessageLossError(error.message)
        case 16:
            return exceptions.SimulationNoRecipientError(error.message)
        case 17:
            return exceptions.SimulationPanicError(error.message)
        case 18:
            return exceptions.SimulationTimeoutError(error.message)
        case 19:
            return exceptions.SimulationOutOfSyncError(error.message)
        case 20:
            return exceptions.SimulationBadQueryError(error.message)
        case 21:
            return exceptions.SimulationTimeOutOfRangeError(error.message)
        case 30:
            return exceptions.SourceNotFoundError(error.message)
        case 31:
            return exceptions.SinkNotFoundError(error.message)
        case _:
            return exceptions.UnexpectedError(error.message)
