from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class RankingShadowScriptTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False)

    def test_ranking_script_writes_no_files_by_default(self) -> None:
        result = self.run_cmd("scripts/run_ranking_shadow.py", "--input", "examples/search_quality/ranking/input_bundle_software_v0.json", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"wrote_files": false', result.stdout)

    def test_ranking_script_writes_explicit_outputs_to_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "ranking.json"
            bundle = Path(temp) / "bundle.json"
            result = self.run_cmd(
                "scripts/run_ranking_shadow.py",
                "--input",
                "examples/search_quality/ranking/input_bundle_software_v0.json",
                "--output",
                str(out),
                "--bundle-output",
                str(bundle),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(out.exists())
            self.assertTrue(bundle.exists())

    def test_ranking_script_refuses_site_dist_output(self) -> None:
        result = self.run_cmd("scripts/run_ranking_shadow.py", "--input", "examples/search_quality/ranking/input_bundle_software_v0.json", "--output", "site/dist/ranking.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_regression_script_refuses_public_index_output(self) -> None:
        result = self.run_cmd("scripts/run_search_quality_regression.py", "--query-set", "examples/search_quality/query_sets/minimal_search_quality_query_set_v0.json", "--output", "data/public_index/ranking.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_script_check_passes(self) -> None:
        result = self.run_cmd("scripts/summarize_ranking_shadow.py", "--input", "examples/search_quality/ranking", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: pass", result.stdout)

    def test_validator_passes_current_repo(self) -> None:
        result = self.run_cmd("scripts/validate_ranking_shadow_runtime.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
