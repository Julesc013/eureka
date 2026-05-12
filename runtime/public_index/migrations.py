"""Migrations for the local reviewed public index store."""

from __future__ import annotations

import hashlib
import sqlite3

from .records import utc_now
from .schema import INITIAL_SCHEMA_STATEMENTS, SCHEMA_VERSION


MIGRATION_ID = "public_index_initial_schema"
MIGRATION_CHECKSUM = hashlib.sha256("\n".join(INITIAL_SCHEMA_STATEMENTS).encode("utf-8")).hexdigest()


def apply_migrations(connection: sqlite3.Connection) -> list[dict[str, object]]:
    applied: list[dict[str, object]] = []
    now = utc_now()
    for statement in INITIAL_SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.execute(
        "INSERT OR REPLACE INTO public_index_meta (key, value, updated_at) VALUES (?, ?, ?)",
        ("schema_version", SCHEMA_VERSION, now),
    )
    connection.execute(
        "INSERT OR IGNORE INTO public_index_migrations (id, version, checksum, applied_at) VALUES (?, ?, ?, ?)",
        (MIGRATION_ID, SCHEMA_VERSION, MIGRATION_CHECKSUM, now),
    )
    connection.commit()
    applied.append({"id": MIGRATION_ID, "version": SCHEMA_VERSION, "checksum": MIGRATION_CHECKSUM})
    return applied


def get_applied_migrations(connection: sqlite3.Connection) -> list[dict[str, object]]:
    try:
        rows = connection.execute(
            "SELECT id, version, checksum, applied_at FROM public_index_migrations ORDER BY applied_at, id"
        ).fetchall()
    except sqlite3.Error:
        return []
    return [
        {"id": str(row[0]), "version": str(row[1]), "checksum": str(row[2]), "applied_at": str(row[3])}
        for row in rows
    ]
