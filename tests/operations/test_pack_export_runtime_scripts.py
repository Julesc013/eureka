import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class PackExportRuntimeScriptsTest(unittest.TestCase):
    def run_command(self, args, cwd=REPO_ROOT):
        return subprocess.run([sys.executable, *args], cwd=cwd, text=True, capture_output=True)

    def test_export_script_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            before = set(Path(temp_dir).iterdir())
            result = self.run_command(
                [
                    "scripts/export_local_pack.py",
                    "--input",
                    "examples/packs/drafts/evidence_pack_draft_v0.json",
                    "--check",
                ]
            )
            after = set(Path(temp_dir).iterdir())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)

    def test_export_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "export.json"
            report = Path(temp_dir) / "report.json"
            summary = Path(temp_dir) / "summary.md"
            result = self.run_command(
                [
                    "scripts/export_local_pack.py",
                    "--input",
                    "examples/packs/drafts/evidence_pack_draft_v0.json",
                    "--output",
                    str(output),
                    "--report-output",
                    str(report),
                    "--summary-output",
                    str(summary),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(report.is_file())
            self.assertTrue(summary.is_file())

    def test_export_script_refuses_forbidden_roots(self):
        for output in ("site/dist/export.json", "runtime/export.json", "site/dist/data/public_index/export.json"):
            result = self.run_command(
                [
                    "scripts/export_local_pack.py",
                    "--input",
                    "examples/packs/drafts/evidence_pack_draft_v0.json",
                    "--output",
                    output,
                ]
            )
            self.assertNotEqual(result.returncode, 0, output)

    def test_validator_passes_current_repo(self):
        result = self.run_command(["scripts/validate_pack_export_runtime.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
