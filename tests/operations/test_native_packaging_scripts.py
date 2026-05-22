import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativePackagingScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_packaging_validators_pass(self) -> None:
        result = self.run_script("scripts/validate_native_packaging_manifests.py", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_scripts_write_no_files_by_default(self) -> None:
        for command in (
            ("scripts/collect_native_smoke_evidence.py", "--lane", "win.winforms", "--check", "--json"),
            ("scripts/build_native_packaging_manifest.py", "--lane", "win.winforms", "--check", "--json"),
            ("scripts/summarize_native_smoke_evidence.py", "--input", "examples/native", "--check", "--json"),
            ("scripts/audit_track_c_integration.py", "--check", "--json"),
        ):
            result = self.run_script(*command)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_scripts_write_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_native_packaging_") as temp_dir:
            output = Path(temp_dir) / "packet.json"
            result = self.run_script("scripts/collect_native_smoke_evidence.py", "--lane", "win.winforms", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            output = Path(temp_dir) / "manifest.json"
            result = self.run_script("scripts/build_native_packaging_manifest.py", "--lane", "win.winforms", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())

    def test_summary_script_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_native_packaging_") as temp_dir:
            output = Path(temp_dir) / "summary.json"
            markdown = Path(temp_dir) / "summary.md"
            result = self.run_script(
                "scripts/summarize_native_smoke_evidence.py",
                "--input",
                "examples/native",
                "--output",
                str(output),
                "--summary-output",
                str(markdown),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(markdown.is_file())

    def test_scripts_refuse_forbidden_output_roots(self) -> None:
        forbidden_paths = (
            "site/dist/native-packaging.json",
            "site/dist/data/public_index/native-packaging.json",
            "native/win/win32/dist/release-payload.json",
            ".local/eureka/native-packaging.json",
        )
        for forbidden in forbidden_paths:
            result = self.run_script("scripts/build_native_packaging_manifest.py", "--lane", "win.winforms", "--output", forbidden)
            self.assertNotEqual(result.returncode, 0, forbidden)
            self.assertIn("Refusing", result.stderr + result.stdout)

    def test_validator_does_not_create_local_private_roots(self) -> None:
        result = self.run_script("scripts/validate_native_packaging_manifests.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
