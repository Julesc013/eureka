import sqlite3
import tempfile
import unittest
from pathlib import Path

from runtime.evidence_ledger import EvidenceLedgerStore
from runtime.evidence_ledger.migrations import MIGRATIONS, apply_migrations, get_applied_migrations
from runtime.evidence_ledger.schema import REQUIRED_TABLES, SCHEMA_VERSION


class EvidenceLedgerMigrationTests(unittest.TestCase):
    def test_repeated_init_is_idempotent(self):
        with EvidenceLedgerStore.open(":memory:") as store:
            first = store.init()
            second = store.init()
            self.assertEqual(1, len(first))
            self.assertEqual([], second)
            self.assertEqual(SCHEMA_VERSION, store.schema_version())

    def test_required_tables_exist(self):
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            tables = {
                row[0]
                for row in store.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
            self.assertTrue(set(REQUIRED_TABLES).issubset(tables))

    def test_migration_history_is_recorded(self):
        connection = sqlite3.connect(":memory:")
        try:
            apply_migrations(connection)
            history = get_applied_migrations(connection)
            self.assertEqual(MIGRATIONS[0].migration_id, history[0]["id"])
        finally:
            connection.close()

    def test_file_backed_repeated_init_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            with EvidenceLedgerStore.open(path) as store:
                store.init()
            with EvidenceLedgerStore.open(path) as store:
                store.init()
                self.assertEqual("pass", store.check_integrity()["status"])


if __name__ == "__main__":
    unittest.main()
