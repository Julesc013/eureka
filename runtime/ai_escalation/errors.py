"""Errors for disabled AI escalation gate records."""


class AIEscalationError(Exception):
    """Base error for AI escalation gate handling."""


class AIEscalationClosedError(AIEscalationError):
    """Raised when a closed store is used."""


class AIEscalationNotFoundError(AIEscalationError):
    """Raised when a gate record is missing."""


class AIEscalationValidationError(AIEscalationError):
    """Raised when disabled-gate validation fails."""
