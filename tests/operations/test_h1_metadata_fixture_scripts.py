import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
NORMALIZE = REPO_ROOT / "scripts/normalize_h1_metadata_fixture.py"
REPLAY = REPO_ROOT / "scripts/replay_h1_metadata_fixtures.py"
VALIDATOR = REPO_ROOT / "scripts/validate_h1_metadata_fixture_runtime.py"
GENERATED = REPO_ROOT / "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/generated"


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)


class H1MetadataFixtureScriptsTests(unittest.TestCase):
    def test_normalizer_script_writes_no_files_by_default(self):
        before = sorted(path.name for path in GENERATED.glob("*"))
        result = run_cmd(["scripts/normalize_h1_metadata_fixture.py", "--source-id", "pypi", "--input", "examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json"])
        after = sorted(path.name for path in GENERATED.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)

    def test_normalizer_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_cmd([
                "scripts/normalize_h1_metadata_fixture.py",
                "--source-id", "pypi",
                "--input", "examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json",
                "--output", str(tmp_path / "normalized.json"),
                "--source-cache-output", str(tmp_path / "source-cache.json"),
                "--evidence-preview-output", str(tmp_path / "evidence.json"),
            ])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((tmp_path / "normalized.json").read_text(encoding="utf-8"))["source_id"], "pypi")
            self.assertTrue((tmp_path / "source-cache.json").is_file())
            self.assertTrue((tmp_path / "evidence.json").is_file())

    def test_replay_script_writes_no_files_by_default(self):
        before = sorted(path.name for path in GENERATED.glob("*"))
        result = run_cmd(["scripts/replay_h1_metadata_fixtures.py", "--check"])
        after = sorted(path.name for path in GENERATED.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)

    def test_replay_script_writes_explicit_outputs_to_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cmd(["scripts/replay_h1_metadata_fixtures.py", "--source-id", "pypi", "--output-dir", tmp])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(list(Path(tmp).glob("*.json")))

    def test_scripts_refuse_site_dist_output(self):
        result = run_cmd([
            "scripts/normalize_h1_metadata_fixture.py",
            "--source-id", "pypi",
            "--input", "examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json",
            "--output", "site/dist/h1.json",
        ])
        self.assertNotEqual(result.returncode, 0)

    def test_scripts_refuse_data_public_index_output(self):
        result = run_cmd(["scripts/replay_h1_metadata_fixtures.py", "--output-dir", "site/dist/data/public_index/h1"])
        self.assertNotEqual(result.returncode, 0)

    def test_validator_passes_current_repo(self):
        result = run_cmd(["scripts/validate_h1_metadata_fixture_runtime.py", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "valid")

    def test_validator_does_not_call_network_model_or_provider(self):
        text = NORMALIZE.read_text(encoding="utf-8") + REPLAY.read_text(encoding="utf-8") + VALIDATOR.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        result = run_cmd(["scripts/validate_h1_metadata_fixture_runtime.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
