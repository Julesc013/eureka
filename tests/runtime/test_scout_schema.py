from __future__ import annotations

from pathlib import Path
import unittest

from runtime.local.eval.scout_schema import (
    BLOCKED_ACTIONS,
    load_scout_example_records,
    load_scout_seed_records,
    validate_discovery_candidate,
    validate_discovery_trail,
    validate_scout_seed,
    validate_source_trust_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "examples/scout/scout_seed_manifest.json"


class ScoutSchemaRuntimeTests(unittest.TestCase):
    def test_example_seeds_load_and_validate(self) -> None:
        seeds = load_scout_seed_records(MANIFEST)
        self.assertGreaterEqual(len(seeds), 5)
        for seed in seeds:
            with self.subTest(seed_id=seed["seed_id"]):
                report = validate_scout_seed(seed)
                self.assertEqual(report["status"], "valid", report["errors"])
                self.assertFalse(seed["accepted_truth"])
                self.assertTrue(seed["review_required"])

    def test_candidate_trail_and_source_trust_validate(self) -> None:
        records = load_scout_example_records(REPO_ROOT)
        reports = [
            validate_discovery_candidate(records["candidate"]),
            validate_discovery_trail(records["trail"]),
            validate_source_trust_record(records["source_trust_record"]),
        ]
        for report in reports:
            self.assertEqual(report["status"], "valid", report["errors"])

    def test_discovery_candidate_is_candidate_only(self) -> None:
        candidate = load_scout_example_records(REPO_ROOT)["candidate"]
        self.assertEqual(candidate["review_state"], "candidate")
        self.assertEqual(candidate["evidence_refs"], [])
        self.assertFalse(candidate["accepted_truth"])
        self.assertFalse(candidate["non_claims"]["evidence_created"])
        self.assertFalse(candidate["non_claims"]["index_mutated"])

    def test_blocked_actions_cover_unsafe_boundaries(self) -> None:
        for action in ("live_source_call", "source_probe", "crawl", "download", "extract", "call_model_provider", "mutate_master_index"):
            self.assertIn(action, BLOCKED_ACTIONS)


if __name__ == "__main__":
    unittest.main()
