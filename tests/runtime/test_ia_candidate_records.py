import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_candidate_index import (
    build_ia_candidates_from_evidence,
    load_default_ia_evidence_candidates,
    load_ia_candidate_policy,
    validate_ia_candidate_record,
)


ROOT = Path(__file__).resolve().parents[2]


class IACandidateRecordTests(unittest.TestCase):
    def test_build_candidates_from_fixture_evidence_candidates(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        evidence_candidates = [
            item for item in load_default_ia_evidence_candidates() if item["provenance"]["source_kind"] == "ia_fixture_replay"
        ]
        candidates = build_ia_candidates_from_evidence(evidence_candidates, policy)
        self.assertTrue(candidates)
        self.assertTrue(all(candidate["review_required"] for candidate in candidates))
        self.assertFalse(any(candidate["accepted_truth"] for candidate in candidates))
        self.assertEqual((), validate_ia_candidate_record(candidates[0], policy))

    def test_build_candidates_from_live_preview_evidence_candidates(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        evidence_candidates = [
            item for item in load_default_ia_evidence_candidates() if item["provenance"]["source_kind"] == "ia_live_probe_preview"
        ]
        candidates = build_ia_candidates_from_evidence(evidence_candidates, policy)
        self.assertTrue(candidates)
        self.assertTrue(all(candidate["provenance"]["source_kind"] == "ia_live_probe_preview" for candidate in candidates))
        self.assertTrue(any(candidate["candidate_kind"] == "ia_source_locator_candidate" for candidate in candidates))

    def test_expected_candidate_kinds_are_generated_where_present(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        candidates = build_ia_candidates_from_evidence(load_default_ia_evidence_candidates(), policy)
        kinds = {candidate["candidate_kind"] for candidate in candidates}
        for expected in (
            "ia_item_candidate",
            "ia_media_metadata_candidate",
            "ia_file_list_candidate",
            "ia_collection_member_candidate",
            "ia_source_locator_candidate",
        ):
            self.assertIn(expected, kinds)

    def test_candidate_invariants_reject_accepted_truth(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        candidate = build_ia_candidates_from_evidence(load_default_ia_evidence_candidates()[:4], policy)[0]
        candidate["accepted_truth"] = True
        self.assertIn("accepted_truth must be false", validate_ia_candidate_record(candidate, policy))


if __name__ == "__main__":
    unittest.main()
