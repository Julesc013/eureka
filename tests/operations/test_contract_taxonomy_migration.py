from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EXECUTOR = ROOT / "scripts" / "execute_contract_taxonomy_migration.py"
VALIDATOR = ROOT / "scripts" / "validate_contract_taxonomy_migration.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_plan(root: Path) -> Path:
    write(root / "contracts/audits/example_audit_report.v0.json", '{"type":"object"}\n')
    write(root / "contracts/connectors/h1_metadata_fixture_replay_result.v0.json", '{"type":"object"}\n')
    write(root / "contracts/native/native_release_candidate_preview.v0.json", '{"type":"object"}\n')
    write(root / "contracts/domain/source_record.v0.json", '{"type":"object"}\n')
    write(root / "contracts/domain/mystery.v0.json", '{"type":"object"}\n')
    plan = {
        "schema_version": "contract_migration_plan.v0",
        "generated_for": "R0-03A",
        "migration_allowed_now": False,
        "r0_03b_ready": True,
        "moves": [
            {
                "source_path": "contracts/audits/example_audit_report.v0.json",
                "target_path": "contracts/schema/control/audits/audits/example_audit_report.v0.json",
                "action": "move",
                "contract_class_before": "audit_schema",
                "contract_class_after": "audit_schema",
                "rationale": "audit schema",
                "references_to_update": ["tests/operations/test_example.py"],
                "compatibility_shim_required": True,
                "risk": "medium",
                "validation": [],
            },
            {
                "source_path": "contracts/connectors/h1_metadata_fixture_replay_result.v0.json",
                "target_path": "contracts/schema/control/fixtures/h1/connectors/metadata_fixture_replay_result.v0.json",
                "action": "move_and_rename",
                "contract_class_before": "fixture_schema",
                "contract_class_after": "fixture_schema",
                "rationale": "fixture schema",
                "references_to_update": [],
                "compatibility_shim_required": True,
                "risk": "medium",
                "validation": [],
            },
            {
                "source_path": "contracts/native/native_release_candidate_preview.v0.json",
                "target_path": "contracts/schema/control/previews/native/native_release_candidate_preview.v0.json",
                "action": "move",
                "contract_class_before": "preview_schema",
                "contract_class_after": "preview_schema",
                "rationale": "preview schema",
                "references_to_update": [],
                "compatibility_shim_required": True,
                "risk": "medium",
                "validation": [],
            },
            {
                "source_path": "contracts/domain/source_record.v0.json",
                "target_path": "contracts/domain/source_record.v0.json",
                "action": "keep",
                "contract_class_before": "product_domain_contract",
                "contract_class_after": "product_domain_contract",
                "rationale": "product contract",
                "references_to_update": [],
                "compatibility_shim_required": False,
                "risk": "low",
                "validation": [],
            },
            {
                "source_path": "contracts/domain/mystery.v0.json",
                "target_path": "contracts/schema/control/deprecated/domain/mystery.v0.json",
                "action": "investigate",
                "contract_class_before": "unknown",
                "contract_class_after": "unknown",
                "rationale": "unknown",
                "references_to_update": [],
                "compatibility_shim_required": True,
                "risk": "high",
                "validation": [],
            },
        ],
        "do_not_move": [],
        "do_not_delete": [],
        "blocked_items": [],
    }
    path = root / "control/inventory/contract_migration_plan.json"
    write(path, json.dumps(plan, indent=2) + "\n")
    write(root / "tests/operations/test_example.py", "SCHEMA = 'contracts/audits/example_audit_report.v0.json'\n")
    return path


