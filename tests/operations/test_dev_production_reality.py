from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "audit_dev_production_reality.py"
VALIDATOR = ROOT / "scripts" / "validate_dev_production_reality.py"
REPORT = ROOT / "control" / "audits" / "r0-01-dev-production-reality-inventory-v0" / "r0_01_report.json"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_dev_production_reality", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_repo(root: Path) -> None:
    write(root / "runtime/connectors/h1_metadata_wave/__init__.py", '"""Fixture-only normalizers for the H1 metadata wave."""\nH1_SOURCE_IDS = ["pypi"]\n')
    write(
        root / "runtime/connectors/h1_metadata_wave/live_probe_common.py",
        """
POLICY_PATHS = {}
SOURCE_CONFIGS = {}
ENDPOINT_URL_TEMPLATES = {}
def build_h1_live_probe_request(): pass
def fetch_h1_metadata_once(): urlopen = None
def normalize_h1_live_probe_result(): pass
def build_h1_source_cache_candidate_preview(): pass
def build_h1_evidence_candidate_preview(): pass
def build_h1_review_queue_seed_preview(): pass
def detect_truth_boundary_violations(): pass
def build_h1_connector_health_summary(): pass
""",
    )
    write(root / "runtime/local_foundry/source_cache.py", '"""Fixture-only local source cache helpers with no runtime side effects."""\n')
    write(root / "contracts/control_schemas/previews/h1/connectors/live_probe_result.v0.json", "{}")
    write(root / "docs/operations/EMPTY.md", "")
    write(root / "scripts/validate_fixture.py", "from pathlib import Path\nREQUIRED = ['a']\nassert Path('a').exists()\n")
    write(root / "tests/operations/test_fixture.py", "from pathlib import Path\n\ndef test_files():\n    assert Path('a').is_file()\n")
    write(root / ".aide/reports/eureka-repo-health.json", '{"production_readiness": false, "current_queue_item": "F0-BUNDLE-01"}')
    write(root / ".aide/context/latest-task-packet.md", "F0-BUNDLE-01")
    write(root / ".aide/queue/index.yaml", "current_recommended_task: F0-BUNDLE-01\n")
    write(root / "control/audits/h14-bundle-04-source-discovery-review-quality-audit-v0/h14_bundle_04_report.json", '{"h14_exit_gate": "PASS_WITH_WARNINGS"}')


class DevProductionRealityTests(unittest.TestCase):
    def run_script(self, *args: str, cwd: Path = ROOT):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, text=True, capture_output=True, check=False)

    def test_audit_script_runs_in_check_mode_and_produces_core_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            proc = self.run_script("--repo-root", str(repo), "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertIn("artifact_taxonomy", payload)
            self.assertIn("runtime_maturity_matrix", payload)
            self.assertEqual("R0-02 - Runtime architecture leakage gate", payload["r0_report"]["recommended_next_task"])

    def test_audit_detects_fixture_runtime_leakage_placeholders_and_contract_taxonomy(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            module = load_audit_module()
            audit = module.build_reality_audit(repo)
            artifacts = {item["path"]: item for item in audit["artifact_taxonomy"]["artifacts"]}
            self.assertEqual("fixture_runtime", artifacts["runtime/connectors/h1_metadata_wave/__init__.py"]["artifact_kind"])
            self.assertEqual("empty_or_zero_byte", artifacts["docs/operations/EMPTY.md"]["maturity"])
            self.assertEqual("preview_contract", artifacts["contracts/control_schemas/previews/h1/connectors/live_probe_result.v0.json"]["artifact_kind"])
            leak_terms = {item["term"] for item in audit["runtime_architecture_leakage_report"]["leaks"]}
            self.assertIn("H1", leak_terms)
            god = artifacts["runtime/connectors/h1_metadata_wave/live_probe_common.py"]["signals"]
            self.assertTrue(any(signal.startswith("god_module_aspects:") for signal in god))

    def test_audit_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
            proc = self.run_script("--repo-root", str(repo), "--check")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
            self.assertEqual(before, after)
            self.assertIn("wrote_files: false", proc.stdout)

    def test_audit_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            make_fixture_repo(repo)
            out_json = Path(tmp) / "artifact_inventory.json"
            out_md = Path(tmp) / "summary.md"
            proc = self.run_script("--repo-root", str(repo), "--output", str(out_json), "--summary-output", str(out_md))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out_json.is_file())
            self.assertTrue(out_md.is_file())
            self.assertEqual("r0.artifact_taxonomy.v0", json.loads(out_json.read_text(encoding="utf-8"))["schema_version"])

    def test_audit_refuses_forbidden_output_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            proc = self.run_script("--repo-root", str(repo), "--output", str(repo / "runtime/report.json"))
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing forbidden output root", proc.stdout + proc.stderr)

    def test_audit_script_does_not_import_live_network_or_provider_modules(self):
        module_text = SCRIPT.read_text(encoding="utf-8")
        forbidden_imports = ("import urllib", "from urllib", "import requests", "import httpx", "import openai", "import anthropic", "import socket")
        for marker in forbidden_imports:
            self.assertNotIn(marker, module_text)
        self.assertNotIn("urlopen(", module_text)

    def test_validator_passes_current_r0_outputs(self):
        proc = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_r0_report_blocks_f0_and_dev_to_main(self):
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual("R0-02 - Runtime architecture leakage gate", payload["recommended_next_task"])
        self.assertIs(payload["f0_should_remain_blocked"], True)
        self.assertIs(payload["dev_to_main_should_remain_blocked"], True)


if __name__ == "__main__":
    unittest.main()
