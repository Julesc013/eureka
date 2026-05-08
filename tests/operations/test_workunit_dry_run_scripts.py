from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock
import unittest

from scripts.run_workunit_dry_run import main as run_workunit_dry_run_main
from scripts.validate_workunit_dry_run_runner import validate_workunit_dry_run_runner


ROOT = Path(__file__).resolve().parents[2]
WORKUNIT = ROOT / "examples" / "work_units" / "search_need_review_v0" / "work_unit.json"


class WorkUnitDryRunScriptTests(unittest.TestCase):
    def test_runner_writes_no_files_by_default(self) -> None:
        before = _tracked_relevant_files()
        stdout = io.StringIO()

        result = run_workunit_dry_run_main(["--workunit", str(WORKUNIT), "--check"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("status: pass", stdout.getvalue())
        self.assertEqual(before, _tracked_relevant_files())

    def test_runner_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "workunit_dry_run_result.json"
            summary = Path(tmp) / "workunit_dry_run_summary.md"
            stdout = io.StringIO()
            result = run_workunit_dry_run_main(
                ["--workunit", str(WORKUNIT), "--output", str(output), "--summary-output", str(summary), "--json"],
                stdout=stdout,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(payload["schema_version"], "work_unit_result.v0")
        self.assertEqual(payload["workunit_result_status"], "pass")
        self.assertIn("WorkUnit Dry-Run Summary", summary_text)

    def test_runner_refuses_site_dist_output(self) -> None:
        forbidden = ROOT / "site" / "dist" / "__workunit_dry_run_forbidden.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_workunit_dry_run.py",
                "--workunit",
                "examples/work_units/search_need_review_v0/work_unit.json",
                "--output",
                str(forbidden),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_runner_refuses_runtime_output(self) -> None:
        forbidden = ROOT / "runtime" / "__workunit_dry_run_forbidden.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_workunit_dry_run.py",
                "--workunit",
                "examples/work_units/search_need_review_v0/work_unit.json",
                "--output",
                str(forbidden),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_runner_lists_examples(self) -> None:
        stdout = io.StringIO()

        result = run_workunit_dry_run_main(["--list-examples"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("examples/work_units/search_need_review_v0/work_unit.json", stdout.getvalue())

    def test_validator_passes_current_repo(self) -> None:
        report = validate_workunit_dry_run_runner(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_runtime_script_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            stdout = io.StringIO()
            result = run_workunit_dry_run_main(["--workunit", str(WORKUNIT), "--check", "--json"], stdout=stdout)

        payload = json.loads(stdout.getvalue())
        self.assertEqual(result, 0)
        self.assertFalse(payload["execution_summary"]["network_used"])
        self.assertFalse(payload["execution_summary"]["model_provider_used"])

    def test_validator_does_not_create_local_private_roots(self) -> None:
        before = _private_root_state()

        report = validate_workunit_dry_run_runner(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _private_root_state())


def _tracked_relevant_files() -> list[str]:
    roots = [
        ROOT / "control" / "audits" / "track-b-10-workunit-dry-run-runner-v0" / "generated",
        ROOT / "examples" / "workunit_dry_runs",
    ]
    results: list[str] = []
    for root in roots:
        if root.exists():
            results.extend(path.relative_to(ROOT).as_posix() for path in root.rglob("*") if path.is_file())
    return sorted(results)


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()
