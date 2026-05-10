import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
NORMALIZER = REPO_ROOT / "scripts/normalize_h4_code_source_fixture.py"
REPLAYER = REPO_ROOT / "scripts/replay_h4_code_source_fixtures.py"
SUMMARY = REPO_ROOT / "scripts/summarize_h4_code_source_fixture_outputs.py"
VALIDATOR = REPO_ROOT / "scripts/validate_h4_code_source_release_fixture_runtime.py"
GENERATED_DIR = REPO_ROOT / "control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated"


def run_cmd(args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )


class H4CodeSourceFixtureScriptTests(unittest.TestCase):
    def test_normalizer_writes_no_files_by_default(self):
        before = sorted(path.name for path in GENERATED_DIR.glob("*"))
        result = run_cmd([
            "scripts/normalize_h4_code_source_fixture.py",
            "--source-id",
            "github_releases",
            "--input",
            "examples/connectors/h4_code_source_release/fixtures/github_releases/typical_record.json",
            "--json",
        ])
        after = sorted(path.name for path in GENERATED_DIR.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertEqual(json.loads(result.stdout)["source_id"], "github_releases")

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "normalized.json"
            identity = tmp_path / "source-identity.json"
            release = tmp_path / "release-identity.json"
            relation = tmp_path / "relation.json"
            asset = tmp_path / "asset.json"
            source_cache = tmp_path / "source-cache.json"
            evidence = tmp_path / "evidence.json"
            result = run_cmd([
                "scripts/normalize_h4_code_source_fixture.py",
                "--source-id",
                "github_releases",
                "--input",
                "examples/connectors/h4_code_source_release/fixtures/github_releases/typical_record.json",
                "--output",
                str(output),
                "--source-identity-output",
                str(identity),
                "--release-identity-output",
                str(release),
                "--relation-output",
                str(relation),
                "--asset-output",
                str(asset),
                "--source-cache-output",
                str(source_cache),
                "--evidence-preview-output",
                str(evidence),
            ])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_id"], "github_releases")
            self.assertTrue(json.loads(relation.read_text(encoding="utf-8")))
            self.assertTrue(json.loads(asset.read_text(encoding="utf-8")))

    def test_replay_writes_no_files_by_default(self):
        before = sorted(path.name for path in GENERATED_DIR.glob("*"))
        result = run_cmd(["scripts/replay_h4_code_source_fixtures.py", "--json"])
        after = sorted(path.name for path in GENERATED_DIR.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["source_count"], 10)
        self.assertEqual(payload["fixture_replay_count"], 60)

    def test_replay_writes_explicit_outputs_to_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cmd(["scripts/replay_h4_code_source_fixtures.py", "--source-id", "github_releases", "--output-dir", tmp])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(len(list(Path(tmp).glob("*.json"))), 6)

    def test_summary_writes_no_files_by_default_and_passes(self):
        before = sorted(path.name for path in GENERATED_DIR.glob("*"))
        result = run_cmd(["scripts/summarize_h4_code_source_fixture_outputs.py", "--input", "examples/connectors/h4_code_source_release", "--json"])
        after = sorted(path.name for path in GENERATED_DIR.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertEqual(json.loads(result.stdout)["source_count"], 10)

    def test_scripts_refuse_forbidden_roots(self):
        bad_commands = [
            ["scripts/normalize_h4_code_source_fixture.py", "--source-id", "github_releases", "--input", "examples/connectors/h4_code_source_release/fixtures/github_releases/typical_record.json", "--output", "site/dist/h4.json"],
            ["scripts/replay_h4_code_source_fixtures.py", "--output-dir", "data/public_index/h4"],
            ["scripts/summarize_h4_code_source_fixture_outputs.py", "--output", "repository_clones/h4.json"],
        ]
        for command in bad_commands:
            result = run_cmd(command)
            self.assertNotEqual(result.returncode, 0, command)
            self.assertIn("refusing forbidden output root", result.stdout)

    def test_validator_passes_current_repo(self):
        result = run_cmd(["scripts/validate_h4_code_source_release_fixture_runtime.py", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["network_calls_made"])
        self.assertFalse(payload["repository_clones_made"])

    def test_scripts_do_not_import_network_model_or_provider(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (NORMALIZER, REPLAYER, SUMMARY, VALIDATOR))
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        result = run_cmd(["scripts/validate_h4_code_source_release_fixture_runtime.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "repository_clones", "repository_mirrors"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
