import tempfile
import unittest
from pathlib import Path

from runtime.evidence_ledger import EvidenceLedgerStore
from runtime.source_observation.internet_archive_evidence import (
    build_ia_evidence_candidate_records,
    load_default_ia_source_cache_records,
    load_ia_evidence_policy,
    write_ia_evidence_candidates,
)


ROOT = Path(__file__).resolve().parents[2]


class IAEvidenceLedgerIntegrationTests(unittest.TestCase):
    def test_dry_run_does_not_mutate_evidence_store(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        candidates = build_ia_evidence_candidate_records(
            load_default_ia_source_cache_records(include_live_preview=False)[:1],
            policy,
        )
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            result = write_ia_evidence_candidates(store, candidates, dry_run=True)
            self.assertFalse(result["write_applied"])
            self.assertEqual(0, store.summarize().evidence_candidate_count)

    def test_apply_writes_fixture_and_live_preview_candidates_to_temp_store(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        source_records = load_default_ia_source_cache_records(include_fixtures=True, include_live_preview=True)
        candidates = build_ia_evidence_candidate_records(source_records, policy)
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_fixture_replay" for item in candidates))
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_live_probe_preview" for item in candidates))
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "evidence_ledger.sqlite"
            with EvidenceLedgerStore.open(db) as store:
                result = write_ia_evidence_candidates(store, candidates, dry_run=False)
                self.assertTrue(result["write_applied"])
                self.assertEqual(len(candidates), result["summary"]["evidence_candidate_count"])
                self.assertEqual("pass", result["integrity"]["status"])


if __name__ == "__main__":
    unittest.main()
