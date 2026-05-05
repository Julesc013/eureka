"""Bounded error types for P104 pack import dry-run runtime."""

from __future__ import annotations


class PackImportDryRunError(Exception):
    """Base error for local pack import dry-run failures."""


class PackImportPolicyError(PackImportDryRunError):
    """Raised when a path, CLI argument, or record violates dry-run policy."""
