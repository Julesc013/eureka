from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from runtime.engine.evals import (
    VALID_EUREKA_STATUSES,
    VALID_FAILURE_LABELS,
    load_search_usefulness_queries,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "evals" / "search_usefulness"
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_search_usefulness_audit.py"
OBSERVATION_SCRIPT_PATH = REPO_ROOT / "scripts" / "record_search_baseline_observation.py"


class SearchUsefulnessFixtureTestCase(unittest.TestCase):
    def test_query_fixtures_parse_and_have_unique_ids(self) -> None:
        load_result = load_search_usefulness_queries(EVAL_ROOT)
        ids = [query.query_id for query in load_result.queries]

        self.assertEqual(load_result.errors, ())
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 60)
        self.assertLessEqual(len(ids), 100)

    def test_query_fixtures_have_valid_statuses_and_labels(self) -> None:
        load_result = load_search_usefulness_queries(EVAL_ROOT)

        for query in load_result.queries:
            self.assertIn(query.expected_eureka_current_status, VALID_EUREKA_STATUSES)
            self.assertLessEqual(len(query.query), 160)
            self.assertLessEqual(len(query.notes), 320)
            for label in query.expected_failure_modes + query.future_work_labels:
                self.assertIn(label, VALID_FAILURE_LABELS)

    def test_query_pack_covers_required_buckets(self) -> None:
        load_result = load_search_usefulness_queries(EVAL_ROOT)
        families = {query.query_family for query in load_result.queries}

        expected = {
            "current_covered_sanity",
            "platform_software",
            "latest_compatible_release",
            "driver_hardware_support",
            "manual_documentation",
            "article_inside_scan",
            "package_container_member",
            "vague_identity",
            "web_archive_dead_link",
            "source_code_package_release",
            "negative_absence",
        }
        self.assertTrue(expected.issubset(families))

    def test_schema_files_are_json_subset_yaml(self) -> None:
        for name in ("query.schema.yaml", "observation.schema.yaml", "report.schema.yaml"):
            payload = json.loads((EVAL_ROOT / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["x-eureka-status"], "draft")


class SearchUsefulnessScriptTestCase(unittest.TestCase):
    def test_script_runs_full_suite_plain_text(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Search usefulness audit", completed.stdout)
        self.assertIn("query_count: 64", completed.stdout)
        self.assertIn("external_pending_counts", completed.stdout)

    def test_script_runs_one_query(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--query", "windows_7_apps"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("windows_7_apps", completed.stdout)
        self.assertIn("query_count: 1", completed.stdout)

    def test_script_json_mode_and_output_path_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "search-usefulness-report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--query",
                    "windows_7_apps",
                    "--json",
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            stdout_payload = json.loads(completed.stdout)
            file_payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(stdout_payload["total_query_count"], 1)
        self.assertEqual(file_payload["total_query_count"], 1)
        self.assertEqual(stdout_payload["queries"][0]["query_id"], "windows_7_apps")
        self.assertEqual(
            stdout_payload["queries"][0]["observations"][1]["observation_status"],
            "pending_manual_observation",
        )

    def test_manual_observation_helper_creates_pending_template(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(OBSERVATION_SCRIPT_PATH),
                "--query",
                "windows_7_apps",
                "--system",
                "google",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["query_id"], "windows_7_apps")
        self.assertEqual(payload["system"], "google")
        self.assertEqual(payload["observation_status"], "pending_manual_observation")
        self.assertEqual(payload["top_results"], [])


if __name__ == "__main__":
    unittest.main()
