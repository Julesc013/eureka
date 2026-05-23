import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_source_cache import (
    build_ia_source_cache_record,
    load_fixture_normalized_records,
    load_ia_source_cache_policy,
    load_live_preview_records,
    validate_ia_source_cache_record,
)


ROOT = Path(__file__).resolve().parents[2]


class IASourceCacheRecordTests(unittest.TestCase):
    def test_build_source_cache_record_from_fixture(self):
        policy = load_ia_source_cache_policy(ROOT / "control/policies/ia_source_cache_policy.json")
        source = load_fixture_normalized_records(ROOT / "examples/internet_archive_metadata")[0]
        record = build_ia_source_cache_record(source, policy)
        self.assertEqual("internet_archive_metadata", record["source_id"])
        self.assertEqual("ia_fixture_replay", record["source_kind"])
        self.assertTrue(record["review_required"])
        self.assertFalse(record["accepted_truth"])
        self.assertFalse(record["download_performed"])
        self.assertEqual((), validate_ia_source_cache_record(record, policy))

    def test_build_source_cache_record_from_live_preview(self):
        policy = load_ia_source_cache_policy(ROOT / "control/policies/ia_source_cache_policy.json")
        source = load_live_preview_records(ROOT / "control/inventory/ia_02_tls_continue_normalized_preview.json")[0]
        record = build_ia_source_cache_record(source, policy, live_probe_id="test")
        self.assertEqual("ia_live_probe_preview", record["source_kind"])
        self.assertEqual("test", record["live_probe_id"])
        self.assertTrue(record["title_candidate_present"])
        self.assertFalse(record["raw_response_committed"])

    def test_record_invariants_reject_truth_claims(self):
        policy = load_ia_source_cache_policy(ROOT / "control/policies/ia_source_cache_policy.json")
        source = load_fixture_normalized_records(ROOT / "examples/internet_archive_metadata")[0]
        record = build_ia_source_cache_record(source, policy)
        record["accepted_truth"] = True
        self.assertIn("accepted_truth must be false", validate_ia_source_cache_record(record, policy))


if __name__ == "__main__":
    unittest.main()
