"""Domain errors for the durable local work queue."""


class WorkUnitQueueError(Exception):
    """Base error for work queue failures."""


class WorkUnitValidationError(WorkUnitQueueError, ValueError):
    """Raised when a work record is invalid."""


class WorkUnitTransitionError(WorkUnitQueueError, ValueError):
    """Raised when a state change is invalid."""


class WorkUnitNotFoundError(WorkUnitQueueError, LookupError):
    """Raised when a work record cannot be found."""


class WorkUnitQueueClosedError(WorkUnitQueueError, RuntimeError):
    """Raised when a closed queue store is used."""
