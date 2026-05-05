"""Bounded source cache dry-run errors."""

from __future__ import annotations


class SourceCacheDryRunError(Exception):
    """Base class for local source cache dry-run failures."""


class SourceCachePolicyError(SourceCacheDryRunError):
    """Raised when a dry-run input violates local safety policy."""


class SourceCacheValidationError(SourceCacheDryRunError):
    """Raised when a candidate cannot be structurally validated."""
