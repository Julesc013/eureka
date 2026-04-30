from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO

from surfaces.native.cli.main import main


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class ResolutionRunsCliTestCase(unittest.TestCase):
    def test_run_resolve_and_run_status_render_checked_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_exit_code, resolve_output = run_cli(
                "run-resolve",
                KNOWN_TARGET_REF,
                "--run-store-root",
                temp_dir,
            )
            status_exit_code, status_output = run_cli(
                "run-status",
                "run-exact-resolution-0001",
                "--run-store-root",
                temp_dir,
            )
            list_exit_code, list_output = run_cli(
                "runs",
                "--run-store-root",
                temp_dir,
            )

        self.assertEqual(resolve_exit_code, 0)
        self.assertEqual(status_exit_code, 0)
        self.assertEqual(list_exit_code, 0)
        self.assertIn("Resolution runs", resolve_output)
        self.assertIn("selected_run_id: run-exact-resolution-0001", resolve_output)
        self.assertIn(
            "checked_source_ids: article-scan-recorded-fixtures, github-releases-recorded-fixtures, internet-archive-recorded-fixtures, local-bundle-fixtures, manual-document-recorded-fixtures, package-registry-recorded-fixtures, review-description-recorded-fixtures, software-heritage-recorded-fixtures, sourceforge-recorded-fixtures, synthetic-fixtures, wayback-memento-recorded-fixtures",
            status_output,
        )
        self.assertIn("Article Scan Recorded Fixtures [active_recorded_fixture]", status_output)
        self.assertIn("Internet Archive Recorded Fixtures [active_recorded_fixture]", status_output)
        self.assertIn("Local Bundle Fixtures [active_fixture]", status_output)
        self.assertIn("Manual Document Recorded Fixtures [active_recorded_fixture]", status_output)
        self.assertIn("SourceForge Recorded Fixtures [active_recorded_fixture]", status_output)
        self.assertIn("Wayback/Memento Recorded Fixtures [active_recorded_fixture]", status_output)
        self.assertIn("Synthetic Fixtures [active_fixture]", status_output)
        self.assertIn("run-exact-resolution-0001", list_output)

    def test_run_search_supports_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code, output = run_cli(
                "run-search",
                "archive",
                "--run-store-root",
                temp_dir,
                "--json",
            )

        payload = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "available")
        self.assertEqual(payload["selected_run_id"], "run-deterministic-search-0001")
        self.assertGreaterEqual(payload["runs"][0]["result_summary"]["result_count"], 15)


if __name__ == "__main__":
    unittest.main()
