import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "scripts/run_ia_metadata_live_probe.py"
VALIDATOR = REPO_ROOT / "scripts/validate_ia_metadata_live_probe.py"
IDENTIFIER = "eureka-software-fixture"


class IAMetadataLiveProbeScriptsTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_cli_writes_no_files_by_default(self):
        before = sorted(path.as_posix() for path in (REPO_ROOT / "examples/connectors/internet_archive/live_probe").glob("*.json"))
        result = self.run_cli("--identifier", IDENTIFIER, "--check")
        after = sorted(path.as_posix() for path in (REPO_ROOT / "examples/connectors/internet_archive/live_probe").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("result: blocked", result.stdout)
        self.assertEqual(before, after)

    def test_cli_writes_explicit_outputs_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result_path = root / "result.json"
            source_cache = root / "source_cache.json"
            evidence = root / "evidence.json"
            review_seed = root / "review_seed.json"
            summary = root / "summary.md"
            result = self.run_cli(
                "--identifier",
                IDENTIFIER,
                "--check",
                "--output",
                str(result_path),
                "--source-cache-output",
                str(source_cache),
                "--evidence-preview-output",
                str(evidence),
                "--review-seed-output",
                str(review_seed),
                "--summary-output",
                str(summary),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result_path.read_text(encoding="utf-8"))["result_status"], "blocked")
            self.assertEqual(json.loads(source_cache.read_text(encoding="utf-8"))["status"], "not_created_blocked_by_policy")
            self.assertTrue(summary.read_text(encoding="utf-8").startswith("# IA Metadata Live Probe Summary"))

    def test_cli_refuses_site_dist_output(self):
        result = self.run_cli("--identifier", IDENTIFIER, "--check", "--output", "site/dist/ia.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_cli_refuses_data_public_index_output(self):
        result = self.run_cli("--identifier", IDENTIFIER, "--check", "--output", "data/public_index/ia.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_validator_default_mode_does_not_call_network(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_live_flag_is_blocked_without_policy_approval(self):
        result = self.run_cli("--identifier", IDENTIFIER, "--live", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["live_probe"]["result_status"], "blocked")
        self.assertFalse(payload["live_probe"]["network_used"])
        self.assertEqual(payload["live_probe"]["request_count"], 0)

    def test_scripts_do_not_import_model_provider_or_requests(self):
        text = CLI.read_text(encoding="utf-8") + "\n" + VALIDATOR.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_runtime_does_not_create_local_private_roots(self):
        self.run_cli("--identifier", IDENTIFIER, "--check")
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
