import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)


class SourceOsCoverageScorecardScriptsTests(unittest.TestCase):
    def test_record_source_coverage_writes_no_files_by_default(self):
        before = set((REPO_ROOT / "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated").glob("*"))
        result = run_cmd(["scripts/record_source_coverage.py", "--input", "examples/sources/coverage/internet_archive_coverage_record_v0.json"])
        after = set((REPO_ROOT / "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/generated").glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            commands = [
                ["scripts/record_source_coverage.py", "--input", "examples/sources/coverage/internet_archive_coverage_record_v0.json", "--output", str(tmp_path / "coverage.json")],
                ["scripts/score_connector.py", "--input", "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json", "--output", str(tmp_path / "scorecard.json")],
                ["scripts/build_source_pack.py", "--input", "examples/packs/source/internet_archive_source_pack_manifest_v0.json", "--output", str(tmp_path / "pack.json")],
            ]
            for command in commands:
                result = run_cmd(command)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((tmp_path / "coverage.json").is_file())
            self.assertTrue((tmp_path / "scorecard.json").is_file())
            self.assertTrue((tmp_path / "pack.json").is_file())

    def test_scripts_refuse_site_dist_output(self):
        result = run_cmd(["scripts/record_source_coverage.py", "--input", "examples/sources/coverage/internet_archive_coverage_record_v0.json", "--output", "site/dist/coverage.json"])
        self.assertNotEqual(result.returncode, 0)

    def test_scripts_refuse_data_public_index_output(self):
        result = run_cmd(["scripts/score_connector.py", "--input", "examples/connectors/core/scorecards/internet_archive_scorecard_v0.json", "--output", "site/dist/data/public_index/scorecard.json"])
        self.assertNotEqual(result.returncode, 0)

    def test_source_pack_refuses_contract_output(self):
        result = run_cmd(["scripts/build_source_pack.py", "--input", "examples/packs/source/internet_archive_source_pack_manifest_v0.json", "--output", "contracts/pack.json"])
        self.assertNotEqual(result.returncode, 0)

    def test_validator_passes_current_repo(self):
        result = run_cmd(["scripts/validate_source_os_coverage_scorecards.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_does_not_create_local_private_roots(self):
        result = run_cmd(["scripts/validate_source_os_coverage_scorecards.py", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)

    def test_no_script_imports_network_or_model_provider(self):
        banned = ("requests", "httpx", "aiohttp", "socket", "openai", "anthropic", "selenium", "playwright")
        for rel in (
            "scripts/record_source_coverage.py",
            "scripts/score_connector.py",
            "scripts/build_source_pack.py",
            "scripts/validate_source_os_coverage_scorecards.py",
            "scripts/audit_h0_integration.py",
        ):
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            for item in banned:
                self.assertNotIn(f"import {item}", text)
                self.assertNotIn(f"from {item}", text)


if __name__ == "__main__":
    unittest.main()
