"""Domain errors for local operator authentication."""


class LocalOperatorError(Exception):
    """Base error for local operator authentication."""


class LocalOperatorAuthError(LocalOperatorError):
    """Raised when operator authentication fails."""


class LocalOperatorConfigError(LocalOperatorError):
    """Raised when operator authentication config is invalid."""
