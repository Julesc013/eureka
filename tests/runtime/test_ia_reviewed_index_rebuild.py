import tempfile
import unittest
from pathlib import Path

from runtime.public_index import PublicIndexStore
from runtime.source_observation.internet_archive_reviewed_index import (
    build_ia_reviewed_index_rebuild_report,
    build_ia_reviewed_records_from_promotion_previews,
    load_default_ia_promotion_previews,
    load_ia_reviewed_index_policy,
    rebuild_ia_reviewed_local_index,
)


class IAReviewedIndexRebuildTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_ia_reviewed_index_policy()
        self.records = build_ia_reviewed_records_from_promotion_previews(load_default_ia_promotion_previews(), self.policy)

    def test_builds_reviewed_local_records_from_promotion_previews(self):
        self.assertGreater(len(self.records), 0)
        self.assertTrue(all(record["reviewed_local_index_record"] for record in self.records))

    def test_dry_run_does_not_create_public_index_db(self):
        with tempfile.TemporaryDirectory(prefix="eureka-ia07-test-") as tmp:
            db_path = Path(tmp) / "public_index.sqlite"
            result = rebuild_ia_reviewed_local_index(None, self.records, dry_run=True)
            report = build_ia_reviewed_index_rebuild_report(self.records, True, result, "dry_run_no_instance_mutation")
            self.assertFalse(db_path.exists())
            self.assertFalse(report["reviewed_index_mutated"])

    def test_apply_writes_reviewed_records_to_explicit_temp_store(self):
        with tempfile.TemporaryDirectory(prefix="eureka-ia07-test-") as tmp:
            db_path = Path(tmp) / "public_index.sqlite"
            with PublicIndexStore.open(db_path) as store:
                result = rebuild_ia_reviewed_local_index(store, self.records[:3], dry_run=False)
                self.assertTrue(result["write_applied"])
                self.assertEqual(3, store.summarize().record_count)


if __name__ == "__main__":
    unittest.main()
