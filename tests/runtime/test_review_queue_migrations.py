import unittest

from runtime.review_queue.migrations import MIGRATIONS
from runtime.review_queue import ReviewQueueStore
from runtime.review_queue.schema import REQUIRED_TABLES, SCHEMA_VERSION


class ReviewQueueMigrationTests(unittest.TestCase):
    def test_repeated_init_is_idempotent(self):
        with ReviewQueueStore.open(":memory:") as store:
            first = store.init()
            second = store.init()
            self.assertEqual(1, len(first))
            self.assertEqual([], second)
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_schema_version_is_deterministic(self):
        self.assertEqual("review_queue_store.v0", SCHEMA_VERSION)
        self.assertEqual(SCHEMA_VERSION, MIGRATIONS[0].version)

    def test_required_tables_are_created(self):
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            rows = store.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            tables = {str(row[0]) for row in rows}
            self.assertTrue(set(REQUIRED_TABLES).issubset(tables))

    def test_migration_history_is_recorded(self):
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            history = store.check_integrity()["applied_migrations"]
            self.assertEqual("001_initial_review_queue_store", history[0]["id"])


if __name__ == "__main__":
    unittest.main()
