import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts/run_h2_package_live_probe.py"
SUMMARY = REPO_ROOT / "scripts/summarize_h2_package_live_probe_outputs.py"
VALIDATOR = REPO_ROOT / "scripts/validate_h2_package_live_probe.py"
GENERATED = REPO_ROOT / "control/audits/h2-bundle-03-package-live-probes-v0/generated"


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)


class H2PackageLiveProbeScriptTests(unittest.TestCase):
    def test_cli_writes_no_files_by_default(self):
        before = sorted(path.name for path in GENERATED.glob("*"))
        result = run_cmd(["scripts/run_h2_package_live_probe.py", "--source-id", "crates_io", "--request-key", "example_package_metadata"])
        after = sorted(path.name for path in GENERATED.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)

    def test_cli_live_without_approval_is_blocked_offline(self):
        result = run_cmd(["scripts/run_h2_package_live_probe.py", "--source-id", "crates_io", "--request-key", "example_package_metadata", "--live", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        live = json.loads(result.stdout)["live_probe"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_cli_writes_explicit_outputs_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_cmd([
                "scripts/run_h2_package_live_probe.py",
                "--source-id",
                "crates_io",
                "--request-key",
                "example_package_metadata",
                "--output",
                str(tmp_path / "result.json"),
                "--identity-output",
                str(tmp_path / "identity.json"),
                "--dependency-output",
                str(tmp_path / "dependencies.json"),
                "--file-candidate-output",
                str(tmp_path / "files.json"),
                "--source-cache-output",
                str(tmp_path / "source-cache.json"),
                "--evidence-preview-output",
                str(tmp_path / "evidence.json"),
                "--review-seed-output",
                str(tmp_path / "review.json"),
                "--health-output",
                str(tmp_path / "health.json"),
                "--summary-output",
                str(tmp_path / "summary.md"),
            ])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))["source_id"], "crates_io")
            self.assertTrue((tmp_path / "summary.md").is_file())

    def test_cli_refuses_site_dist_output(self):
        result = run_cmd(["scripts/run_h2_package_live_probe.py", "--source-id", "crates_io", "--request-key", "example_package_metadata", "--output", "site/dist/h2.json"])
        self.assertNotEqual(result.returncode, 0)

    def test_cli_refuses_data_public_index_output(self):
        result = run_cmd(["scripts/run_h2_package_live_probe.py", "--source-id", "crates_io", "--request-key", "example_package_metadata", "--output", "site/dist/data/public_index/h2.json"])
        self.assertNotEqual(result.returncode, 0)

    def test_summary_script_passes_on_examples(self):
        result = run_cmd(["scripts/summarize_h2_package_live_probe_outputs.py", "--input", "examples/connectors/h2_package_registries/live_probe_results", "--check", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["network_used"])
        self.assertGreaterEqual(payload["blocked_count"], 8)

    def test_validator_passes_current_repo(self):
        result = run_cmd(["scripts/validate_h2_package_live_probe.py", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "valid")

    def test_runtime_does_not_import_model_or_provider_libraries(self):
        text = RUNNER.read_text(encoding="utf-8") + SUMMARY.read_text(encoding="utf-8") + VALIDATOR.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        result = run_cmd(["scripts/validate_h2_package_live_probe.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
