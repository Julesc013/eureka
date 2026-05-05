import json
import tempfile
import unittest
from pathlib import Path

from runtime.source_cache.dry_run import classify_candidate, run_source_cache_dry_run


def candidate(**overrides):
    payload = {
        "schema_version": "0.1.0",
        "candidate_id": "temp-source-cache-candidate",
        "candidate_kind": "source_cache_candidate",
        "source_family": "internet_archive",
        "record_kind": "metadata_summary",
        "source_ref": {"source_id": "internet_archive", "source_label": "Synthetic source"},
        "privacy_status": "public_safe",
        "public_safety_status": "public_safe",
        "evidence_readiness": "evidence_candidate_ready",
        "policy_status": "approved_example",
        "summary": {"summary_text": "Synthetic metadata summary."},
        "limitations": ["Temporary unit-test candidate."],
        "hard_booleans": {
            "local_dry_run": True,
            "live_source_called": False,
            "external_calls_performed": False,
            "connector_runtime_executed": False,
            "source_sync_worker_executed": False,
            "authoritative_source_cache_written": False,
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
            "public_search_runtime_mutated": False,
            "telemetry_exported": False,
            "credentials_used": False,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
        },
    }
    payload.update(overrides)
    return payload


class SourceCacheDryRunRuntimeTests(unittest.TestCase):
    def test_run_source_cache_dry_run_over_synthetic_temp_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCE_CACHE_CANDIDATE.json"
            path.write_text(json.dumps(candidate(), indent=2), encoding="utf-8")
            report = run_source_cache_dry_run([Path(tmp)], strict=True)
        payload = report.to_dict()
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertEqual(payload["candidates_seen"], 1)
        self.assertEqual(payload["candidates_valid"], 1)
        self.assertEqual(payload["source_families"], {"internet_archive": 1})
        self.assertEqual(payload["record_kinds"], {"metadata_summary": 1})
        self.assertTrue(payload["hard_booleans"]["local_dry_run"])
        for key, value in payload["hard_booleans"].items():
            if key != "local_dry_run":
                self.assertFalse(value, key)

    def test_classifies_source_family_and_record_kind(self) -> None:
        summary = classify_candidate(candidate(source_family="github_releases", record_kind="release_metadata_summary"))
        self.assertEqual(summary.source_family, "github_releases")
        self.assertEqual(summary.record_kind, "release_metadata_summary")
        self.assertTrue(summary.valid)

    def test_rejects_private_absolute_path(self) -> None:
        summary = classify_candidate(candidate(summary={"summary_text": "Synthetic C:\\Users\\Alice\\private cache"}))
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

    def test_report_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCE_CACHE_CANDIDATE.json"
            path.write_text(json.dumps(candidate(), indent=2), encoding="utf-8")
            first = run_source_cache_dry_run([Path(tmp)], strict=True).to_dict()
            second = run_source_cache_dry_run([Path(tmp)], strict=True).to_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
