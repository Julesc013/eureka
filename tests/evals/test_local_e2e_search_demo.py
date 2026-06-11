from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.run_local_e2e_search_demo import (
    BASELINE_PROFILES,
    REQUIRED_QUERY_TEXTS,
    build_demo_suite,
    build_profile_output,
    write_demo_fixtures,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalE2ESearchDemoTests(unittest.TestCase):
    def test_all_required_hard_queries_are_covered(self) -> None:
        suite = build_demo_suite(REPO_ROOT)
        query_texts = {item["query_text"] for item in suite["queries"]}

        self.assertEqual(query_texts, set(REQUIRED_QUERY_TEXTS))
        self.assertEqual(len(suite["queries"]), 6)

    def test_artifact_gate_and_verified_count_are_visible(self) -> None:
        suite = build_demo_suite(REPO_ROOT)
        gate = suite["artifact_gate"]

        self.assertEqual(gate["reviewed_artifact_record_count"], 4)
        self.assertEqual(gate["minimum_public_alpha_reviewed_artifact_records"], 25)
        self.assertEqual(gate["reviewed_artifact_record_gap"], 21)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertTrue(gate["public_alpha_blocked"])

        for profile in BASELINE_PROFILES:
            output = build_profile_output(suite, profile)
            self.assertIn("artifact_gate", output)
            self.assertEqual(output["artifact_gate"]["verified_artifact_count"], 0)

    def test_driver_query_remains_blocked_for_user_details_concept(self) -> None:
        suite = build_demo_suite(REPO_ROOT)
        driver = suite["results"]["hq_driver_win98"]["json_v0"]
        fallback = driver["view_model"]["payload"]["fallback_summary"]

        self.assertEqual(driver["expected_status"], "need")
        self.assertEqual(driver["status_concept"], "blocked_for_user_details")
        self.assertIn("hardware_identifier_missing", fallback["reason_codes"])
        self.assertIn("Need vendor and device model", repr(fallback["needs"]))
        self.assertFalse(driver["truth_boundary"]["verified"])

    def test_demo_does_not_call_sources_or_mutate_indexes(self) -> None:
        suite = build_demo_suite(REPO_ROOT)

        self.assertFalse(suite["live_source_calls"])
        self.assertFalse(suite["source_provider_calls"])
        self.assertFalse(suite["downloads_performed"])
        self.assertFalse(suite["reviewed_index_mutated"])
        self.assertFalse(suite["public_index_mutated"])
        self.assertFalse(suite["master_index_mutated"])
        for profile_results in suite["results"].values():
            for result in profile_results.values():
                self.assertFalse(any(result["surface_flags"].values()))
                self.assertFalse(any(result["renderer_flags"].values()))

    def test_fixture_write_is_deterministic_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = write_demo_fixtures(Path(tmp) / "first", REPO_ROOT)
            second = write_demo_fixtures(Path(tmp) / "second", REPO_ROOT)

            self.assertEqual(set(first), {
                "query_inputs.json",
                "expected_statuses.json",
                "surface_view_models.json",
                "rendered_json_v0.json",
                "rendered_text_v0.txt",
                "rendered_html_basic_v0.html",
                "snapshot_v0.json",
                "demo_report.md",
            })
            for name in first:
                self.assertEqual(
                    (Path(tmp) / "first" / name).read_text(encoding="utf-8"),
                    (Path(tmp) / "second" / name).read_text(encoding="utf-8"),
                )

    def test_cli_all_json_profile_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_local_e2e_search_demo.py", "--all", "--profile", "json_v0"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["profile"], "json_v0")
        self.assertEqual(len(payload["queries"]), 6)
        self.assertFalse(payload["live_source_calls"])


if __name__ == "__main__":
    unittest.main()
