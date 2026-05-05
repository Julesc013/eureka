"""Bounded errors for the P103 local page dry-run runtime."""

from __future__ import annotations


class PageDryRunError(Exception):
    """Base class for dry-run page runtime failures."""


class PagePolicyError(PageDryRunError):
    """Raised when a path, argument, or record violates dry-run policy."""


class PageValidationError(PageDryRunError):
    """Raised when a page record cannot be structurally validated."""
