"""Errors raised by the headless resolution-run kernel."""


class ResolutionRunError(Exception):
    """Base error for resolution-run orchestration."""


class ResolutionRunValidationError(ResolutionRunError, ValueError):
    """Raised when a run packet or command is malformed."""


class ResolutionRunPolicyError(ResolutionRunError, PermissionError):
    """Raised when a command is forbidden by policy."""


class ResolutionRunNotFoundError(ResolutionRunError, LookupError):
    """Raised when a requested run is not available in the store."""
