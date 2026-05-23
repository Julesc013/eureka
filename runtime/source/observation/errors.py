"""Domain errors for source observation runtime."""

from __future__ import annotations


class SourceObservationError(Exception):
    """Base error for source observation runtime."""


class SourceObservationValidationError(SourceObservationError):
    """Raised when source observation data cannot be accepted by the seam."""


class SourceObservationPolicyError(SourceObservationError):
    """Raised when policy evaluation cannot be completed."""
