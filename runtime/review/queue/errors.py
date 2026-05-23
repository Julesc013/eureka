"""Error types for the durable review queue store."""

from __future__ import annotations


class ReviewQueueError(Exception):
    """Base error for review queue operations."""


class ReviewQueueValidationError(ReviewQueueError):
    """Raised when review queue input fails validation."""


class ReviewQueueMigrationError(ReviewQueueError):
    """Raised when review queue schema migration fails."""


class ReviewQueueStoreError(ReviewQueueError):
    """Raised when review queue persistence fails."""
