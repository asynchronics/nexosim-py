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
    BENCH_PANIC: _ClassVar[ErrorCode]
    BENCH_ERROR: _ClassVar[ErrorCode]
    BENCH_NOT_BUILT: _ClassVar[ErrorCode]
    DUPLICATE_EVENT_SOURCE: _ClassVar[ErrorCode]
    DUPLICATE_QUERY_SOURCE: _ClassVar[ErrorCode]
    DUPLICATE_EVENT_SINK: _ClassVar[ErrorCode]
    INVALID_BENCH_CONFIG: _ClassVar[ErrorCode]
    SIMULATION_PANIC: _ClassVar[ErrorCode]
    SIMULATION_NOT_STARTED: _ClassVar[ErrorCode]
    SIMULATION_TERMINATED: _ClassVar[ErrorCode]
    SIMULATION_DEADLOCK: _ClassVar[ErrorCode]
    SIMULATION_MESSAGE_LOSS: _ClassVar[ErrorCode]
    SIMULATION_NO_RECIPIENT: _ClassVar[ErrorCode]
    SIMULATION_TIMEOUT: _ClassVar[ErrorCode]
    SIMULATION_OUT_OF_SYNC: _ClassVar[ErrorCode]
    SIMULATION_BAD_QUERY: _ClassVar[ErrorCode]
    SIMULATION_TIME_OUT_OF_RANGE: _ClassVar[ErrorCode]
    EVENT_SOURCE_NOT_FOUND: _ClassVar[ErrorCode]
    QUERY_SOURCE_NOT_FOUND: _ClassVar[ErrorCode]
    SINK_NOT_FOUND: _ClassVar[ErrorCode]
    SINK_TERMINATED: _ClassVar[ErrorCode]
    SINK_READ_RACE: _ClassVar[ErrorCode]
    SINK_READ_TIMEOUT: _ClassVar[ErrorCode]
    INVALID_EVENT_TYPE: _ClassVar[ErrorCode]
    INVALID_QUERY_TYPE: _ClassVar[ErrorCode]
    SAVE_ERROR: _ClassVar[ErrorCode]
    RESTORE_ERROR: _ClassVar[ErrorCode]
INTERNAL_ERROR: ErrorCode
MISSING_ARGUMENT: ErrorCode
INVALID_TIME: ErrorCode
INVALID_PERIOD: ErrorCode
INVALID_DEADLINE: ErrorCode
INVALID_MESSAGE: ErrorCode
INVALID_KEY: ErrorCode
INVALID_TIMEOUT: ErrorCode
BENCH_PANIC: ErrorCode
BENCH_ERROR: ErrorCode
BENCH_NOT_BUILT: ErrorCode
DUPLICATE_EVENT_SOURCE: ErrorCode
DUPLICATE_QUERY_SOURCE: ErrorCode
DUPLICATE_EVENT_SINK: ErrorCode
INVALID_BENCH_CONFIG: ErrorCode
SIMULATION_PANIC: ErrorCode
SIMULATION_NOT_STARTED: ErrorCode
SIMULATION_TERMINATED: ErrorCode
SIMULATION_DEADLOCK: ErrorCode
SIMULATION_MESSAGE_LOSS: ErrorCode
SIMULATION_NO_RECIPIENT: ErrorCode
SIMULATION_TIMEOUT: ErrorCode
SIMULATION_OUT_OF_SYNC: ErrorCode
SIMULATION_BAD_QUERY: ErrorCode
SIMULATION_TIME_OUT_OF_RANGE: ErrorCode
EVENT_SOURCE_NOT_FOUND: ErrorCode
QUERY_SOURCE_NOT_FOUND: ErrorCode
SINK_NOT_FOUND: ErrorCode
SINK_TERMINATED: ErrorCode
SINK_READ_RACE: ErrorCode
SINK_READ_TIMEOUT: ErrorCode
INVALID_EVENT_TYPE: ErrorCode
INVALID_QUERY_TYPE: ErrorCode
SAVE_ERROR: ErrorCode
RESTORE_ERROR: ErrorCode

