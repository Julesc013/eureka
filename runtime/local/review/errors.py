"""Domain errors for local review and rebuild operations."""


class LocalReviewError(Exception):
    """Base error for local review operations."""


class LocalReviewDecisionError(LocalReviewError):
    """Raised when a local review decision is invalid."""


class LocalReviewRebuildError(LocalReviewError):
    """Raised when reviewed index rebuild fails."""
