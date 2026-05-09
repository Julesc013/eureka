import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class PackBuilderRuntimeScriptsTest(unittest.TestCase):
    def run_command(self, args, cwd=REPO_ROOT):
        return subprocess.run([sys.executable, *args], cwd=cwd, text=True, capture_output=True)

    def test_build_script_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            before = set(Path(temp_dir).iterdir())
            result = self.run_command(
                [
                    "scripts/build_local_pack.py",
                    "--pack-type",
                    "evidence_pack_draft",
                    "--input",
                    "examples/evidence_ledger_records/metadata_claim_record_v0.json",
                    "--check",
                ],
                cwd=REPO_ROOT,
            )
            after = set(Path(temp_dir).iterdir())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)

    def test_build_script_writes_explicit_report_to_temp_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "pack.json"
            result = self.run_command(
                [
                    "scripts/build_local_pack.py",
                    "--pack-type",
                    "evidence_pack_draft",
                    "--input",
                    "examples/evidence_ledger_records/metadata_claim_record_v0.json",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())

    def test_build_script_refuses_forbidden_roots(self):
        for output in ("site/dist/pack.json", "runtime/pack.json", "data/public_index/pack.json"):
            result = self.run_command(
                [
                    "scripts/build_local_pack.py",
                    "--pack-type",
                    "evidence_pack_draft",
                    "--input",
                    "examples/evidence_ledger_records/metadata_claim_record_v0.json",
                    "--output",
                    output,
                ]
            )
            self.assertNotEqual(result.returncode, 0, output)

    def test_summarizer_works_on_examples(self):
        result = self.run_command(
            [
                "scripts/summarize_local_pack.py",
                "--input",
                "examples/pack_drafts",
                "--check",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Pack drafts", result.stdout)

    def test_summarizer_refuses_forbidden_output_root(self):
        result = self.run_command(
            [
                "scripts/summarize_local_pack.py",
                "--input",
                "examples/pack_drafts",
                "--output",
                "runtime/pack_summary.md",
            ]
        )
        self.assertNotEqual(result.returncode, 0)

    def test_validator_passes_current_repo(self):
        result = self.run_command(["scripts/validate_pack_builder_runtime.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
