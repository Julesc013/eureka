import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY = REPO_ROOT / "scripts/summarize_connector_families.py"
REPLAY = REPO_ROOT / "scripts/run_connector_fixture_replay.py"
EVALUATE = REPO_ROOT / "scripts/evaluate_connector_policy.py"
VALIDATOR = REPO_ROOT / "scripts/validate_connector_interface_foundation.py"
FAMILY_DIR = "examples/connectors/core/families"
REPLAY_REQUEST = "examples/connectors/core/fixture_replay/minimal_fixture_replay_request_v0.json"
POLICY_REQUEST = "examples/connectors/core/live_probe/policy_blocked_live_probe_request_v0.json"


class ConnectorInterfaceFoundationScriptsTest(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, *map(str, args)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_summary_script_writes_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / FAMILY_DIR).glob("*.json"))
        result = self.run_script(SUMMARY, "--input", FAMILY_DIR, "--json")
        after = sorted(path.name for path in (REPO_ROOT / FAMILY_DIR).glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertEqual(json.loads(result.stdout)["family_count"], 8)

    def test_summary_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "families.json"
            markdown = root / "families.md"
            result = self.run_script(SUMMARY, "--input", FAMILY_DIR, "--output", output, "--summary-output", markdown)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["live_access_enabled_count"], 0)
            self.assertTrue(markdown.read_text(encoding="utf-8").startswith("# Connector Family Summary"))

    def test_fixture_replay_script_writes_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/connectors/core/fixture_replay").glob("*.json"))
        result = self.run_script(REPLAY, "--request", REPLAY_REQUEST, "--json")
        after = sorted(path.name for path in (REPO_ROOT / "examples/connectors/core/fixture_replay").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(json.loads(result.stdout)["validation_summary"].get("network_used", False))

    def test_fixture_replay_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "replay.json"
            result = self.run_script(REPLAY, "--request", REPLAY_REQUEST, "--output", output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["no_network_used"])

    def test_connector_policy_evaluator_writes_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/connectors/core/live_probe").glob("*.json"))
        result = self.run_script(EVALUATE, "--request", POLICY_REQUEST, "--json")
        after = sorted(path.name for path in (REPO_ROOT / "examples/connectors/core/live_probe").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(json.loads(result.stdout)["allowed_for_live_probe"])

    def test_scripts_refuse_site_dist_output(self):
        result = self.run_script(SUMMARY, "--input", FAMILY_DIR, "--output", "site/dist/connectors.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_scripts_refuse_data_public_index_output(self):
        result = self.run_script(REPLAY, "--request", REPLAY_REQUEST, "--output", "data/public_index/replay.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_validator_passes_current_repo(self):
        result = self.run_script(VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_validator_does_not_call_network_model_or_provider(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                VALIDATOR,
                SUMMARY,
                REPLAY,
                EVALUATE,
                REPO_ROOT / "runtime/connectors/core/connector_interface.py",
                REPO_ROOT / "runtime/connectors/core/fixture_replay.py",
                REPO_ROOT / "runtime/connectors/core/live_probe_envelope.py",
                REPO_ROOT / "runtime/connectors/core/policy_evaluator.py",
                REPO_ROOT / "runtime/connectors/core/output_envelope.py",
            )
        )
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|socket|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        self.run_script(VALIDATOR)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
