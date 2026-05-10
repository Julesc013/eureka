from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import summarize_h7_library_research_sources as summary_script


ROOT = Path(__file__).resolve().parents[2]


class H7LibraryResearchSummaryTests(unittest.TestCase):
    def test_build_summary_counts_sources(self) -> None:
        summary = summary_script.build_summary()
        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["source_count"], 30)
        self.assertEqual(summary["live_access_enabled_count"], 0)
        self.assertEqual(summary["harvest_or_api_enabled_count"], 0)
        self.assertEqual(summary["download_enabled_count"], 0)
        self.assertEqual(summary["scraping_crawling_enabled_count"], 0)
        self.assertEqual(summary["restricted_source_enabled_count"], 0)

    def test_cli_check_writes_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (ROOT / "control/audits/h7-bundle-01-library-research-policy-packs-v0/generated").glob("*")}
        result = subprocess.run(
            [sys.executable, "scripts/summarize_h7_library_research_sources.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (ROOT / "control/audits/h7-bundle-01-library-research-policy-packs-v0/generated").glob("*")}
        self.assertEqual(before, after)

    def test_cli_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            markdown = Path(tmp) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/summarize_h7_library_research_sources.py",
                    "--output",
                    str(output),
                    "--summary-output",
                    str(markdown),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_count"], 30)
            self.assertIn("H7 Library Cultural Research", markdown.read_text(encoding="utf-8"))

    def test_cli_refuses_forbidden_output_roots(self) -> None:
        for rel in ("site/dist/h7-summary.json", "data/public_index/h7-summary.json", "runtime/h7-summary.json", "contracts/h7-summary.json"):
            result = subprocess.run(
                [sys.executable, "scripts/summarize_h7_library_research_sources.py", "--output", rel],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, rel)
            self.assertIn("refusing", result.stdout + result.stderr)

    def test_json_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/summarize_h7_library_research_sources.py", "--check", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["source_count"], 30)


if __name__ == "__main__":
    unittest.main()
