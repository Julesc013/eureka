import sqlite3
import tempfile
import unittest
from pathlib import Path

from runtime.source.cache import SourceCacheStore
from runtime.source.cache.migrations import MIGRATIONS, apply_migrations, get_applied_migrations
from runtime.source.cache.schema import REQUIRED_TABLES, SCHEMA_VERSION


class SourceCacheMigrationTests(unittest.TestCase):
    def test_init_creates_schema(self) -> None:
        with SourceCacheStore.open(":memory:") as store:
            store.init()
            tables = {
                row[0]
                for row in store.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
            self.assertTrue(set(REQUIRED_TABLES).issubset(tables))
            self.assertEqual(SCHEMA_VERSION, store.schema_version())

    def test_repeated_init_is_idempotent(self) -> None:
        with SourceCacheStore.open(":memory:") as store:
            first = store.init()
            second = store.init()
            self.assertEqual(1, len(first))
            self.assertEqual([], second)
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_migration_history_is_recorded_once(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            apply_migrations(connection)
            apply_migrations(connection)
            applied = get_applied_migrations(connection)
            self.assertEqual(1, len(applied))
            self.assertEqual(MIGRATIONS[0].migration_id, applied[0]["id"])
        finally:
            connection.close()

    def test_file_backed_repeated_init_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "cache.sqlite"
            with SourceCacheStore.open(db) as store:
                store.init()
            with SourceCacheStore.open(db) as store:
                store.init()
                self.assertEqual("pass", store.check_integrity()["status"])


if __name__ == "__main__":
    unittest.main()
