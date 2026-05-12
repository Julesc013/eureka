import tempfile
import unittest
from pathlib import Path

from runtime.public_index import PublicIndexRecord, PublicIndexStore
from runtime.public_index.errors import PublicIndexValidationError
from runtime.public_index.validation import (
    validate_no_public_truth_fields,
    validate_public_index_path,
)


def make_record(record_id: str = "pir_0123456789abcdef") -> PublicIndexRecord:
    return PublicIndexRecord(
        record_id=record_id,
        source_id="source.example.metadata",
        source_cache_entry_id="sce_test",
        evidence_id="evc_test",
        review_item_id="rvi_test",
        review_decision_id="rvd_test",
        title="demo-project",
        description="Synthetic metadata for local review",
        normalized_fields={"name": "demo-project", "summary": "Synthetic metadata"},
        searchable_text="demo project synthetic metadata source example",
        source_family="package_registry",
        trust_lane="synthetic",
    )


class PublicIndexStoreTests(unittest.TestCase):
    def test_init_creates_schema(self):
        with PublicIndexStore.open(":memory:") as store:
            applied = store.init()
            self.assertEqual(1, len(applied))
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_repeated_init_is_idempotent(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.init()
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_in_memory_store_works(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.write_record(make_record())
            self.assertEqual(1, store.summarize().record_count)

    def test_file_backed_tempdir_store_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "public.sqlite"
            with PublicIndexStore.open(db) as store:
                store.init()
                store.write_record(make_record())
            with PublicIndexStore.open(db) as store:
                store.init()
                self.assertIsNotNone(store.get_record("pir_0123456789abcdef"))

    def test_invalid_db_path_is_rejected(self):
        with self.assertRaises(PublicIndexValidationError):
            PublicIndexStore.open("runtime/public-index.sqlite")

    def test_hidden_default_private_and_site_dist_roots_are_rejected(self):
        self.assertTrue(validate_public_index_path(".cache/public.sqlite"))
        self.assertTrue(validate_public_index_path("site/dist/public.sqlite"))

    def test_write_read_public_index_record_works(self):
        record = make_record()
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.write_record(record)
            fetched = store.get_record(record.record_id)
            self.assertEqual(record.source_id, fetched.source_id)
            self.assertEqual(record.evidence_id, fetched.evidence_id)
            self.assertEqual(record.review_item_id, fetched.review_item_id)

    def test_list_search_summary_and_integrity_work(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            store.write_record(make_record())
            self.assertEqual(1, len(store.list_records(source_id="source.example.metadata")))
            self.assertEqual(1, len(store.search("demo")))
            self.assertEqual(1, store.summarize().source_ref_count)
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_serialized_record_contains_no_reserved_boundary_fields(self):
        text = make_record().to_json()
        self.assertNotIn("truth_boundary", text)
        self.assertNotIn("product_boundary", text)

    def test_payload_with_source_truth_field_is_rejected(self):
        self.assertTrue(validate_no_public_truth_fields({"source_truth": True}))

    def test_payload_with_production_ready_field_is_rejected(self):
        self.assertTrue(validate_no_public_truth_fields({"production_ready": True}))

    def test_store_does_not_create_master_or_site_tables(self):
        with PublicIndexStore.open(":memory:") as store:
            store.init()
            tables = {row[0] for row in store.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            self.assertNotIn("master_index", tables)
            self.assertNotIn("site_dist", tables)


if __name__ == "__main__":
    unittest.main()
