"""Simulation-related exceptions.

All exceptions derive from the `SimulationError` class.
"""


class SimulationError(Exception):
    """The base class for exceptions thrown by a [`Simulation`][nexosim.Simulation]."""

    pass


class InternalError(SimulationError):
    """Raised when an internal implementation error occurs."""

    pass


class MissingArgumentError(SimulationError):
    """Raised when a simulation call was invoked with too few arguments."""

    pass


class InvalidTimeError(SimulationError):
    """Raised when the provided timestamp is not well-formed."""

    pass


class InvalidPeriodError(SimulationError):
    """Raised when a null or negative period was provided."""

    pass


class InvalidDeadlineError(SimulationError):
    """Raised when a deadline that is not in the future of the current
    simulation time was provided."""

    pass


class InvalidMessageError(SimulationError):
    """Raised when the provided event, query or initialization configuration
    message is invalid."""

    pass


class InvalidKeyError(SimulationError):
    """Raised when an event key is invalid or outdated."""

    pass


class InvalidTimeoutError(SimulationError):
    """Raised when a negative timeout was provided."""

    pass


class BenchPanicError(SimulationError):
    """Raised when the simulation bench builder has panicked."""

    pass


class BenchError(SimulationError):
    """Raised when the simulation bench building has failed."""

    pass


class BenchNotBuiltError(SimulationError):
    """Raised when the simulation is initialized or restored before being built."""

    pass


class DuplicateEventSourceError(SimulationError):
    """
    Raised when an attempt to add an event source has failed because
    the provided path is already in use by another event source.
    """

    pass


class DuplicateQuerySourceError(SimulationError):
    """
    Raised when an attempt to add a query source has failed because
    the provided path is already in use by another query source.
    """

    pass


class DuplicateEventSinkError(SimulationError):
    """
    Raised when an attempt to add an event sink has failed because
    the provided path is already in use by another event sink.
    """

    pass


class InvalidBenchConfigError(SimulationError):
    """Raised when the simulation bench configuration could not be deserialized."""

    pass


class SimulationPanicError(SimulationError):
    """Raised when a panic is caught during execution."""

    pass


class SimulationNotStartedError(SimulationError):
    """Raised when the simulation is invoked before it was initialized."""

    pass


class SimulationTerminatedError(SimulationError):
    """
    Raised when the simulation has been terminated due to an earlier deadlock,
    message loss, missing recipient, model panic, timeout, or synchronization
    loss.
    """

    pass


class SimulationDeadlockError(SimulationError):
    """Raised when the simulation has deadlocked."""

    pass


class SimulationMessageLossError(SimulationError):
    """
    Raised when a message was left unprocessed because the recipient's mailbox
    was not migrated to the simulation.
    """

    pass


class SimulationNoRecipientError(SimulationError):
    """Raised when the recipient of a message does not exists."""

    pass


class SimulationTimeoutError(SimulationError):
    """Raised when a simulation step fails to complete within the allocated
    time."""

    pass


class SimulationOutOfSyncError(SimulationError):
    """Raised when the simulation has lost synchronization with the clock."""

    pass


class SimulationBadQueryError(SimulationError):
    """Raised when a query did not obtain a response because the mailbox
    targeted by the query was not found in the simulation."""

    pass


class SimulationTimeOutOfRangeError(SimulationError):
    """Raised when the provided simulation time is out of the range supported by
    the Python timestamp."""

    pass


class EventSourceNotFoundError(SimulationError):
    """Raised when the provided name does not match any event source."""

    pass


class QuerySourceNotFoundError(SimulationError):
    """Raised when the provided name does not match any query source."""

    pass


class SinkNotFoundError(SimulationError):
    """Raised when the provided name does not match any event sink."""

    pass


class SinkTerminatedError(SimulationError):
    """Raised when an event sink has no sender."""

    pass


class SinkReadRaceError(SimulationError):
    """
    Raised when a concurrent read operation on an event sink has been attempted.
    """

    pass


class SinkReadTimeoutError(SimulationError):
    """
    Raised a read operation on an event sink has timed out.
    """

    pass


class InvalidEventTypeError(SimulationError):
    """
    Raised when the specified event type for an event source or event sink does
    not match the expected type.
    """

    pass


class InvalidQueryTypeError(SimulationError):
    """
    Raised when the specified request or reply types for a query source do not
    match the respective expected types.
    """

    pass


class SaveError(SimulationError):
    """Raised when a simulation state store procedure has failed."""

    pass


class RestoreError(SimulationError):
    """Raised when a simulation state restore procedure has failed."""

    pass


class UnexpectedError(SimulationError):
    """Raised when an internal implementation error occurs."""

    pass