class ContractTaxonomyMigrationTests(unittest.TestCase):
    def run_executor(self, repo: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(EXECUTOR), "--repo-root", str(repo), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_executor_defaults_to_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            proc = self.run_executor(repo, "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual("dry_run", payload["mode"])
            self.assertTrue((repo / "contracts/audits/example_audit_report.v0.json").exists())

    def test_executor_refuses_without_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proc = self.run_executor(repo, "--apply", "--json")
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("missing R0-03A migration plan", proc.stdout + proc.stderr)

    def test_executor_moves_only_batch_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            proc = self.run_executor(repo, "--apply", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(3, payload["moves_completed"])
            self.assertTrue((repo / "contracts/schema/control/audits/audits/example_audit_report.v0.json").exists())
            self.assertTrue((repo / "contracts/schema/control/fixtures/h1/connectors/metadata_fixture_replay_result.v0.json").exists())
            self.assertTrue((repo / "contracts/schema/control/previews/native/native_release_candidate_preview.v0.json").exists())
            self.assertTrue((repo / "contracts/domain/source_record.v0.json").exists())
            self.assertTrue((repo / "contracts/domain/mystery.v0.json").exists())

    def test_executor_does_not_move_product_or_unknown_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            proc = self.run_executor(repo, "--apply", "--json")
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["product_contracts_moved"])
            self.assertEqual(0, payload["unknown_contracts_moved"])

    def test_executor_never_deletes_schemas(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            proc = self.run_executor(repo, "--apply", "--json")
            payload = json.loads(proc.stdout)
            self.assertEqual(0, payload["schemas_deleted"])

    def test_executor_refuses_forbidden_output_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            proc = self.run_executor(repo, "--output", str(repo / "runtime/report.json"))
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing forbidden output root", proc.stdout + proc.stderr)

    def test_executor_writes_explicit_output_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            make_plan(repo)
            out = Path(tmp) / "result.json"
            proc = self.run_executor(repo, "--apply", "--output", str(out))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertEqual("r0_03b_1_migration_result.v0", json.loads(out.read_text(encoding="utf-8"))["schema_version"])

    def test_validator_validates_moved_schema_exists(self):
        module = load_module(VALIDATOR, "validate_contract_taxonomy_migration")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            result = load_module(EXECUTOR, "execute_contract_taxonomy_migration").execute_migration(
                repo,
                json.loads((repo / "control/inventory/contract_migration_plan.json").read_text(encoding="utf-8")),
                mode="apply",
                update_references=False,
            )
            errors: list[str] = []
            module.validate_migration_payload(repo, result["migration_result"], errors)
            self.assertFalse(errors)

    def test_validator_detects_missing_target(self):
        module = load_module(VALIDATOR, "validate_contract_taxonomy_migration")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan(repo)
            payload = {
                "task": "R0-03B-1",
                "status": "pass",
                "schemas_deleted": 0,
                "product_contracts_moved": 0,
                "unknown_contracts_moved": 0,
                "runtime_files_modified": 0,
                "f0_should_remain_blocked": True,
                "dev_to_main_should_remain_blocked": True,
                "moved": [
                    {
                        "source_path": "contracts/audits/example_audit_report.v0.json",
                        "target_path": "contracts/schema/control/audits/audits/example_audit_report.v0.json",
                        "contract_class": "audit_schema",
                    }
                ],
                "blocked": [],
            }
            errors: list[str] = []
            module.validate_migration_payload(repo, payload, errors)
            self.assertTrue(any("moved target is missing" in error for error in errors))

    def test_validator_detects_accidental_product_contract_move(self):
        module = load_module(VALIDATOR, "validate_contract_taxonomy_migration")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(repo / "contracts/schema/control/audits/domain/source_record.v0.json", "{}\n")
            payload = {
                "task": "R0-03B-1",
                "status": "pass",
                "schemas_deleted": 0,
                "product_contracts_moved": 1,
                "unknown_contracts_moved": 0,
                "runtime_files_modified": 0,
                "f0_should_remain_blocked": True,
                "dev_to_main_should_remain_blocked": True,
                "moved": [
                    {
                        "source_path": "contracts/domain/source_record.v0.json",
                        "target_path": "contracts/schema/control/audits/domain/source_record.v0.json",
                        "contract_class": "product_domain_contract",
                    }
                ],
                "blocked": [],
            }
            errors: list[str] = []
            module.validate_migration_payload(repo, payload, errors)
            self.assertTrue(any("product_contracts_moved" in error or "disallowed class" in error for error in errors))

    def test_validator_detects_runtime_file_modification(self):
        module = load_module(VALIDATOR, "validate_contract_taxonomy_migration")
        payload = {
            "task": "R0-03B-1",
            "status": "pass",
            "schemas_deleted": 0,
            "product_contracts_moved": 0,
            "unknown_contracts_moved": 0,
            "runtime_files_modified": 1,
            "f0_should_remain_blocked": True,
            "dev_to_main_should_remain_blocked": True,
            "moved": [],
            "blocked": [],
        }
        errors: list[str] = []
        module.validate_migration_payload(ROOT, payload, errors)
        self.assertTrue(any("runtime_files_modified" in error for error in errors))

    def test_validator_validates_reference_and_shim_reports(self):
        module = load_module(VALIDATOR, "validate_contract_taxonomy_migration")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(repo / "tests/operations/test_example.py", "SCHEMA = 'contracts/schema/control/audits/audits/example_audit_report.v0.json'\n")
            migration = {
                "moved": [{"source_path": "contracts/audits/example_audit_report.v0.json", "target_path": "contracts/schema/control/audits/audits/example_audit_report.v0.json"}],
                "blocked": [],
            }
            refs = {
                "updates": [
                    {
                        "path": "tests/operations/test_example.py",
                        "old_reference": "contracts/audits/example_audit_report.v0.json",
                        "new_reference": "contracts/schema/control/audits/audits/example_audit_report.v0.json",
                        "reason": "test",
                    }
                ],
                "unresolved_references": [],
                "historical_references_left_intact": [],
            }
            shims = {
                "shims": [
                    {
                        "old_path": "contracts/audits/example_audit_report.v0.json",
                        "new_path": "contracts/schema/control/audits/audits/example_audit_report.v0.json",
                        "shim_kind": "none",
                        "expires_after_task": "never",
                        "reason": "test",
                    }
                ]
            }
            errors: list[str] = []
            module.validate_reference_report(repo, migration, refs, errors)
            module.validate_shim_report(migration, shims, errors)
            self.assertFalse(errors)

    def test_r0_report_blocks_f0_and_dev_to_main(self):
        report = ROOT / "control/audits/r0-03b-1-contract-taxonomy-migration-v0/r0_03b_1_report.json"
        if report.exists():
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertIs(payload["f0_should_remain_blocked"], True)
            self.assertIs(payload["dev_to_main_should_remain_blocked"], True)

    def test_no_network_api_model_provider_imports(self):
        for path in (EXECUTOR, VALIDATOR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".")[0] for alias in node.names}
                    self.assertFalse(roots & {"urllib", "requests", "openai", "anthropic", "runtime"})
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn((node.module or "").split(".")[0], {"urllib", "requests", "openai", "anthropic", "runtime"})


if __name__ == "__main__":
    unittest.main()
