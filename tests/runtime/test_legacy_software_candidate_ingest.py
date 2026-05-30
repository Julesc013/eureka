from __future__ import annotations

import unittest

from runtime.seed_batches import (
    apply_legacy_software_suppressions,
    build_legacy_software_query_plans,
    load_legacy_software_query_set,
    normalize_legacy_software_candidates,
    run_legacy_software_fixture_candidates,
)


class LegacySoftwareCandidateIngestTests(unittest.TestCase):
    def test_fixture_candidates_normalize_to_review_only_records(self) -> None:
        plans = build_legacy_software_query_plans(load_legacy_software_query_set())
        candidates = normalize_legacy_software_candidates(run_legacy_software_fixture_candidates(plans))
        candidates = apply_legacy_software_suppressions(candidates)
        self.assertEqual(16, len(candidates))
        self.assertTrue(all(item["schema_version"] == "candidate_record.v0" for item in candidates))
        self.assertTrue(all(item["accepted_truth"] is False for item in candidates))
        self.assertTrue(all(item["reviewed_record_ref"] is None for item in candidates))


if __name__ == "__main__":
    unittest.main()
