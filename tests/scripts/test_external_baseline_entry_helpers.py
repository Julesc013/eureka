from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
LIST_HELPER = REPO_ROOT / "scripts" / "list_external_baseline_observations.py"
CREATE_HELPER = REPO_ROOT / "scripts" / "create_external_baseline_observation.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_external_baseline_observations.py"
REPORTER = REPO_ROOT / "scripts" / "report_external_baseline_status.py"
SCORE_FIELDS = (
    "object_type_fit",
    "smallest_actionable_unit",
    "evidence_quality",
    "compatibility_clarity",
    "actionability",
    "absence_explanation",
    "duplicate_handling",
    "user_cost_reduction",
    "overall",
)


class ExternalBaselineEntryHelperTest(unittest.TestCase):
    def test_list_helper_lists_and_filters_batch_slots(self) -> None:
        all_batch = self._run_json(LIST_HELPER, "--batch", "batch_0", "--json")
        one_query = self._run_json(
            LIST_HELPER,
            "--batch",
            "batch_0",
            "--query-id",
            "windows_7_apps",
            "--json",
        )
        one_system = self._run_json(
            LIST_HELPER,
            "--batch",
            "batch_0",
            "--system-id",
            "google_web_search",
            "--json",
        )
        plain = subprocess.run(
            [sys.executable, str(LIST_HELPER), "--batch", "batch_0", "--query-id", "windows_7_apps"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(all_batch["status"], "ready")
        self.assertEqual(all_batch["slot_count"], 39)
        self.assertEqual(one_query["slot_count"], 3)
        self.assertEqual(one_system["slot_count"], 13)
        self.assertIn(
            "batch_0 / windows_7_apps / google_web_search / pending_manual_observation",
            plain.stdout,
        )

    def test_create_helper_stdout_emits_pending_fillable_record(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(CREATE_HELPER),
                "--batch",
                "batch_0",
                "--query-id",
                "windows_7_apps",
                "--system-id",
                "google_web_search",
                "--stdout",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["query_id"], "windows_7_apps")
        self.assertEqual(payload["query_text"], "Windows 7 apps")
        self.assertEqual(payload["system_id"], "google_web_search")
        self.assertEqual(payload["observation_status"], "pending_manual_observation")
        self.assertEqual(payload["top_results"], [])
        self.assertIsNone(payload["exact_query_submitted"])
        self.assertIsNone(payload["observed_at"])
        self.assertNotIn("http", json.dumps(payload).lower())

    def test_create_helper_writes_pending_file_and_validator_accepts_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "manual_observation.json"
            subprocess.run(
                [
                    sys.executable,
                    str(CREATE_HELPER),
                    "--batch",
                    "batch_0",
                    "--query-id",
                    "windows_7_apps",
                    "--system-id",
                    "google_web_search",
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["observation_status"], "pending_manual_observation")
            self.assertEqual(payload["top_results"], [])

            validation = subprocess.run(
                [sys.executable, str(VALIDATOR), "--file", str(output_path), "--json"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(validation.stdout)["status"], "valid")

    def test_create_helper_refuses_unknown_slot_and_overwrite(self) -> None:
        unknown = subprocess.run(
            [
                sys.executable,
                str(CREATE_HELPER),
                "--batch",
                "batch_0",
                "--query-id",
                "not_a_query",
                "--system-id",
                "google_web_search",
                "--stdout",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(unknown.returncode, 0)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "manual_observation.json"
            command = [
                sys.executable,
                str(CREATE_HELPER),
                "--batch",
                "batch_0",
                "--query-id",
                "windows_7_apps",
                "--system-id",
                "google_web_search",
                "--output",
                str(output_path),
            ]
            subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True, text=True)
            overwrite = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(overwrite.returncode, 0)
            self.assertIn("use --force", overwrite.stdout)
            subprocess.run(
                [*command, "--force"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

    def test_validator_file_mode_rejects_placeholder_observed_records(self) -> None:
        record = self._minimal_observed_record()
        record["operator"] = "<operator>"

        completed = self._run_validator_file(record)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("observed record missing operator", completed.stdout)
        self.assertIn("template placeholders", completed.stdout)

    def test_validator_file_mode_rejects_observed_missing_results_or_scores(self) -> None:
        record = self._minimal_observed_record()
        record["top_results"] = []
        record["usefulness_scores"] = {"overall": 2}

        completed = self._run_validator_file(record)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("observed record must contain manually recorded top_results", completed.stdout)
        self.assertIn("observed record missing scores", completed.stdout)

    def test_validator_file_mode_accepts_minimal_human_entered_observed_record(self) -> None:
        completed = self._run_validator_file(self._minimal_observed_record())

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")

    def test_reporter_batch_and_next_pending_modes(self) -> None:
        batch_report = self._run_json(REPORTER, "--batch", "batch_0", "--json")
        next_report = self._run_json(
            REPORTER,
            "--batch",
            "batch_0",
            "--next-pending",
            "--json",
        )

        self.assertEqual(batch_report["status"], "ready")
        self.assertEqual(batch_report["selected_batch"], "batch_0")
        self.assertEqual(batch_report["batches"]["batch_0"]["completion_percent"], 0.0)
        self.assertEqual(len(next_report["next_pending_slots"]), 39)

    def _run_json(self, script: Path, *args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def _run_validator_file(self, record: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "observation.json"
            path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), "--file", str(path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

    def _minimal_observed_record(self) -> dict:
        return {
            "observation_id": "manual-test::windows_7_apps::google_web_search",
            "query_id": "windows_7_apps",
            "query_text": "Windows 7 apps",
            "system_id": "google_web_search",
            "observation_status": "observed",
            "operator": "Manual Test Operator",
            "observed_at": "2026-04-27T00:00:00Z",
            "browser_or_tool": "manual test fixture, no browser opened",
            "location_context_optional": "test fixture",
            "exact_query_submitted": "Windows 7 apps",
            "filters_or_scope": "none",
            "result_count_visible_optional": 1,
            "collection_method": "manual",
            "top_results": [
                {
                    "rank": 1,
                    "title": "Manually entered visible title",
                    "url_or_locator": "manual-locator:google_web_search:1",
                    "snippet_or_visible_summary": "Short manually entered summary.",
                    "result_type": "organic",
                    "notes": "Local validator fixture only; no external lookup was performed.",
                }
            ],
            "first_useful_result_rank": 1,
            "first_useful_result_reason": "Manually marked useful in this validator fixture.",
            "usefulness_scores": {field: 2 for field in SCORE_FIELDS},
            "failure_modes": [],
            "comparison_notes": ["Local validator fixture."],
            "next_eureka_work": [],
            "evidence_limitations": ["Manual observation metadata required in real records."],
            "staleness_notes": ["Validator fixture, not a committed baseline observation."],
            "created_by": "test_external_baseline_entry_helpers",
            "schema_version": "manual_external_baseline_observation.v0",
        }


if __name__ == "__main__":
    unittest.main()
