from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "remediate_legacy_runtime_leakage.py"
VALIDATOR = ROOT / "scripts" / "validate_legacy_runtime_leakage_remediation.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("remediate_legacy_runtime_leakage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LegacyRuntimeLeakageRemediationTests(unittest.TestCase):
    def run_script(self, *args: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_remediation_script_defaults_to_dry_run(self):
        proc = self.run_script("--json")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["applied"])

    def test_remediation_script_refuses_forbidden_roots(self):
        proc = self.run_script("--dry-run", "--output", "runtime/forbidden.json", "--json")
        self.assertNotEqual(0, proc.returncode)
        payload = json.loads(proc.stdout)
        self.assertEqual("fail", payload["result"]["status"])

    def test_remediation_script_refuses_broad_delete(self):
        proc = self.run_script("--dry-run", "--delete", "--json")
        self.assertNotEqual(0, proc.returncode)
        payload = json.loads(proc.stdout)
        self.assertIn("broad deletion", " ".join(payload["errors"]))

    def test_classifies_h_series_runtime_path(self):
        module = load_script_module()
        classification = module.classify_finding("runtime/connectors/h14_source_discovery/rollup.py", "H14")
        self.assertEqual("prototype_runtime_to_quarantine", classification)

    def test_classifies_validator_policy_usage_as_allowed(self):
        module = load_script_module()
        classification = module.classify_finding("scripts/validate_runtime_architecture_leakage.py", "truth_boundary")
        self.assertEqual("validator_policy_ok", classification)

    def test_preserves_clean_r0_seam_fixture(self):
        module = load_script_module()
        self.assertEqual("must_fix_now", module.classify_finding("runtime/source_cache/store.py", "truth_boundary"))

    def test_reference_replacements_cover_imports_and_paths(self):
        module = load_script_module()
        replacements = dict(module.build_reference_replacements(["h1_metadata_wave"]))
        self.assertEqual(
            "control.prototypes.legacy_runtime.connectors.h1_metadata_wave",
            replacements["runtime.connectors.h1_metadata_wave"],
        )
        self.assertEqual(
            "control/prototypes/legacy_runtime/connectors/h1_metadata_wave",
            replacements["runtime/connectors/h1_metadata_wave"],
        )

    def test_detects_legacy_connector_dirs_in_temp_repo(self):
        module = load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runtime/connectors/h1_metadata_wave").mkdir(parents=True)
            (root / "runtime/connectors/github_releases").mkdir(parents=True)
            names = sorted(
                path.name
                for path in (root / "runtime/connectors").iterdir()
                if path.is_dir() and module.is_legacy_connector_name(path.name)
            )
            self.assertEqual(["h1_metadata_wave"], names)

    def test_validator_passes_current_repo(self):
        if not (ROOT / "control/inventory/legacy_runtime_leakage_remediation_result.json").exists():
            self.skipTest("remediation has not been applied yet")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
