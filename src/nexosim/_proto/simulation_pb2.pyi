from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INTERNAL_ERROR: _ClassVar[ErrorCode]
    MISSING_ARGUMENT: _ClassVar[ErrorCode]
    INVALID_TIME: _ClassVar[ErrorCode]
    INVALID_PERIOD: _ClassVar[ErrorCode]
    INVALID_DEADLINE: _ClassVar[ErrorCode]
    INVALID_MESSAGE: _ClassVar[ErrorCode]
    INVALID_KEY: _ClassVar[ErrorCode]
    INVALID_TIMEOUT: _ClassVar[ErrorCode]
    INITIALIZER_PANIC: _ClassVar[ErrorCode]
    SIMULATION_NOT_STARTED: _ClassVar[ErrorCode]
    SIMULATION_HALTED: _ClassVar[ErrorCode]
    SIMULATION_TERMINATED: _ClassVar[ErrorCode]
    SIMULATION_DEADLOCK: _ClassVar[ErrorCode]
    SIMULATION_MESSAGE_LOSS: _ClassVar[ErrorCode]
    SIMULATION_NO_RECIPIENT: _ClassVar[ErrorCode]
    SIMULATION_PANIC: _ClassVar[ErrorCode]
    SIMULATION_TIMEOUT: _ClassVar[ErrorCode]
    SIMULATION_OUT_OF_SYNC: _ClassVar[ErrorCode]
    SIMULATION_BAD_QUERY: _ClassVar[ErrorCode]
    SIMULATION_TIME_OUT_OF_RANGE: _ClassVar[ErrorCode]
    SOURCE_NOT_FOUND: _ClassVar[ErrorCode]
    SINK_NOT_FOUND: _ClassVar[ErrorCode]
INTERNAL_ERROR: ErrorCode
MISSING_ARGUMENT: ErrorCode
INVALID_TIME: ErrorCode
INVALID_PERIOD: ErrorCode
INVALID_DEADLINE: ErrorCode
INVALID_MESSAGE: ErrorCode
INVALID_KEY: ErrorCode
INVALID_TIMEOUT: ErrorCode
INITIALIZER_PANIC: ErrorCode
SIMULATION_NOT_STARTED: ErrorCode
SIMULATION_HALTED: ErrorCode
SIMULATION_TERMINATED: ErrorCode
SIMULATION_DEADLOCK: ErrorCode
SIMULATION_MESSAGE_LOSS: ErrorCode
SIMULATION_NO_RECIPIENT: ErrorCode
SIMULATION_PANIC: ErrorCode
SIMULATION_TIMEOUT: ErrorCode
SIMULATION_OUT_OF_SYNC: ErrorCode
SIMULATION_BAD_QUERY: ErrorCode
SIMULATION_TIME_OUT_OF_RANGE: ErrorCode
SOURCE_NOT_FOUND: ErrorCode
SINK_NOT_FOUND: ErrorCode

