"""Errors for the local reviewed public index store."""

from __future__ import annotations


class PublicIndexError(Exception):
    """Base error for reviewed public index operations."""


class PublicIndexValidationError(PublicIndexError):
    """Raised when reviewed public index inputs are invalid."""


class PublicIndexStoreError(PublicIndexError):
    """Raised when the reviewed public index store cannot complete an operation."""


class PublicIndexRebuildError(PublicIndexError):
    """Raised when a reviewed public index rebuild cannot complete."""
