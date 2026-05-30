from __future__ import annotations

import unittest

from runtime.seed_batches import (
    build_seed_batch_query_plans,
    load_frontier_media_query_set,
    normalize_seed_batch_candidates,
    run_seed_batch_fixture_candidates,
)


class FrontierMediaCandidateIngestTests(unittest.TestCase):
    def test_fixture_candidates_normalize_to_review_only_records(self) -> None:
        plans = build_seed_batch_query_plans(load_frontier_media_query_set())
        candidates = normalize_seed_batch_candidates(run_seed_batch_fixture_candidates(plans))
        self.assertEqual(12, len(candidates))
        self.assertTrue(all(item["schema_version"] == "candidate_record.v0" for item in candidates))
        self.assertTrue(all(item["accepted_truth"] is False for item in candidates))
        self.assertTrue(all(item["reviewed_record_ref"] is None for item in candidates))


if __name__ == "__main__":
    unittest.main()
