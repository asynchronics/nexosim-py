"""Simulation-related exceptions.

All exceptions derive from the `SimulationError` class.
"""


class SimulationError(Exception):
    """The base class for exceptions thrown by a [`Simulation`][nexosim.Simulation]."""

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


class SimulationNotStartedError(SimulationError):
    """Raised when the simulation is invoked before it was initialized."""

    pass


class SimulationHaltedError(SimulationError):
    """The simulation has been intentionally stopped."""

    pass


class SimulationTerminatedError(SimulationError):
    """The simulation has been terminated due to an earlier deadlock, message
    loss, missing recipient, model panic, timeout or synchronization loss"""

    pass


class SimulationDeadlockError(SimulationError):
    """Raised when the simulation has deadlocked."""

    pass


class SimulationMessageLossError(SimulationError):
    """Raised when the recipient of a message does not exists."""

    pass


class SimulationNoRecipientError(SimulationError):
    """Raised when the simulation is invoked before it was initialized."""

    pass


class SimulationPanicError(SimulationError):
    """Raised when a panic is caught during execution."""

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


class SourceNotFoundError(SimulationError):
    """Raised when the provided name does not match any event or query
    source."""

    pass


class SinkNotFoundError(SimulationError):
    """Raised when the provided name does not match any event sink."""

    pass


class UnexpectedError(SimulationError):
    """Raised when an internal implementation error occurs."""

    pass
