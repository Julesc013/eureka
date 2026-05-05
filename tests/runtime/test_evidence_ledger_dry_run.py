import json
import tempfile
import unittest
from pathlib import Path

from runtime.evidence_ledger.dry_run import classify_candidate, run_evidence_ledger_dry_run


def candidate(**overrides):
    payload = {
        "schema_version": "0.1.0",
        "candidate_id": "temp-evidence-ledger-candidate",
        "candidate_kind": "evidence_ledger_candidate",
        "evidence_kind": "source_metadata_observation",
        "claim_kind": "metadata_claim",
        "source_family": "internet_archive",
        "provenance_status": "source_cache_candidate",
        "review_status": "review_required",
        "privacy_status": "public_safe",
        "public_safety_status": "public_safe",
        "rights_risk_status": "metadata_only",
        "promotion_readiness": "review_required",
        "source_ref": {"source_id": "internet_archive", "source_label": "Synthetic source"},
        "provenance_ref": {"provenance_id": "synthetic-source-cache-candidate"},
        "claim": {
            "claim_value": "Synthetic metadata claim.",
            "global_absence_claimed": False,
            "accepted_as_truth": False,
        },
        "observation": {"summary_text": "Synthetic observation.", "raw_payload_included": False},
        "limitations": ["Temporary unit-test candidate."],
        "hard_booleans": {
            "local_dry_run": True,
            "live_source_called": False,
            "external_calls_performed": False,
            "connector_runtime_executed": False,
            "source_sync_worker_executed": False,
            "authoritative_evidence_ledger_written": False,
            "evidence_ledger_mutated": False,
            "source_cache_mutated": False,
            "candidate_index_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
            "public_search_runtime_mutated": False,
            "claim_accepted_as_truth": False,
            "promotion_decision_created": False,
            "telemetry_exported": False,
            "credentials_used": False,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
        },
    }
    payload.update(overrides)
    return payload


class EvidenceLedgerDryRunRuntimeTests(unittest.TestCase):
    def test_run_evidence_ledger_dry_run_over_synthetic_temp_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVIDENCE_LEDGER_CANDIDATE.json"
            path.write_text(json.dumps(candidate(), indent=2), encoding="utf-8")
            report = run_evidence_ledger_dry_run([Path(tmp)], strict=True)
        payload = report.to_dict()
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertEqual(payload["candidates_seen"], 1)
        self.assertEqual(payload["candidates_valid"], 1)
        self.assertEqual(payload["evidence_kinds"], {"source_metadata_observation": 1})
        self.assertEqual(payload["claim_kinds"], {"metadata_claim": 1})
        self.assertEqual(payload["source_families"], {"internet_archive": 1})
        self.assertTrue(payload["hard_booleans"]["local_dry_run"])
        for key, value in payload["hard_booleans"].items():
            if key != "local_dry_run":
                self.assertFalse(value, key)

    def test_classifies_candidate_dimensions(self) -> None:
        summary = classify_candidate(
            candidate(
                evidence_kind="release_metadata_observation",
                claim_kind="version_claim",
                source_family="github_releases",
                review_status="conflict_review_required",
            )
        )
        self.assertEqual(summary.evidence_kind, "release_metadata_observation")
        self.assertEqual(summary.claim_kind, "version_claim")
        self.assertEqual(summary.source_family, "github_releases")
        self.assertEqual(summary.review_status, "conflict_review_required")
        self.assertTrue(summary.valid)

    def test_rejects_private_absolute_path(self) -> None:
        summary = classify_candidate(candidate(observation={"summary_text": "Synthetic C:\\Users\\Alice\\private path"}))
        self.assertFalse(summary.valid)
        self.assertTrue(any("private" in error for error in summary.errors))

    def test_rejects_url_and_live_source_fields(self) -> None:
        summary = classify_candidate(candidate(url="synthetic-url-field", live_source="internet_archive"))
        self.assertFalse(summary.valid)
        self.assertTrue(any("forbidden field" in error for error in summary.errors))

    def test_detects_secret_like_keys(self) -> None:
        summary = classify_candidate(candidate(api_key="redacted-test-key"))
        self.assertFalse(summary.valid)
        self.assertTrue(any("forbidden field" in error for error in summary.errors))

    def test_detects_truth_acceptance(self) -> None:
        mutated = candidate()
        mutated["claim"] = dict(mutated["claim"])
        mutated["claim"]["accepted_as_truth"] = True
        summary = classify_candidate(mutated)
        self.assertFalse(summary.valid)
        self.assertTrue(any("accepted_as_truth" in error for error in summary.errors))

    def test_detects_promotion_decision_fields(self) -> None:
        summary = classify_candidate(candidate(promotion_decision_created=True))
        self.assertFalse(summary.valid)
        self.assertTrue(any("promotion" in error for error in summary.errors))

    def test_report_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVIDENCE_LEDGER_CANDIDATE.json"
            path.write_text(json.dumps(candidate(), indent=2), encoding="utf-8")
            first = run_evidence_ledger_dry_run([Path(tmp)], strict=True).to_dict()
            second = run_evidence_ledger_dry_run([Path(tmp)], strict=True).to_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
