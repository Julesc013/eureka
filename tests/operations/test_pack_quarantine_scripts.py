from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class PackQuarantineScriptTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False)

    def test_quarantine_script_writes_no_files_by_default(self) -> None:
        result = self.run_cmd("scripts/quarantine_local_pack.py", "--input", "examples/packs/exports/evidence_pack_export_v0.json", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"wrote_files": false', result.stdout)

    def test_quarantine_script_writes_explicit_outputs_to_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "quarantine.json"
            fixity = Path(temp) / "fixity.json"
            result = self.run_cmd(
                "scripts/quarantine_local_pack.py",
                "--input",
                "examples/packs/exports/evidence_pack_export_v0.json",
                "--output",
                str(output),
                "--fixity-output",
                str(fixity),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.exists())
            self.assertTrue(fixity.exists())
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schema_version"], "pack_quarantine_result.v0")

    def test_scripts_refuse_site_dist_output(self) -> None:
        result = self.run_cmd("scripts/quarantine_local_pack.py", "--input", "examples/packs/exports/evidence_pack_export_v0.json", "--output", "site/dist/quarantine.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_scripts_refuse_data_public_index_output(self) -> None:
        result = self.run_cmd("scripts/verify_local_pack_fixity.py", "--input", "examples/packs/exports/evidence_pack_export_v0.json", "--output", "site/dist/data/public_index/fixity.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_scripts_refuse_hosted_upload_roots(self) -> None:
        result = self.run_cmd("scripts/quarantine_local_pack.py", "--input", "examples/packs/exports/evidence_pack_export_v0.json", "--output", "hosted_upload/quarantine.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_preview_pack_import_script_check_passes(self) -> None:
        result = self.run_cmd("scripts/preview_pack_import.py", "--input", "examples/packs/quarantine/results/evidence_pack_quarantine_result_v0.json", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Imports records: false", result.stdout)

    def test_summary_script_check_passes(self) -> None:
        result = self.run_cmd("scripts/summarize_pack_quarantine.py", "--input", "examples/packs/quarantine/results", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: pass", result.stdout)

    def test_validator_passes_current_repo(self) -> None:
        result = self.run_cmd("scripts/validate_pack_quarantine_runtime.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