class Error(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: ErrorCode
    message: str
    def __init__(self, code: _Optional[_Union[ErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class EventKey(_message.Message):
    __slots__ = ("subkey1", "subkey2")
    SUBKEY1_FIELD_NUMBER: _ClassVar[int]
    SUBKEY2_FIELD_NUMBER: _ClassVar[int]
    subkey1: int
    subkey2: int
    def __init__(self, subkey1: _Optional[int] = ..., subkey2: _Optional[int] = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ("cfg",)
    CFG_FIELD_NUMBER: _ClassVar[int]
    cfg: bytes
    def __init__(self, cfg: _Optional[bytes] = ...) -> None: ...

class InitReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class TerminateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TerminateReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class HaltRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HaltReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class TimeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TimeReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class StepRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StepReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class StepUntilRequest(_message.Message):
    __slots__ = ("time", "duration")
    TIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    duration: _duration_pb2.Duration
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class StepUntilReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class StepUnboundedRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StepUnboundedReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ScheduleEventRequest(_message.Message):
    __slots__ = ("time", "duration", "source_name", "event", "period", "with_key")
    TIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    WITH_KEY_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    duration: _duration_pb2.Duration
    source_name: str
    event: bytes
    period: _duration_pb2.Duration
    with_key: bool
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., source_name: _Optional[str] = ..., event: _Optional[bytes] = ..., period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., with_key: bool = ...) -> None: ...

class ScheduleEventReply(_message.Message):
    __slots__ = ("empty", "key", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    key: EventKey
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., key: _Optional[_Union[EventKey, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class CancelEventRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: EventKey
    def __init__(self, key: _Optional[_Union[EventKey, _Mapping]] = ...) -> None: ...

class CancelEventReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ProcessEventRequest(_message.Message):
    __slots__ = ("source_name", "event")
    SOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    source_name: str
    event: bytes
    def __init__(self, source_name: _Optional[str] = ..., event: _Optional[bytes] = ...) -> None: ...

class ProcessEventReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ProcessQueryRequest(_message.Message):
    __slots__ = ("source_name", "request")
    SOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    source_name: str
    request: bytes
    def __init__(self, source_name: _Optional[str] = ..., request: _Optional[bytes] = ...) -> None: ...

class ProcessQueryReply(_message.Message):
    __slots__ = ("replies", "empty", "error")
    REPLIES_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    replies: _containers.RepeatedScalarFieldContainer[bytes]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, replies: _Optional[_Iterable[bytes]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ReadEventsRequest(_message.Message):
    __slots__ = ("sink_name",)
    SINK_NAME_FIELD_NUMBER: _ClassVar[int]
    sink_name: str
    def __init__(self, sink_name: _Optional[str] = ...) -> None: ...

class ReadEventsReply(_message.Message):
    __slots__ = ("events", "empty", "error")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedScalarFieldContainer[bytes]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, events: _Optional[_Iterable[bytes]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class AwaitEventRequest(_message.Message):
    __slots__ = ("sink_name", "timeout")
    SINK_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    sink_name: str
    timeout: _duration_pb2.Duration
    def __init__(self, sink_name: _Optional[str] = ..., timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class AwaitEventReply(_message.Message):
    __slots__ = ("event", "error")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    event: bytes
    error: Error
    def __init__(self, event: _Optional[bytes] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class OpenSinkRequest(_message.Message):
    __slots__ = ("sink_name",)
    SINK_NAME_FIELD_NUMBER: _ClassVar[int]
    sink_name: str
    def __init__(self, sink_name: _Optional[str] = ...) -> None: ...

class OpenSinkReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class CloseSinkRequest(_message.Message):
    __slots__ = ("sink_name",)
    SINK_NAME_FIELD_NUMBER: _ClassVar[int]
    sink_name: str
    def __init__(self, sink_name: _Optional[str] = ...) -> None: ...

class CloseSinkReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class AnyRequest(_message.Message):
    __slots__ = ("init_request", "halt_request", "time_request", "step_request", "step_until_request", "schedule_event_request", "cancel_event_request", "process_event_request", "process_query_request", "read_events_request", "open_sink_request", "close_sink_request", "await_event_request", "step_unbounded_request", "terminate_request")
    INIT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    HALT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TIME_REQUEST_FIELD_NUMBER: _ClassVar[int]
    STEP_REQUEST_FIELD_NUMBER: _ClassVar[int]
    STEP_UNTIL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_EVENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    CANCEL_EVENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    PROCESS_EVENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    PROCESS_QUERY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    READ_EVENTS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    OPEN_SINK_REQUEST_FIELD_NUMBER: _ClassVar[int]
    CLOSE_SINK_REQUEST_FIELD_NUMBER: _ClassVar[int]
    AWAIT_EVENT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    STEP_UNBOUNDED_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TERMINATE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    init_request: InitRequest
    halt_request: HaltRequest
    time_request: TimeRequest
    step_request: StepRequest
    step_until_request: StepUntilRequest
    schedule_event_request: ScheduleEventRequest
    cancel_event_request: CancelEventRequest
    process_event_request: ProcessEventRequest
    process_query_request: ProcessQueryRequest
    read_events_request: ReadEventsRequest
    open_sink_request: OpenSinkRequest
    close_sink_request: CloseSinkRequest
    await_event_request: AwaitEventRequest
    step_unbounded_request: StepUnboundedRequest
    terminate_request: TerminateRequest
    def __init__(self, init_request: _Optional[_Union[InitRequest, _Mapping]] = ..., halt_request: _Optional[_Union[HaltRequest, _Mapping]] = ..., time_request: _Optional[_Union[TimeRequest, _Mapping]] = ..., step_request: _Optional[_Union[StepRequest, _Mapping]] = ..., step_until_request: _Optional[_Union[StepUntilRequest, _Mapping]] = ..., schedule_event_request: _Optional[_Union[ScheduleEventRequest, _Mapping]] = ..., cancel_event_request: _Optional[_Union[CancelEventRequest, _Mapping]] = ..., process_event_request: _Optional[_Union[ProcessEventRequest, _Mapping]] = ..., process_query_request: _Optional[_Union[ProcessQueryRequest, _Mapping]] = ..., read_events_request: _Optional[_Union[ReadEventsRequest, _Mapping]] = ..., open_sink_request: _Optional[_Union[OpenSinkRequest, _Mapping]] = ..., close_sink_request: _Optional[_Union[CloseSinkRequest, _Mapping]] = ..., await_event_request: _Optional[_Union[AwaitEventRequest, _Mapping]] = ..., step_unbounded_request: _Optional[_Union[StepUnboundedRequest, _Mapping]] = ..., terminate_request: _Optional[_Union[TerminateRequest, _Mapping]] = ...) -> None: ...
