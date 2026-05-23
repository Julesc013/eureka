import unittest

from runtime.source.observation.internet_archive_reviewed_index import (
    build_ia_reviewed_records_from_promotion_previews,
    load_default_ia_promotion_previews,
    load_ia_reviewed_index_policy,
    validate_ia_reviewed_record,
)


class IAReviewedLocalRecordTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_ia_reviewed_index_policy()
        self.records = build_ia_reviewed_records_from_promotion_previews(load_default_ia_promotion_previews(), self.policy)

    def test_reviewed_local_record_invariants_hold(self):
        for record in self.records:
            self.assertEqual((), validate_ia_reviewed_record(record, self.policy))
            self.assertTrue(record["reviewed_local_index_record"])
            self.assertFalse(record["master_index_record"])
            self.assertFalse(record["public_hosted_record"])
            self.assertFalse(record["raw_response_committed"])
            self.assertFalse(record["download_performed"])
            self.assertTrue(record["evidence_ids"])
            self.assertTrue(record["provenance"])
            self.assertTrue(record["uncertainty"])
            self.assertTrue(record["limitations"])

    def test_fixture_and_live_preview_records_are_present(self):
        source_kinds = {record["provenance"].get("source_kind") for record in self.records}
        self.assertIn("ia_fixture_replay", source_kinds)
        self.assertIn("ia_live_probe_preview", source_kinds)


if __name__ == "__main__":
    unittest.main()
