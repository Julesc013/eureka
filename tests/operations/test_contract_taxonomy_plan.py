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
SCRIPT = ROOT / "scripts" / "audit_contract_taxonomy.py"
VALIDATOR = ROOT / "scripts" / "validate_contract_taxonomy_plan.py"
TAXONOMY_POLICY = ROOT / "control" / "policies" / "contract_taxonomy_policy.json"
MIGRATION_POLICY = ROOT / "control" / "policies" / "contract_migration_policy.json"
REPORT = ROOT / "control" / "audits" / "r0-03a-contract-taxonomy-refactor-plan-v0" / "r0_03a_report.json"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_contract_taxonomy", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_repo(root: Path) -> None:
    write(root / "control/policies/contract_taxonomy_policy.json", TAXONOMY_POLICY.read_text(encoding="utf-8"))
    write(root / "control/policies/contract_migration_policy.json", MIGRATION_POLICY.read_text(encoding="utf-8"))
    write(root / "contracts/domain/source_record.v0.json", '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object"}\n')
    write(root / "contracts/schema/control/audits/h14/connectors/source_discovery_quality_delta_report.v0.json", '{"type":"object"}\n')
    write(root / "contracts/schema/control/fixtures/h1/connectors/metadata_fixture_replay_result.v0.json", '{"type":"object"}\n')
    write(root / "contracts/schema/control/previews/native/native_release_candidate_preview.v0.json", '{"type":"object"}\n')
    write(root / "contracts/domain/h14_bundle_quality_delta.v0.json", '{"type":"object"}\n')
    write(root / "contracts/domain/empty_contract.v0.json", "")
    write(root / "scripts/validate_source_record.py", "PATH = 'contracts/domain/source_record.v0.json'\n")
    write(root / "tests/operations/test_source_record.py", "SCHEMA = 'contracts/domain/source_record.v0.json'\n")


