import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_h2_package_registry_fixture_runtime import validate_repo


REPO_ROOT = Path(__file__).resolve().parents[2]


class H2PackageFixtureScriptTests(unittest.TestCase):
    def run_cmd(self, args):
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)

    def test_normalizer_script_writes_no_files_by_default(self):
        result = self.run_cmd([
            "scripts/normalize_h2_package_fixture.py",
            "--source-id",
            "crates_io",
            "--input",
            "examples/connectors/h2_package_registries/fixtures/crates_io/typical_record.json",
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: pass", result.stdout)

    def test_normalizer_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "normalized.json"
            identity = Path(tmp) / "identity.json"
            dep = Path(tmp) / "deps.json"
            file_out = Path(tmp) / "files.json"
            result = self.run_cmd([
                "scripts/normalize_h2_package_fixture.py",
                "--source-id",
                "crates_io",
                "--input",
                "examples/connectors/h2_package_registries/fixtures/crates_io/typical_record.json",
                "--output",
                str(out),
                "--identity-output",
                str(identity),
                "--dependency-output",
                str(dep),
                "--file-candidate-output",
                str(file_out),
            ])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(out.read_text())["schema_version"], "h2_package_normalized_record.v0")
            self.assertTrue(identity.is_file())
            self.assertTrue(dep.is_file())
            self.assertTrue(file_out.is_file())

    def test_replay_script_writes_no_files_by_default(self):
        result = self.run_cmd(["scripts/replay_h2_package_fixtures.py", "--check"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("fixture_replay_count: 32", result.stdout)

    def test_replay_script_writes_explicit_outputs_to_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cmd(["scripts/replay_h2_package_fixtures.py", "--source-id", "crates_io", "--output-dir", tmp])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(any(Path(tmp).glob("*.json")))

    def test_scripts_refuse_forbidden_roots(self):
        bad_site = self.run_cmd([
            "scripts/normalize_h2_package_fixture.py",
            "--source-id",
            "crates_io",
            "--input",
            "examples/connectors/h2_package_registries/fixtures/crates_io/typical_record.json",
            "--output",
            "site/dist/h2.json",
        ])
        self.assertNotEqual(bad_site.returncode, 0)
        bad_public = self.run_cmd(["scripts/replay_h2_package_fixtures.py", "--output-dir", "site/dist/data/public_index/h2"])
        self.assertNotEqual(bad_public.returncode, 0)
        bad_private = self.run_cmd([
            "scripts/normalize_h2_package_fixture.py",
            "--source-id",
            "crates_io",
            "--input",
            "examples/connectors/h2_package_registries/fixtures/crates_io/typical_record.json",
            "--output",
            ".local/eureka/h2.json",
        ])
        self.assertNotEqual(bad_private.returncode, 0)

    def test_summary_script_passes(self):
        result = self.run_cmd(["scripts/summarize_h2_package_fixture_outputs.py", "--input", "examples/connectors/h2_package_registries", "--check", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_count"], 8)

    def test_validator_passes_current_repo(self):
        result = validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_validator_does_not_create_local_private_roots(self):
        self.assertFalse((REPO_ROOT / ".local" / "eureka").exists())
        self.assertFalse((REPO_ROOT / ".cache" / "eureka").exists())


if __name__ == "__main__":
    unittest.main()

