import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INTEGRATE = REPO_ROOT / "scripts/integrate_h2_package_review.py"
QUALITY = REPO_ROOT / "scripts/summarize_h2_package_quality_delta.py"
VALIDATOR = REPO_ROOT / "scripts/validate_h2_package_review_quality_audit.py"


class H2PackageReviewQualityScriptsTest(unittest.TestCase):
    def run_integrate(self, *args):
        return subprocess.run([sys.executable, str(INTEGRATE), *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)

    def run_quality(self, *args):
        return subprocess.run([sys.executable, str(QUALITY), *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)

    def test_scripts_write_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/connectors/h2_package_registries/review_integration").glob("*.json"))
        result = self.run_integrate("--input-dir", "examples/connectors/h2_package_registries/replay_results", "--json")
        after = sorted(path.name for path in (REPO_ROOT / "examples/connectors/h2_package_registries/review_integration").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(json.loads(result.stdout)["wrote_files"])

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "review"
            result = self.run_integrate("--input-dir", "examples/connectors/h2_package_registries/replay_results", "--output-dir", str(out_dir))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((out_dir / "h2_review_integration_result_v0.json").is_file())
            quality = self.run_quality("--input-dir", str(out_dir), "--output", str(Path(tmp) / "quality.json"), "--summary-output", str(Path(tmp) / "quality.md"))
            self.assertEqual(quality.returncode, 0, quality.stdout + quality.stderr)
            payload = json.loads((Path(tmp) / "quality.json").read_text(encoding="utf-8"))
            self.assertFalse(payload["truth_boundary"]["package_installability_verified"])

    def test_scripts_refuse_site_dist_output(self):
        result = self.run_integrate("--input-dir", "examples/connectors/h2_package_registries/replay_results", "--output-dir", "site/dist/h2-review")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_scripts_refuse_data_public_index_output(self):
        result = self.run_quality("--input-dir", "examples/connectors/h2_package_registries/review_integration", "--output", "site/dist/data/public_index/h2-quality.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_scripts_refuse_package_cache_roots(self):
        result = self.run_quality("--input-dir", "examples/connectors/h2_package_registries/review_integration", "--output", "package_cache/h2-quality.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_validator_passes_current_repo(self):
        result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_scripts_do_not_import_network_model_or_provider_clients(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (INTEGRATE, QUALITY, VALIDATOR))
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        subprocess.run([sys.executable, str(VALIDATOR)], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
