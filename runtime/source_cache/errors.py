"""Bounded source cache dry-run errors."""

from __future__ import annotations


class SourceCacheError(Exception):
    """Base class for durable source cache failures."""


class SourceCacheValidationError(SourceCacheError):
    """Raised when durable source cache input is invalid."""


class SourceCacheMigrationError(SourceCacheError):
    """Raised when durable source cache schema setup fails."""


class SourceCacheStoreError(SourceCacheError):
    """Raised when durable source cache storage fails."""


class SourceCacheDryRunError(Exception):
    """Base class for local source cache dry-run failures."""


class SourceCachePolicyError(SourceCacheDryRunError):
    """Raised when a dry-run input violates local safety policy."""


class SourceCacheValidationError(SourceCacheDryRunError):
    """Raised when a candidate cannot be structurally validated."""
