from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.search.hunt import SearchHuntError, SearchHuntSession, SearchHuntStore


class SearchHuntStoreTests(unittest.TestCase):
    def test_store_init_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search_hunt.sqlite"
            with SearchHuntStore.open(path) as store:
                first = store.init()
                second = store.init()
                self.assertTrue(first)
                self.assertEqual([], second)
                self.assertEqual("pass", store.check_integrity()["status"])

    def test_create_list_show_and_summary_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search_hunt.sqlite"
            with SearchHuntStore.open(path) as store:
                store.init()
                created = store.create_session(SearchHuntSession.new("sampleproject"))
                self.assertEqual(created.id, store.get_session(created.id).id)
                self.assertEqual([created.id], [item.id for item in store.list_sessions()])
                summary = store.summarize()
                self.assertEqual(1, summary["total"])
                self.assertEqual(1, summary["by_state"]["created"])
                self.assertIs(summary["workunit_creation_enabled"], False)

    def test_idempotency_key_returns_existing_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search_hunt.sqlite"
            with SearchHuntStore.open(path) as store:
                store.init()
                first = store.create_session(SearchHuntSession.new("sampleproject", idempotency_key="same"))
                second = store.create_session(SearchHuntSession.new("different", idempotency_key="same"))
                self.assertEqual(first.id, second.id)
                self.assertEqual(1, store.summarize()["total"])

    def test_transition_history_and_summary_attachment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search_hunt.sqlite"
            with SearchHuntStore.open(path) as store:
                store.init()
                session = store.create_session(SearchHuntSession.new("sampleproject"))
                store.transition_session(session.id, "running", "start")
                store.attach_search_summary(session.id, {"result_count": 0, "results": []})
                store.attach_absence_summary(session.id, {"local_current_index_absence_only": True})
                self.assertGreaterEqual(len(store.list_transitions(session.id)), 2)
                self.assertEqual(2, len(store.list_summaries(session.id)))
                self.assertIsNotNone(store.get_session(session.id).absence_report_id)

    def test_invalid_transition_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search_hunt.sqlite"
            with SearchHuntStore.open(path) as store:
                store.init()
                session = store.create_session(SearchHuntSession.new("sampleproject"))
                with self.assertRaises(SearchHuntError):
                    store.transition_session(session.id, "complete", "invalid")


if __name__ == "__main__":
    unittest.main()
