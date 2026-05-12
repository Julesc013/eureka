"""Error types for evidence ledger runtime helpers."""

from __future__ import annotations


class EvidenceLedgerError(Exception):
    """Base error for evidence ledger operations."""


class EvidenceLedgerValidationError(EvidenceLedgerError):
    """Raised when evidence ledger input fails validation."""


class EvidenceLedgerMigrationError(EvidenceLedgerError):
    """Raised when evidence ledger schema migration fails."""


class EvidenceLedgerStoreError(EvidenceLedgerError):
    """Raised when evidence ledger persistence fails."""


class EvidenceLedgerDryRunError(Exception):
    """Base class for local dry-run failures."""


class EvidenceLedgerPolicyError(EvidenceLedgerDryRunError):
    """Raised when a dry-run input or output violates policy."""
