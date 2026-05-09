import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INTEGRATION_CLI = REPO_ROOT / "scripts/integrate_ia_metadata_review.py"
QUALITY_CLI = REPO_ROOT / "scripts/summarize_ia_connector_quality_delta.py"
VALIDATOR = REPO_ROOT / "scripts/validate_ia_review_integration.py"
IA02_GENERATED = REPO_ROOT / "control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/generated"


class IAReviewIntegrationScriptsTest(unittest.TestCase):
    def run_integration(self, *args):
        return subprocess.run(
            [sys.executable, str(INTEGRATION_CLI), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def run_quality(self, *args):
        return subprocess.run(
            [sys.executable, str(QUALITY_CLI), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_scripts_write_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/connectors/internet_archive/review_integration").glob("*.json"))
        result = self.run_integration(
            "--source-cache-candidate",
            str(IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json"),
            "--evidence-preview",
            str(IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json"),
            "--json",
        )
        after = sorted(path.name for path in (REPO_ROOT / "examples/connectors/internet_archive/review_integration").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertEqual(json.loads(result.stdout)["integration_status"], "blocked_dry_run")

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            integration = self.run_integration(
                "--source-cache-candidate",
                str(IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json"),
                "--evidence-preview",
                str(IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json"),
                "--output-dir",
                str(root),
            )
            self.assertEqual(integration.returncode, 0, integration.stdout + integration.stderr)
            self.assertTrue((root / "sample_ia_source_cache_review_entry.json").is_file())
            quality = self.run_quality(
                "--input-dir",
                str(root),
                "--output",
                str(root / "quality.json"),
                "--postmortem-output",
                str(root / "postmortem.json"),
                "--h0-output",
                str(root / "h0.json"),
            )
            self.assertEqual(quality.returncode, 0, quality.stdout + quality.stderr)
            self.assertFalse(json.loads((root / "quality.json").read_text(encoding="utf-8"))["claims_production_readiness"])
            self.assertFalse(json.loads((root / "postmortem.json").read_text(encoding="utf-8"))["auto_approves_future_connectors"])

    def test_forbidden_output_roots_are_rejected(self):
        result = self.run_integration(
            "--source-cache-candidate",
            str(IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json"),
            "--evidence-preview",
            str(IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json"),
            "--output-dir",
            "site/dist/ia-review",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_data_public_index_output_root_is_rejected(self):
        result = self.run_integration(
            "--source-cache-candidate",
            str(IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json"),
            "--evidence-preview",
            str(IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json"),
            "--output-dir",
            "data/public_index/ia-review",
        )
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

    def test_scripts_do_not_import_network_model_or_provider_clients(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (INTEGRATION_CLI, QUALITY_CLI, VALIDATOR))
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_runtime_does_not_create_local_private_roots(self):
        self.run_integration(
            "--source-cache-candidate",
            str(IA02_GENERATED / "sample_source_cache_candidate_from_live_probe.json"),
            "--evidence-preview",
            str(IA02_GENERATED / "sample_evidence_candidate_preview_from_live_probe.json"),
            "--check",
        )
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