class ContractTaxonomyPlanTests(unittest.TestCase):
    def run_script(self, repo: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(repo), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_taxonomy_policy_validates(self):
        payload = json.loads(TAXONOMY_POLICY.read_text(encoding="utf-8"))
        self.assertEqual("contract_taxonomy_policy.v0", payload["schema_version"])
        self.assertIn("product_domain_contract", payload["contract_classes"])
        self.assertIn("contracts/schema/control/audits/", payload["target_roots"].values())
        self.assertIn("h14", payload["forbidden_product_contract_signals"])

    def test_migration_policy_validates(self):
        payload = json.loads(MIGRATION_POLICY.read_text(encoding="utf-8"))
        self.assertEqual("contract_migration_policy.v0", payload["schema_version"])
        self.assertIs(payload["planning_only_current"], True)
        self.assertIs(payload["migration_allowed_current"], False)
        self.assertIs(payload["f0_blocked_until_complete"], True)

    def test_audit_script_runs_in_check_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            proc = self.run_script(repo, "--check", "--json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual("R0-03A", payload["task"])
            self.assertEqual(6, payload["r0_03a_report"]["contract_count"])

    def test_classifies_product_contract_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            contracts = {item["path"]: item for item in audit["contract_taxonomy_inventory"]["contracts"]}
            item = contracts["contracts/domain/source_record.v0.json"]
            self.assertEqual("product_domain_contract", item["contract_class"])
            self.assertEqual("keep", item["recommended_action"])

    def test_classifies_audit_schema_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            item = {entry["path"]: entry for entry in audit["contract_taxonomy_inventory"]["contracts"]}[
                "contracts/schema/control/audits/h14/connectors/source_discovery_quality_delta_report.v0.json"
            ]
            self.assertEqual("audit_schema", item["contract_class"])
            self.assertTrue(item["target_path"].startswith("contracts/schema/control/audits/h14/"))

    def test_classifies_fixture_schema_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            item = {entry["path"]: entry for entry in audit["contract_taxonomy_inventory"]["contracts"]}[
                "contracts/schema/control/fixtures/h1/connectors/metadata_fixture_replay_result.v0.json"
            ]
            self.assertEqual("fixture_schema", item["contract_class"])
            self.assertIn("control_schema_fixture_path", item["signals"])

    def test_classifies_preview_schema_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            item = {entry["path"]: entry for entry in audit["contract_taxonomy_inventory"]["contracts"]}[
                "contracts/schema/control/previews/native/native_release_candidate_preview.v0.json"
            ]
            self.assertEqual("preview_schema", item["contract_class"])
            self.assertTrue(item["target_path"].startswith("contracts/schema/control/previews/"))

    def test_detects_phase_bundle_quality_delta_in_product_contract_like_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            item = {entry["path"]: entry for entry in audit["contract_taxonomy_inventory"]["contracts"]}[
                "contracts/domain/h14_bundle_quality_delta.v0.json"
            ]
            self.assertIn("task_or_bundle_named", item["signals"])
            self.assertIn(item["recommended_action"], {"move_and_rename", "move"})

    def test_detects_zero_byte_or_near_empty_contract_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            item = {entry["path"]: entry for entry in audit["contract_taxonomy_inventory"]["contracts"]}[
                "contracts/domain/empty_contract.v0.json"
            ]
            self.assertEqual("empty_or_zero_byte", item["maturity"])
            self.assertEqual("delete_later_if_unreferenced", item["recommended_action"])

    def test_builds_reference_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            edges = audit["contract_reference_graph"]["edges"]
            self.assertTrue(any(edge["to_path"] == "contracts/domain/source_record.v0.json" for edge in edges))
            self.assertTrue(any(edge["edge_kind"] == "validates" for edge in edges))

    def test_proposes_target_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            audit = load_audit_module().build_contract_taxonomy_audit(repo)
            item = {entry["path"]: entry for entry in audit["contract_taxonomy_inventory"]["contracts"]}[
                "contracts/schema/control/audits/h14/connectors/source_discovery_quality_delta_report.v0.json"
            ]
            self.assertEqual("contracts/schema/control/audits/h14/connectors/source_discovery_quality_delta_report.v0.json", item["target_path"])

    def test_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
            proc = self.run_script(repo, "--check")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
            self.assertEqual(before, after)

    def test_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            make_fixture_repo(repo)
            out_inventory = Path(tmp) / "inventory.json"
            out_migration = Path(tmp) / "migration.json"
            out_reference = Path(tmp) / "reference.json"
            out_summary = Path(tmp) / "summary.md"
            proc = self.run_script(
                repo,
                "--output",
                str(out_inventory),
                "--migration-output",
                str(out_migration),
                "--reference-output",
                str(out_reference),
                "--summary-output",
                str(out_summary),
            )
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertEqual("contract_taxonomy_inventory.v0", json.loads(out_inventory.read_text(encoding="utf-8"))["schema_version"])
            self.assertEqual("contract_migration_plan.v0", json.loads(out_migration.read_text(encoding="utf-8"))["schema_version"])
            self.assertEqual("contract_reference_graph.v0", json.loads(out_reference.read_text(encoding="utf-8"))["schema_version"])
            self.assertTrue(out_summary.read_text(encoding="utf-8").startswith("# Contract Taxonomy Summary"))

    def test_refuses_forbidden_output_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            proc = self.run_script(repo, "--output", str(repo / "contracts/report.json"))
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing forbidden output root", proc.stdout + proc.stderr)

    def test_validator_confirms_no_contract_files_moved_and_recommends_r0_03b(self):
        proc = subprocess.run([sys.executable, str(VALIDATOR), "--json"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIs(payload["contracts_moved"], False)
        self.assertEqual("R0-03B — Contract taxonomy refactor execution", payload["recommended_next_task"])

    def test_validator_does_not_call_network_or_provider(self):
        for path in (SCRIPT, VALIDATOR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertNotIn("urllib", {alias.name.split(".")[0] for alias in node.names})
                    self.assertNotIn("requests", {alias.name.split(".")[0] for alias in node.names})
                    self.assertNotIn("openai", {alias.name.split(".")[0] for alias in node.names})
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn((node.module or "").split(".")[0], {"urllib", "requests", "openai", "anthropic", "runtime"})

    def test_r0_report_blocks_f0_and_dev_to_main(self):
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertIs(payload["f0_should_remain_blocked"], True)
        self.assertIs(payload["dev_to_main_should_remain_blocked"], True)
        self.assertEqual("R0-03B — Contract taxonomy refactor execution", payload["recommended_next_task"])


if __name__ == "__main__":
    unittest.main()
