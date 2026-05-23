import json
import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_source_cache import (
    build_ia_source_cache_boundary_report,
    build_ia_source_cache_record,
    build_ia_source_cache_write_report,
    build_source_cache_store_objects,
    load_fixture_normalized_records,
    load_ia_source_cache_policy,
)


ROOT = Path(__file__).resolve().parents[2]


class IASourceCacheBoundaryTests(unittest.TestCase):
    def test_store_payload_omits_reserved_truth_field(self):
        policy = load_ia_source_cache_policy(ROOT / "control/policies/ia_source_cache_policy.json")
        record = build_ia_source_cache_record(load_fixture_normalized_records(ROOT / "examples/internet_archive_metadata")[0], policy)
        *_, cache_entry = build_source_cache_store_objects(record)
        text = json.dumps(cache_entry.to_dict(), sort_keys=True)
        self.assertNotIn("accepted_truth", text)
        self.assertNotIn("master_index_mutated", text)

    def test_boundary_report_keeps_downstream_mutations_false(self):
        report = build_ia_source_cache_write_report(
            [],
            dry_run=True,
            store_result={"write_applied": False},
            write_scope="dry_run_no_instance_mutation",
        )
        boundary = build_ia_source_cache_boundary_report(report)
        self.assertTrue(boundary["passed"])
        self.assertFalse(boundary["raw_response_committed"])
        self.assertFalse(boundary["evidence_ledger_write_performed"])
        self.assertFalse(boundary["candidate_index_mutated"])
        self.assertFalse(boundary["download_performed"])


if __name__ == "__main__":
    unittest.main()
