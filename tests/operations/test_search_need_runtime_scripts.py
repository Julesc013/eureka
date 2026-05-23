from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock
import unittest

from scripts.record_search_need import main as record_search_need_main
from scripts.validate_search_need_runtime import validate_search_need_runtime


ROOT = Path(__file__).resolve().parents[2]
EMPTY_MISS = ROOT / "examples" / "search" / "misses" / "empty_result_search_miss_v0.json"


class SearchNeedRuntimeScriptTests(unittest.TestCase):
    def test_script_writes_no_files_by_default(self) -> None:
        before = _tracked_relevant_files()
        stdout = io.StringIO()

        result = record_search_need_main(["--input", str(EMPTY_MISS), "--check"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("status: pass", stdout.getvalue())
        self.assertEqual(before, _tracked_relevant_files())

    def test_script_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "search_need_report.json"
            stdout = io.StringIO()
            result = record_search_need_main(
                ["--input", str(EMPTY_MISS), "--output", str(output), "--json"],
                stdout=stdout,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["schema_version"], "search_need_runtime_report.v0")

    def test_script_refuses_site_dist_output(self) -> None:
        forbidden = ROOT / "site" / "dist" / "__search_need_forbidden_report.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [
                sys.executable,
                "scripts/record_search_need.py",
                "--input",
                "examples/search/misses/empty_result_search_miss_v0.json",
                "--output",
                str(forbidden),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_script_refuses_runtime_output(self) -> None:
        forbidden = ROOT / "runtime" / "__search_need_forbidden_report.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [
                sys.executable,
                "scripts/record_search_need.py",
                "--input",
                "examples/search/misses/empty_result_search_miss_v0.json",
                "--output",
                str(forbidden),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_validator_passes_current_repo(self) -> None:
        report = validate_search_need_runtime(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_runtime_script_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            stdout = io.StringIO()
            result = record_search_need_main(["--input", str(EMPTY_MISS), "--check", "--json"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "pass")

    def test_validator_does_not_create_local_private_roots(self) -> None:
        before = _private_root_state()

        report = validate_search_need_runtime(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _private_root_state())


def _tracked_relevant_files() -> list[str]:
    roots = [
        ROOT / "control" / "audits" / "track-b-09-search-need-runtime-v0" / "generated",
        ROOT / "examples" / "search" / "needs",
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
