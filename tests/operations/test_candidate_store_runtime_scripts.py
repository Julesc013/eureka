from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock
import unittest

from scripts.record_candidate import main as record_candidate_main
from scripts.summarize_candidate_store import main as summarize_candidate_store_main
from scripts.validate_candidate_store_runtime import validate_candidate_store_runtime


ROOT = Path(__file__).resolve().parents[2]
SEARCH_NEED_INPUT = ROOT / "examples" / "search" / "needs" / "software_version_search_need_v0.json"


class CandidateStoreScriptTests(unittest.TestCase):
    def test_record_candidate_writes_no_files_by_default(self) -> None:
        before = _tracked_relevant_files()
        stdout = io.StringIO()

        result = record_candidate_main(["--input", str(SEARCH_NEED_INPUT), "--check"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("status: pass", stdout.getvalue())
        self.assertEqual(before, _tracked_relevant_files())

    def test_record_candidate_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "candidate_report.json"
            summary = Path(tmp) / "candidate_summary.md"
            stdout = io.StringIO()
            result = record_candidate_main(
                ["--input", str(SEARCH_NEED_INPUT), "--output", str(output), "--summary-output", str(summary), "--json"],
                stdout=stdout,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(payload["schema_version"], "candidate_store_runtime_report.v0")
        self.assertIn("Candidate Report", summary_text)

    def test_record_candidate_refuses_site_dist_output(self) -> None:
        forbidden = ROOT / "site" / "dist" / "__candidate_forbidden.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [sys.executable, "scripts/record_candidate.py", "--input", str(SEARCH_NEED_INPUT), "--output", str(forbidden)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_record_candidate_refuses_runtime_output(self) -> None:
        forbidden = ROOT / "runtime" / "__candidate_forbidden.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [sys.executable, "scripts/record_candidate.py", "--input", str(SEARCH_NEED_INPUT), "--output", str(forbidden)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_summarizer_works_on_examples(self) -> None:
        stdout = io.StringIO()

        result = summarize_candidate_store_main(["--input", str(ROOT / "examples" / "index" / "candidates"), "--check"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("candidate_count: 7", stdout.getvalue())

    def test_validator_passes_current_repo(self) -> None:
        report = validate_candidate_store_runtime(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_runtime_scripts_do_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            stdout = io.StringIO()
            result = record_candidate_main(["--input", str(SEARCH_NEED_INPUT), "--check", "--json"], stdout=stdout)

        payload = json.loads(stdout.getvalue())
        self.assertEqual(result, 0)
        self.assertFalse(payload["product_boundary"]["enabled_network_access"])
        self.assertFalse(payload["product_boundary"]["enabled_model_provider_calls"])

    def test_validator_does_not_create_local_private_roots(self) -> None:
        before = _private_root_state()

        report = validate_candidate_store_runtime(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _private_root_state())


def _tracked_relevant_files() -> list[str]:
    roots = [
        ROOT / "control" / "audits" / "track-b-12-candidate-store-runtime-v0" / "generated",
        ROOT / "examples" / "index" / "candidates",
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

