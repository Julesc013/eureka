"""Bounded errors for evidence-ledger dry-run policy checks."""

from __future__ import annotations


class EvidenceLedgerDryRunError(Exception):
    """Base class for local dry-run failures."""


class EvidenceLedgerPolicyError(EvidenceLedgerDryRunError):
    """Raised when a dry-run input or output violates policy."""
