from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_external_baseline_observations.py"
REPORTER = REPO_ROOT / "scripts" / "report_external_baseline_status.py"


class ExternalBaselineObservationScriptTest(unittest.TestCase):
    def test_validator_accepts_committed_pending_observations(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["query_count"], 64)
        for system_id, counts in payload["status_counts_by_system"].items():
            with self.subTest(system_id=system_id):
                self.assertEqual(counts["pending_manual_observation"], 64)
                self.assertNotIn("observed", counts)
        self.assertIn("batch_0", payload["batches"])
        batch = payload["batches"]["batch_0"]
        self.assertEqual(batch["selected_query_count"], 13)
        self.assertEqual(batch["expected_observation_count"], 39)
        self.assertEqual(batch["pending_observation_count"], 39)
        self.assertEqual(batch["observed_observation_count"], 0)

    def test_validator_plain_text_summary(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Manual external baseline observations", completed.stdout)
        self.assertIn("google_web_search", completed.stdout)
        self.assertIn("pending=64", completed.stdout)
        self.assertIn("batch_0", completed.stdout)
        self.assertIn("expected=39", completed.stdout)

    def test_reporter_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(REPORTER)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        structured = subprocess.run(
            [sys.executable, str(REPORTER), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(structured.stdout)

        self.assertIn("External baseline observation status", plain.stdout)
        self.assertIn("batch_0", plain.stdout)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["global_slot_counts"]["pending_manual_observation"], 192)
        self.assertEqual(payload["missing_observation_slots"]["google_web_search"], 64)
        self.assertEqual(payload["batches"]["batch_0"]["pending_observation_count"], 39)
        self.assertEqual(payload["batches"]["batch_0"]["completion_percent"], 0.0)

    def test_validator_rejects_observed_record_missing_metadata(self) -> None:
        record = {
            "observation_id": "bad",
            "query_id": "windows_7_apps",
            "query_text": "Windows 7 apps",
            "system_id": "google_web_search",
            "observation_status": "observed",
            "collection_method": "manual",
            "top_results": [],
            "usefulness_scores": {"overall": 2},
        }

        completed = self._run_validator_with_record(record)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("observed record missing operator", completed.stdout)
        self.assertIn("observed record missing observed_at", completed.stdout)

    def test_validator_rejects_unknown_system_id(self) -> None:
        record = self._valid_pending_record()
        record["system_id"] = "unknown_search"

        completed = self._run_validator_with_record(record)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unknown system_id", completed.stdout)

    def test_validator_rejects_scores_outside_range(self) -> None:
        record = self._valid_pending_record()
        record["usefulness_scores"] = {"overall": 4}

        completed = self._run_validator_with_record(record)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("score overall must be an integer from 0 to 3", completed.stdout)

    def test_validator_rejects_scraped_or_automated_method(self) -> None:
        record = self._valid_pending_record()
        record["collection_method"] = "scraped"

        completed = self._run_validator_with_record(record)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("collection_method must be manual", completed.stdout)

    def _run_validator_with_record(self, record: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            observations_dir = Path(temp_dir)
            (observations_dir / "record.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--json",
                    "--observations-dir",
                    str(observations_dir),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

    def _valid_pending_record(self) -> dict:
        return {
            "observation_id": "pending",
            "query_id": "windows_7_apps",
            "query_text": "Windows 7 apps",
            "system_id": "google_web_search",
            "observation_status": "pending_manual_observation",
            "collection_method": "manual",
            "top_results": [],
            "first_useful_result_rank": None,
            "usefulness_scores": {"overall": 0},
            "failure_modes": ["external_baseline_pending"],
            "next_eureka_work": [],
            "evidence_limitations": ["Pending placeholder only."],
            "created_by": "test",
            "schema_version": "manual_external_baseline_observation.v0",
        }


if __name__ == "__main__":
    unittest.main()
