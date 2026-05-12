"""Deterministic SQLite migrations for the evidence ledger store."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from typing import Sequence

from .errors import EvidenceLedgerMigrationError
from .records import utc_now
from .schema import INITIAL_SCHEMA_STATEMENTS, SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class EvidenceLedgerMigration:
    migration_id: str
    version: str
    statements: tuple[str, ...]

    @property
    def checksum(self) -> str:
        payload = "\n".join(statement.strip() for statement in self.statements)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "migration_id": self.migration_id,
            "version": self.version,
            "checksum": self.checksum,
            "statement_count": len(self.statements),
        }


MIGRATIONS: tuple[EvidenceLedgerMigration, ...] = (
    EvidenceLedgerMigration(
        migration_id="001_initial_evidence_ledger_store",
        version=SCHEMA_VERSION,
        statements=tuple(INITIAL_SCHEMA_STATEMENTS),
    ),
)


def apply_migrations(
    connection: sqlite3.Connection,
    migrations: Sequence[EvidenceLedgerMigration] = MIGRATIONS,
) -> list[dict[str, object]]:
    applied: list[dict[str, object]] = []
    try:
        connection.execute("BEGIN")
        for migration in migrations:
            for statement in migration.statements:
                connection.execute(statement)
            existing = connection.execute(
                "SELECT checksum FROM evidence_ledger_migrations WHERE id = ?",
                (migration.migration_id,),
            ).fetchone()
            if existing is not None and existing[0] != migration.checksum:
                raise EvidenceLedgerMigrationError(f"migration checksum mismatch: {migration.migration_id}")
            if existing is None:
                connection.execute(
                    "INSERT INTO evidence_ledger_migrations (id, version, checksum, applied_at) VALUES (?, ?, ?, ?)",
                    (migration.migration_id, migration.version, migration.checksum, utc_now()),
                )
                applied.append(migration.to_dict())
        connection.execute(
            "INSERT INTO evidence_ledger_meta (key, value, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            ("schema_version", SCHEMA_VERSION, utc_now()),
        )
        connection.commit()
    except sqlite3.Error as exc:
        connection.rollback()
        raise EvidenceLedgerMigrationError(str(exc)) from exc
    return applied


def get_applied_migrations(connection: sqlite3.Connection) -> list[dict[str, str]]:
    rows = connection.execute(
        "SELECT id, version, checksum, applied_at FROM evidence_ledger_migrations ORDER BY id"
    ).fetchall()
    return [
        {
            "id": str(row[0]),
            "version": str(row[1]),
            "checksum": str(row[2]),
            "applied_at": str(row[3]),
        }
        for row in rows
    ]
