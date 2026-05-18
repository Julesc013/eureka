import tempfile
import unittest
from pathlib import Path

from runtime.candidate_index import CandidateIndexStore
from runtime.source_observation.internet_archive_candidate_index import (
    build_ia_candidates_from_evidence,
    load_default_ia_evidence_candidates,
    load_ia_candidate_policy,
    write_ia_candidate_records,
)


ROOT = Path(__file__).resolve().parents[2]


class IACandidateIndexIntegrationTests(unittest.TestCase):
    def test_dry_run_does_not_mutate_candidate_store(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        candidates = build_ia_candidates_from_evidence(load_default_ia_evidence_candidates()[:4], policy)
        with tempfile.TemporaryDirectory() as tmp:
            store = CandidateIndexStore.open(Path(tmp) / "ia_candidate_index.json")
            store.init()
            result = write_ia_candidate_records(store, candidates, dry_run=True)
            self.assertFalse(result["write_applied"])
            self.assertEqual(0, store.summarize()["candidate_count"])

    def test_apply_writes_fixture_and_live_preview_candidates_to_temp_store(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        candidates = build_ia_candidates_from_evidence(load_default_ia_evidence_candidates(), policy)
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_fixture_replay" for item in candidates))
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_live_probe_preview" for item in candidates))
        with tempfile.TemporaryDirectory() as tmp:
            store = CandidateIndexStore.open(Path(tmp) / "ia_candidate_index.json")
            result = write_ia_candidate_records(store, candidates, dry_run=False)
            self.assertTrue(result["write_applied"])
            self.assertEqual(len(candidates), result["summary"]["candidate_count"])
            self.assertEqual(len(candidates), store.summarize()["review_required_count"])


if __name__ == "__main__":
    unittest.main()
