import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "audit_track_b_integration.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_track_b_integration", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


audit = load_audit_module()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class TrackBIntegrationAuditTest(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def make_fixture(self, root: Path):
        report = {
            "schema_version": "fixture_report.v0",
            "status": "pass",
            "truth_boundary": {
                "accepted_public_truth_created": False,
                "accepted_evidence_truth_created": False,
                "master_index_mutated": False,
            },
            "product_boundary": {
                "enabled_network_access": False,
                "mutated_public_index": False,
                "mutated_master_index": False,
            },
        }
        files = [
            "contracts/node/example.v0.json",
            "control/inventory/example_policy.json",
            "runtime/local/foundry/example_runtime.py",
            "scripts/example_validator.py",
            "tests/operations/example_test.py",
            "examples/example_record.json",
            "docs/reference/EXAMPLE.md",
            "control/audits/example/README.md",
        ]
        for rel in files:
            if rel.endswith(".json"):
                write_json(root / rel, {"schema_version": "fixture.v0"})
            else:
                write_text(root / rel, "")
        write_json(root / "control/audits/example/track_b_00_report.json", report)
        matrix = {
            "schema_version": "track_b_completion_matrix.v0",
            "tasks": [
                {
                    "task_id": "TRACK-B-00",
                    "label": "Fixture task",
                    "artifact_paths": ["docs/reference/EXAMPLE.md"],
                    "contract_paths": ["contracts/node/example.v0.json"],
                    "policy_paths": ["control/inventory/example_policy.json"],
                    "runtime_paths": ["runtime/local/foundry/example_runtime.py"],
                    "script_paths": ["scripts/example_validator.py"],
                    "validator_paths": ["scripts/example_validator.py"],
                    "test_paths": ["tests/operations/example_test.py"],
                    "example_paths": ["examples/example_record.json"],
                    "audit_paths": ["control/audits/example"],
                    "known_warnings": [],
                    "product_boundary_preserved": True,
                    "truth_boundary_preserved": True,
                }
            ],
            "contract_families": ["contracts/node"],
            "runtime_families": ["runtime/local/foundry/example_runtime.py"],
            "validator_families": ["scripts/example_validator.py"],
            "policy_families": ["control/inventory/example_policy.json"],
            "example_families": ["examples/example_record.json"],
            "audit_packs": ["control/audits/example"],
            "deferred_work": [],
            "known_gaps": [],
        }
        write_json(root / "control/inventory/track_b_completion_matrix.json", matrix)

    def test_audit_script_check_passes_current_repo(self):
        result = self.run_script("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("critical_blockers: 0", result.stdout)

    def test_list_output_is_non_empty(self):
        result = self.run_script("--list")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TRACK-B-01", result.stdout)

    def test_json_output_writes_deterministic_report_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "track_b_audit.json"
            result = self.run_script("--json-output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], "track_b_23_report.v0")
            self.assertEqual(sorted(data), list(data.keys()))

    def test_missing_expected_artifact_is_reported_in_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            (root / "examples/example_record.json").unlink()
            result = audit.audit_repo(root)
            self.assertTrue(any("missing expected path" in item for item in result["critical_blockers"]))

    def test_product_boundary_true_claim_fails_in_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            report_path = root / "control/audits/example/track_b_00_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["product_boundary"]["enabled_network_access"] = True
            write_json(report_path, report)
            result = audit.audit_repo(root)
            self.assertTrue(any("product boundary violation" in item for item in result["critical_blockers"]))

    def test_truth_boundary_true_claim_fails_in_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            report_path = root / "control/audits/example/track_b_00_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["truth_boundary"]["accepted_public_truth_created"] = True
            write_json(report_path, report)
            result = audit.audit_repo(root)
            self.assertTrue(any("truth boundary violation" in item for item in result["critical_blockers"]))

    def test_invalid_json_inventory_fails_in_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            (root / "control/inventory/track_b_completion_matrix.json").write_text("{", encoding="utf-8")
            result = audit.audit_repo(root)
            self.assertTrue(any("invalid matrix JSON" in item for item in result["critical_blockers"]))

    def test_forbidden_output_root_presence_is_detected_in_strict_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            write_text(root / "site/dist/generated.txt", "do not create")
            result = audit.audit_repo(root, strict_forbidden_roots=True)
            self.assertTrue(any("forbidden output root exists" in item for item in result["critical_blockers"]))

    def test_audit_does_not_mutate_site_dist_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            target = root / "site/dist/existing.txt"
            write_text(target, "stable")
            before = target.read_text(encoding="utf-8")
            audit.audit_repo(root, strict_forbidden_roots=False)
            after = target.read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_script_has_no_network_or_model_provider_imports(self):
        matrix = {
            "tasks": [
                {
                    "runtime_paths": [],
                    "script_paths": ["scripts/audit_track_b_integration.py"],
                    "validator_paths": [],
                }
            ]
        }
        self.assertEqual(audit.check_banned_imports(REPO_ROOT, matrix), [])

    def test_script_does_not_run_connector_probes(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("validate_internet_archive_metadata_connector", text)
        self.assertNotIn("run_connector_probe", text)


if __name__ == "__main__":
    unittest.main()
