"""Domain errors for deterministic local workers."""


class LocalWorkerError(Exception):
    """Base error for local worker failures."""


class LocalWorkerPolicyError(LocalWorkerError, ValueError):
    """Raised when worker policy blocks execution."""


class LocalWorkerValidationError(LocalWorkerError, ValueError):
    """Raised when worker output is invalid."""


class LocalWorkerNotFoundError(LocalWorkerError, LookupError):
    """Raised when a worker kind is not registered."""
