from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class SearchExplanationScriptTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False)

    def test_explanation_script_writes_no_files_by_default(self) -> None:
        result = self.run_cmd(
            "scripts/explain_search_fixture.py",
            "--input",
            "examples/search/quality/input_bundles/software_search_explanation_bundle_v0.json",
            "--check",
            "--json",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"wrote_files": false', result.stdout)

    def test_explanation_script_writes_explicit_outputs_to_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "explanation.json"
            bundle = Path(temp) / "bundle.json"
            result = self.run_cmd(
                "scripts/explain_search_fixture.py",
                "--input",
                "examples/search/quality/input_bundles/software_search_explanation_bundle_v0.json",
                "--output",
                str(out),
                "--bundle-output",
                str(bundle),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(out.exists())
            self.assertTrue(bundle.exists())

    def test_explanation_script_refuses_site_dist_output(self) -> None:
        result = self.run_cmd(
            "scripts/explain_search_fixture.py",
            "--input",
            "examples/search/quality/input_bundles/software_search_explanation_bundle_v0.json",
            "--output",
            "site/dist/explanation.json",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_script_refuses_public_index_output(self) -> None:
        result = self.run_cmd(
            "scripts/summarize_search_explanations.py",
            "--input",
            "examples/search/quality",
            "--output",
            "site/dist/data/public_index/explanation.json",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_script_check_passes(self) -> None:
        result = self.run_cmd("scripts/summarize_search_explanations.py", "--input", "examples/search/quality", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: pass", result.stdout)

    def test_validator_passes_current_repo(self) -> None:
        result = self.run_cmd("scripts/validate_search_explanation_runtime.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
