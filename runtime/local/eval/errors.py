"""Errors for deterministic local evaluation."""


class LocalEvalError(Exception):
    """Base error for local evaluation."""


class LocalEvalValidationError(LocalEvalError):
    """Raised when local evaluation input or output is invalid."""


class LocalEvalSafetyError(LocalEvalError):
    """Raised when a safety boundary check fails."""
