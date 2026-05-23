from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.worker.workunit_queue import ALLOWED_WORKUNIT_TYPES, WorkUnit, WorkUnitQueueStore


class WorkUnitQueueStoreTests(unittest.TestCase):
    def test_store_init_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workunit_queue.sqlite"
            with WorkUnitQueueStore.open(path) as store:
                first = store.init()
                second = store.init()
                self.assertTrue(first)
                self.assertEqual([], second)
                self.assertEqual("pass", store.check_integrity()["status"])

    def test_create_list_show_and_summary_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workunit_queue.sqlite"
            with WorkUnitQueueStore.open(path) as store:
                store.init()
                created = store.create_workunit(WorkUnit.new("search_need", "Find a local object"))
                self.assertEqual(created.id, store.get_workunit(created.id).id)
                self.assertEqual([created.id], [item.id for item in store.list_workunits()])
                summary = store.summarize().to_dict()
                self.assertEqual(1, summary["total"])
                self.assertEqual(1, summary["by_state"]["queued"])
                self.assertIs(summary["execution_enabled"], False)

    def test_every_required_type_can_be_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workunit_queue.sqlite"
            with WorkUnitQueueStore.open(path) as store:
                store.init()
                for kind in ALLOWED_WORKUNIT_TYPES:
                    store.create_workunit(WorkUnit.new(kind, f"Sample {kind}"))
                self.assertEqual(set(ALLOWED_WORKUNIT_TYPES), set(store.summarize().by_kind))

    def test_idempotency_key_returns_existing_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "workunit_queue.sqlite"
            with WorkUnitQueueStore.open(path) as store:
                store.init()
                first = store.create_workunit(WorkUnit.new("search_need", "First", idempotency_key="same"))
                second = store.create_workunit(WorkUnit.new("search_need", "Second", idempotency_key="same"))
                self.assertEqual(first.id, second.id)
                self.assertEqual(1, store.summarize().total)


if __name__ == "__main__":
    unittest.main()
