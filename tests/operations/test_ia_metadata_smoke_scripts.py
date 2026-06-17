from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IAMetadataSmokeScriptTests(unittest.TestCase):
    def test_fixture_smoke_json_preserves_boundaries(self) -> None:
        payload = _run_smoke("--mode", "fixture")

        self.assertEqual("PASS", payload["status"], payload)
        self.assertEqual(7, payload["query_count"])
        self.assertEqual("PASS", payload["fixture_smoke"]["status"])
        self.assertEqual("not_requested", payload["live_smoke"]["status"])
        self.assertGreater(payload["totals"]["source_observations_created"], 0)
        self.assertGreater(payload["totals"]["evidence_summaries_created"], 0)
        self.assertGreater(payload["totals"]["candidates_created"], 0)
        self.assertGreater(payload["totals"]["review_previews_created"], 0)
        self.assertFalse(payload["candidate_index_delta"]["candidate_index_mutated"])
        self.assertFalse(payload["review_queue_preview"]["review_queue_mutated"])
        self.assertFalse(payload["safety"]["reviewed_master_index_mutation"])
        self.assertFalse(payload["safety"]["public_fanout"])
        self.assertFalse(payload["safety"]["downloads"])
        self.assertFalse(payload["safety"]["file_fetching"])
        self.assertFalse(payload["safety"]["wayback_replay"])
        self.assertFalse(payload["safety"]["rights_safety_claims"])

    def test_live_mode_without_operator_opt_in_reports_blocked(self) -> None:
        payload = _run_smoke("--mode", "live")

        self.assertEqual("PASS_WITH_WARNINGS", payload["status"], payload)
        self.assertEqual("not_requested", payload["fixture_smoke"]["status"])
        self.assertEqual("operator_blocked", payload["live_smoke"]["status"])
        self.assertFalse(payload["live_smoke"]["live_metadata_request_performed"])
        self.assertEqual(0, payload["live_smoke"]["total_http_requests"])
        self.assertFalse(payload["safety"]["public_fanout"])
        self.assertFalse(payload["safety"]["downloads"])

    def test_output_and_audit_files_are_written(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-smoke-test-") as tmp:
            tmp_path = Path(tmp)
            payload = _run_smoke(
                "--mode",
                "fixture",
                "--out",
                str(tmp_path / "out"),
                "--audit-dir",
                str(tmp_path / "audit"),
            )

            self.assertEqual("PASS", payload["status"], payload)
            self.assertTrue((tmp_path / "out" / "ia_metadata_provider_smoke_report.json").exists())
            self.assertTrue((tmp_path / "out" / "SMOKE_RESULTS.md").exists())
            self.assertTrue((tmp_path / "audit" / "ia_metadata_provider_smoke_report.json").exists())
            self.assertTrue((tmp_path / "audit" / "SMOKE_RESULTS.md").exists())


def _run_smoke(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_ia_metadata_smoke.py", *args, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=90,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
