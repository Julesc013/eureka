"""Domain exceptions for the local HTTP service."""


class LocalServiceError(Exception):
    """Base error for local service failures."""


class LocalServiceValidationError(LocalServiceError):
    """Raised when a request or configuration is invalid."""


class LocalServiceHostError(LocalServiceValidationError):
    """Raised when a bind or client host is outside the local boundary."""


class LocalServiceReadOnlyError(LocalServiceValidationError):
    """Raised when a request attempts a disabled write path."""


class LocalServiceRouteError(LocalServiceError):
    """Raised when a local route cannot be served."""
