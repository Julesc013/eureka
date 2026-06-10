from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_artifact_evidence_return.py"


class ValidateArtifactEvidenceReturnScriptTestCase(unittest.TestCase):
    def test_valid_minimal_return_passes_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact_evidence_collection_summary.json"
            path.write_text(json.dumps(_valid_payload(), indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json", "--strict"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["target_result_count"], 2)
        self.assertFalse(payload["truth_created"])

    def test_missing_default_return_fails_cleanly(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(any("file is missing" in error for error in payload["errors"]))

    def test_rejects_verified_artifact_truth_claim(self) -> None:
        payload = _valid_payload()
        payload["target_results"][0]["truth_boundary"]["verified_artifact_created"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "return.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("verified_artifact_created" in error for error in report["errors"]))

    def test_rejects_driver_result_without_hardware_identity(self) -> None:
        payload = _valid_payload()
        payload["target_results"][1]["status"] = "evidence_collected"
        payload["target_results"][1]["recommended_review_action"] = "promote_to_review_candidate"
        payload["target_results"][1]["observed_fields"] = {"artifact_evidence_level": "level2_source_observed_artifact_listing"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "driver.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("lacks hardware identity" in error for error in report["errors"]))

    def test_rejects_private_absolute_path(self) -> None:
        payload = _valid_payload()
        payload["target_results"][0]["observed_fields"]["observed_url_or_locator"] = r"C:\Users\Alice\Downloads\driver.exe"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "private_path.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("private or absolute local evidence paths" in error for error in report["errors"]))


def _valid_payload() -> dict:
    return {
        "schema_version": "artifact_evidence_collection_return.v0",
        "run_id": "test-run",
        "collected_at": "2026-06-11T00:00:00Z",
        "collector": "unit-test",
        "target_results": [
            {
                "target_id": "collect_b02_7zip_2601_integrity",
                "status": "evidence_collected",
                "artifact_evidence_level": "level4_artifact_integrity_evidence",
                "source_refs": ["src_7zip_release"],
                "observed_fields": {
                    "artifact_name": "7-Zip",
                    "artifact_version": "26.01",
                    "checksum_or_signature": "source-published checksum observed"
                },
                "remaining_gaps": ["human review required"],
                "recommended_review_action": "promote_to_review_candidate",
                "truth_boundary": {
                    "reviewed_artifact_record_created": False,
                    "verified_artifact_created": False,
                    "rights_clearance_claimed": False,
                    "malware_safety_claimed": False,
                    "download_or_execution_performed": False
                }
            },
            {
                "target_id": "collect_win98_driver_hardware_identity",
                "status": "blocked",
                "source_refs": [],
                "observed_fields": {},
                "remaining_gaps": ["hardware vendor", "hardware model", "chipset", "device id"],
                "recommended_review_action": "mark_blocked_for_user_details"
            }
        ],
        "raw_artifacts_retained_outside_repo": False,
        "downloads_performed": False,
        "executables_fetched": False,
        "install_or_execution_performed": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "resume_recommended_task": "MANUAL-ARTIFACT-OBSERVATION-BATCH-03"
    }


if __name__ == "__main__":
    unittest.main()
