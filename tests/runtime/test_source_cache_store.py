import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.demo_source_cache_store import build_demo_objects, run_demo

from runtime.source_cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source_cache.errors import SourceCacheValidationError
from runtime.source_cache.validation import validate_cache_payload


class SourceCacheStoreTests(unittest.TestCase):
    def make_store_with_entry(self):
        source_record, response, source_observation, normalized = build_demo_objects()
        store = SourceCacheStore.open(":memory:")
        store.init()
        store.write_source_record(source_record)
        store.write_metadata_response(response)
        store.write_source_observation(source_observation)
        store.write_normalized_observation(normalized)
        entry = build_cache_entry(source_record, response, source_observation, normalized)
        store.write_cache_entry(entry)
        return store, source_record, response, source_observation, normalized, entry

    def test_in_memory_store_works(self) -> None:
        store, source_record, *_ = self.make_store_with_entry()
        try:
            self.assertEqual(source_record, store.get_source_record(str(source_record.source_id)))
            self.assertEqual(1, store.summarize().cache_entry_count)
        finally:
            store.close()

    def test_file_backed_tempdir_store_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "cache.sqlite"
            result = run_demo(db)
            self.assertEqual("pass", result["status"])
            self.assertTrue(db.is_file())

    def test_invalid_db_path_is_rejected(self) -> None:
        with self.assertRaises(SourceCacheValidationError):
            SourceCacheStore.open("runtime/source-cache.sqlite")

    def test_hidden_private_roots_are_rejected(self) -> None:
        with self.assertRaises(SourceCacheValidationError):
            SourceCacheStore.open(".cache/source-cache.sqlite")

    def test_write_read_source_record_works(self) -> None:
        store, source_record, *_ = self.make_store_with_entry()
        try:
            read = store.get_source_record(str(source_record.source_id))
            self.assertEqual(source_record.source_family, read.source_family)
        finally:
            store.close()

    def test_write_read_metadata_response_works(self) -> None:
        store, _, response, *_ = self.make_store_with_entry()
        try:
            row = store.connection.execute(
                "SELECT payload_json FROM metadata_responses WHERE response_id = ?",
                (response.response_id,),
            ).fetchone()
            self.assertEqual(response.to_dict(), json.loads(row[0]))
        finally:
            store.close()

    def test_write_read_source_observation_works(self) -> None:
        store, _, _, source_observation, *_ = self.make_store_with_entry()
        try:
            row = store.connection.execute(
                "SELECT payload_json FROM source_observations WHERE observation_id = ?",
                (source_observation.observation_id,),
            ).fetchone()
            self.assertEqual(source_observation.to_dict(), json.loads(row[0]))
        finally:
            store.close()

    def test_write_read_normalized_observation_works(self) -> None:
        store, _, _, _, normalized, _ = self.make_store_with_entry()
        try:
            row = store.connection.execute(
                "SELECT payload_json FROM normalized_observations WHERE normalized_observation_id = ?",
                (normalized.normalized_observation_id,),
            ).fetchone()
            self.assertEqual(normalized.to_dict(), json.loads(row[0]))
        finally:
            store.close()

    def test_write_read_source_cache_entry_works(self) -> None:
        store, *_, entry = self.make_store_with_entry()
        try:
            read = store.get_cache_entry(entry.entry_id)
            self.assertEqual(entry.entry_id, read.entry_id)
            self.assertEqual(SourceCacheStatus.CACHED, read.status)
        finally:
            store.close()

    def test_list_by_source_id_and_status_works(self) -> None:
        store, source_record, *_, entry = self.make_store_with_entry()
        try:
            by_source = store.list_cache_entries(source_id=str(source_record.source_id))
            by_status = store.list_cache_entries(status=SourceCacheStatus.CACHED)
            self.assertEqual([entry.entry_id], [item.entry_id for item in by_source])
            self.assertEqual([entry.entry_id], [item.entry_id for item in by_status])
        finally:
            store.close()

    def test_summarize_and_integrity_pass(self) -> None:
        store, *_ = self.make_store_with_entry()
        try:
            self.assertEqual(1, store.summarize().source_record_count)
            self.assertEqual("pass", store.check_integrity()["status"])
        finally:
            store.close()

    def test_payload_with_accepted_truth_field_is_rejected(self) -> None:
        self.assertTrue(validate_cache_payload({"accepted_truth": True}))

    def test_store_does_not_create_downstream_tables(self) -> None:
        store, *_ = self.make_store_with_entry()
        try:
            tables = {
                row[0]
                for row in store.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
            self.assertNotIn("evidence_ledger", tables)
            self.assertNotIn("review_queue", tables)
            self.assertNotIn("public_index", tables)
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
