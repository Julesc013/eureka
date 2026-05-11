from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import summarize_h12_retro_community_sources as summary


class H12RetroCommunitySummaryTests(unittest.TestCase):
    def test_build_summary(self) -> None:
        result = summary.build_summary()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["source_count"], 13)
        self.assertEqual(result["live_access_enabled_count"], 0)
        self.assertEqual(result["downloads_enabled_count"], 0)
        self.assertEqual(result["extraction_execution_enabled_count"], 0)

    def test_cli_writes_no_files_by_default_and_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, "scripts/summarize_h12_retro_community_sources.py", "--json"],
            cwd=summary.REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["wrote_files"])

    def test_cli_writes_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/summarize_h12_retro_community_sources.py",
                    "--output",
                    str(out),
                    "--summary-output",
                    str(md),
                ],
                cwd=summary.REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertTrue(out.exists())
            self.assertTrue(md.exists())

    def test_forbidden_output_roots_are_rejected(self) -> None:
        for raw in ("site/dist/h12.json", "data/public_index/h12.json", "runtime/h12.json", "contracts/h12.json"):
            proc = subprocess.run(
                [sys.executable, "scripts/summarize_h12_retro_community_sources.py", "--output", raw],
                cwd=summary.REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(proc.returncode, 0, raw)
            self.assertIn("refusing forbidden output root", proc.stdout)


if __name__ == "__main__":
    unittest.main()
