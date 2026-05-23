import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_evidence import (
    build_ia_evidence_candidates,
    build_ia_evidence_candidate_records,
    load_default_ia_source_cache_records,
    load_ia_evidence_policy,
    validate_ia_evidence_candidate,
)


ROOT = Path(__file__).resolve().parents[2]


class IAEvidenceRecordTests(unittest.TestCase):
    def test_build_evidence_candidates_from_fixture_source_cache_record(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        source_record = load_default_ia_source_cache_records(include_live_preview=False)[0]
        candidates = build_ia_evidence_candidates(source_record, policy)
        self.assertTrue(candidates)
        self.assertTrue(all(candidate["review_required"] for candidate in candidates))
        self.assertFalse(any(candidate["accepted_truth"] for candidate in candidates))
        self.assertEqual((), validate_ia_evidence_candidate(candidates[0], policy))

    def test_build_evidence_candidates_from_live_preview_source_cache_record(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        source_record = load_default_ia_source_cache_records(include_fixtures=False)[0]
        candidates = build_ia_evidence_candidates(source_record, policy)
        claim_kinds = {candidate["claim_kind"] for candidate in candidates}
        self.assertIn("title_claim_candidate", claim_kinds)
        self.assertIn("source_locator_claim_candidate", claim_kinds)
        self.assertTrue(all(candidate["provenance"]["source_kind"] == "ia_live_probe_preview" for candidate in candidates))

    def test_expected_claim_kinds_are_generated_where_present(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        candidates = build_ia_evidence_candidate_records(load_default_ia_source_cache_records(), policy)
        claim_kinds = {candidate["claim_kind"] for candidate in candidates}
        for expected in (
            "title_claim_candidate",
            "mediatype_claim_candidate",
            "collection_claim_candidate",
            "file_metadata_claim_candidate",
            "checksum_metadata_claim_candidate",
            "source_locator_claim_candidate",
        ):
            self.assertIn(expected, claim_kinds)

    def test_candidate_invariants_reject_accepted_truth(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        source_record = load_default_ia_source_cache_records(include_live_preview=False)[0]
        candidate = build_ia_evidence_candidates(source_record, policy)[0]
        candidate["accepted_truth"] = True
        self.assertIn("accepted_truth must be false", validate_ia_evidence_candidate(candidate, policy))


if __name__ == "__main__":
    unittest.main()
