import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeFirstWaveScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_first_wave_validators_pass(self) -> None:
        for script in (
            "scripts/validate_native_first_wave_skeletons.py",
            "scripts/validate_native_project_boundaries.py",
        ):
            result = self.run_script(script, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_summary_script_writes_no_files_by_default(self) -> None:
        result = self.run_script("scripts/summarize_native_first_wave.py", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")

    def test_summary_script_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_native_first_wave_") as temp_dir:
            output = Path(temp_dir) / "summary.json"
            markdown = Path(temp_dir) / "summary.md"
            result = self.run_script(
                "scripts/summarize_native_first_wave.py",
                "--output",
                str(output),
                "--summary-output",
                str(markdown),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(markdown.is_file())

    def test_scripts_refuse_forbidden_output_roots(self) -> None:
        for forbidden in (
            "site/dist/native-first-wave-summary.json",
            "data/public_index/native-first-wave-summary.json",
            ".local/eureka/native-first-wave-summary.json",
        ):
            result = self.run_script("scripts/summarize_native_first_wave.py", "--output", forbidden)
            self.assertNotEqual(result.returncode, 0, forbidden)
            self.assertIn("Refusing", result.stderr + result.stdout)

    def test_validators_do_not_create_local_private_roots(self) -> None:
        result = self.run_script("scripts/validate_native_first_wave_skeletons.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