class Error(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: ErrorCode
    message: str
    def __init__(self, code: _Optional[_Union[ErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class Path(_message.Message):
    __slots__ = ("segments",)
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    segments: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, segments: _Optional[_Iterable[str]] = ...) -> None: ...

class EventSourceSchema(_message.Message):
    __slots__ = ("source", "event")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    source: Path
    event: str
    def __init__(self, source: _Optional[_Union[Path, _Mapping]] = ..., event: _Optional[str] = ...) -> None: ...

class QuerySourceSchema(_message.Message):
    __slots__ = ("source", "request", "reply")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    REPLY_FIELD_NUMBER: _ClassVar[int]
    source: Path
    request: str
    reply: str
    def __init__(self, source: _Optional[_Union[Path, _Mapping]] = ..., request: _Optional[str] = ..., reply: _Optional[str] = ...) -> None: ...

class EventSinkSchema(_message.Message):
    __slots__ = ("sink", "event")
    SINK_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    sink: Path
    event: str
    def __init__(self, sink: _Optional[_Union[Path, _Mapping]] = ..., event: _Optional[str] = ...) -> None: ...

class EventKey(_message.Message):
    __slots__ = ("subkey1", "subkey2")
    SUBKEY1_FIELD_NUMBER: _ClassVar[int]
    SUBKEY2_FIELD_NUMBER: _ClassVar[int]
    subkey1: int
    subkey2: int
    def __init__(self, subkey1: _Optional[int] = ..., subkey2: _Optional[int] = ...) -> None: ...

class BuildRequest(_message.Message):
    __slots__ = ("cfg",)
    CFG_FIELD_NUMBER: _ClassVar[int]
    cfg: bytes
    def __init__(self, cfg: _Optional[bytes] = ...) -> None: ...

class BuildReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ("time",)
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class InitReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class InitAndRunRequest(_message.Message):
    __slots__ = ("time",)
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class InitAndRunReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class RestoreRequest(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: bytes
    def __init__(self, state: _Optional[bytes] = ...) -> None: ...

class RestoreReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class RestoreAndRunRequest(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: bytes
    def __init__(self, state: _Optional[bytes] = ...) -> None: ...

class RestoreAndRunReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

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

class SaveRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SaveReply(_message.Message):
    __slots__ = ("state", "error")
    STATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    state: bytes
    error: Error
    def __init__(self, state: _Optional[bytes] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

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

class RunRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RunReply(_message.Message):
    __slots__ = ("time", "error")
    TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    error: Error
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ListEventSourcesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListEventSourcesReply(_message.Message):
    __slots__ = ("sources", "empty", "error")
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    sources: _containers.RepeatedCompositeFieldContainer[Path]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, sources: _Optional[_Iterable[_Union[Path, _Mapping]]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class GetEventSourceSchemasRequest(_message.Message):
    __slots__ = ("sources",)
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    sources: _containers.RepeatedCompositeFieldContainer[Path]
    def __init__(self, sources: _Optional[_Iterable[_Union[Path, _Mapping]]] = ...) -> None: ...

class GetEventSourceSchemasReply(_message.Message):
    __slots__ = ("schemas", "empty", "error")
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.RepeatedCompositeFieldContainer[EventSourceSchema]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, schemas: _Optional[_Iterable[_Union[EventSourceSchema, _Mapping]]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ListQuerySourcesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListQuerySourcesReply(_message.Message):
    __slots__ = ("sources", "empty", "error")
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    sources: _containers.RepeatedCompositeFieldContainer[Path]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, sources: _Optional[_Iterable[_Union[Path, _Mapping]]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class GetQuerySourceSchemasRequest(_message.Message):
    __slots__ = ("sources",)
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    sources: _containers.RepeatedCompositeFieldContainer[Path]
    def __init__(self, sources: _Optional[_Iterable[_Union[Path, _Mapping]]] = ...) -> None: ...

class GetQuerySourceSchemasReply(_message.Message):
    __slots__ = ("schemas", "empty", "error")
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.RepeatedCompositeFieldContainer[QuerySourceSchema]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, schemas: _Optional[_Iterable[_Union[QuerySourceSchema, _Mapping]]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ListEventSinksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListEventSinksReply(_message.Message):
    __slots__ = ("sinks", "empty", "error")
    SINKS_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    sinks: _containers.RepeatedCompositeFieldContainer[Path]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, sinks: _Optional[_Iterable[_Union[Path, _Mapping]]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class GetEventSinkSchemasRequest(_message.Message):
    __slots__ = ("sinks",)
    SINKS_FIELD_NUMBER: _ClassVar[int]
    sinks: _containers.RepeatedCompositeFieldContainer[Path]
    def __init__(self, sinks: _Optional[_Iterable[_Union[Path, _Mapping]]] = ...) -> None: ...

class GetEventSinkSchemasReply(_message.Message):
    __slots__ = ("schemas", "empty", "error")
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.RepeatedCompositeFieldContainer[EventSinkSchema]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, schemas: _Optional[_Iterable[_Union[EventSinkSchema, _Mapping]]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class InjectEventRequest(_message.Message):
    __slots__ = ("source", "event")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    source: Path
    event: bytes
    def __init__(self, source: _Optional[_Union[Path, _Mapping]] = ..., event: _Optional[bytes] = ...) -> None: ...

class InjectEventReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ScheduleEventRequest(_message.Message):
    __slots__ = ("time", "duration", "source", "event", "period", "with_key")
    TIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    WITH_KEY_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    duration: _duration_pb2.Duration
    source: Path
    event: bytes
    period: _duration_pb2.Duration
    with_key: bool
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., source: _Optional[_Union[Path, _Mapping]] = ..., event: _Optional[bytes] = ..., period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., with_key: bool = ...) -> None: ...

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
    __slots__ = ("source", "event")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    source: Path
    event: bytes
    def __init__(self, source: _Optional[_Union[Path, _Mapping]] = ..., event: _Optional[bytes] = ...) -> None: ...

class ProcessEventReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ProcessQueryRequest(_message.Message):
    __slots__ = ("source", "request")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    source: Path
    request: bytes
    def __init__(self, source: _Optional[_Union[Path, _Mapping]] = ..., request: _Optional[bytes] = ...) -> None: ...

class ProcessQueryReply(_message.Message):
    __slots__ = ("replies", "empty", "error")
    REPLIES_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    replies: _containers.RepeatedScalarFieldContainer[bytes]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, replies: _Optional[_Iterable[bytes]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class TryReadEventsRequest(_message.Message):
    __slots__ = ("sink",)
    SINK_FIELD_NUMBER: _ClassVar[int]
    sink: Path
    def __init__(self, sink: _Optional[_Union[Path, _Mapping]] = ...) -> None: ...

class TryReadEventsReply(_message.Message):
    __slots__ = ("events", "empty", "error")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedScalarFieldContainer[bytes]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, events: _Optional[_Iterable[bytes]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ReadEventRequest(_message.Message):
    __slots__ = ("sink", "timeout")
    SINK_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    sink: Path
    timeout: _duration_pb2.Duration
    def __init__(self, sink: _Optional[_Union[Path, _Mapping]] = ..., timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class ReadEventReply(_message.Message):
    __slots__ = ("event", "error")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    event: bytes
    error: Error
    def __init__(self, event: _Optional[bytes] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class EnableSinkRequest(_message.Message):
    __slots__ = ("sink",)
    SINK_FIELD_NUMBER: _ClassVar[int]
    sink: Path
    def __init__(self, sink: _Optional[_Union[Path, _Mapping]] = ...) -> None: ...

class EnableSinkReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class DisableSinkRequest(_message.Message):
    __slots__ = ("sink",)
    SINK_FIELD_NUMBER: _ClassVar[int]
    sink: Path
    def __init__(self, sink: _Optional[_Union[Path, _Mapping]] = ...) -> None: ...

class DisableSinkReply(_message.Message):
    __slots__ = ("empty", "error")
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    error: Error
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...
