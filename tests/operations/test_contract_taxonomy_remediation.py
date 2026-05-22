import json
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import resolve_contract_taxonomy_blockers as resolver
from scripts import validate_contract_taxonomy_remediation as validator


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class ContractTaxonomyRemediationTests(unittest.TestCase):
    def make_repo(self) -> tempfile.TemporaryDirectory:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        unresolved = [{"path": path, "reason": "test", "severity": "high"} for path in resolver.REMEDIATION_MOVES]
        write_json(
            root / "control/inventory/r0_03b_2_unresolved_contracts.json",
            {"schema_version": "r0_03b_2_unresolved_contracts.v0", "task": "R0-03B-2", "unresolved": unresolved},
        )
        write_json(
            root / "control/inventory/r0_03b_2_final_contract_taxonomy.json",
            {"unresolved_contract_count": 19, "compatibility_shim_count": 19, "contracts_root_status": "partial"},
        )
        write_json(
            root / "control/inventory/r0_03b_1_compatibility_shim_report.json",
            {"shims": [{"old_path": old, "new_path": spec["target_path"]} for old, spec in resolver.REMEDIATION_MOVES.items()]},
        )
        write_json(root / "control/policies/contract_migration_policy.json", {"deletion_allowed_current": False})
        for source in resolver.REMEDIATION_MOVES:
            path = root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"schema": source}), encoding="utf-8")
        (root / "scripts").mkdir(exist_ok=True)
        (root / "scripts/validate_demo.py").write_text(
            'SCHEMA = "contracts/connectors/h14_source_need_candidate.v0.json"\n',
            encoding="utf-8",
        )
        return temp

    def taxonomy_patch(self):
        return mock.patch.object(
            resolver,
            "load_current_taxonomy",
            return_value={"contract_taxonomy_inventory": {"contracts": []}},
        )

    def test_resolver_defaults_to_dry_run(self) -> None:
        with self.make_repo() as temp, self.taxonomy_patch():
            root = Path(temp)
            code = resolver.main(["--repo-root", str(root), "--json"], stdout=io.StringIO(), stderr=io.StringIO())
            self.assertEqual(code, 0)
            self.assertTrue((root / "contracts/connectors/h14_source_need_candidate.v0.json").exists())

    def test_resolver_refuses_missing_unresolved_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            code = resolver.main(["--repo-root", temp, "--json"], stdout=io.StringIO(), stderr=io.StringIO())
            self.assertEqual(code, 1)

    def test_resolver_classifies_archive_fixture_contracts_as_fixture_schemas(self) -> None:
        spec = resolver.REMEDIATION_MOVES["contracts/archive/fixtures/software/synthetic_resolution_fixture.json"]
        self.assertEqual(spec["classification"], "fixture_schema")
        self.assertTrue(spec["target_path"].startswith("contracts/control_schemas/fixtures/archive/"))

    def test_resolver_classifies_h14_candidates_as_control_previews(self) -> None:
        h14 = [spec for old, spec in resolver.REMEDIATION_MOVES.items() if old.startswith("contracts/connectors/h14_")]
        self.assertTrue(h14)
        self.assertTrue(all(spec["classification"] == "preview_schema" for spec in h14))
        self.assertTrue(all(spec["target_path"].startswith("contracts/control_schemas/previews/h14/") for spec in h14))

    def test_resolver_moves_node_and_query_non_product_schemas(self) -> None:
        self.assertEqual(resolver.REMEDIATION_MOVES["contracts/node/work_unit.v0.json"]["target_path"], "contracts/control_schemas/policies/node/work_unit.v0.json")
        self.assertEqual(
            resolver.REMEDIATION_MOVES["contracts/query/observation_candidate_review_queue.v0.json"]["target_path"],
            "contracts/control_schemas/tasks/query/observation_candidate_review_queue.v0.json",
        )

    def test_resolver_updates_active_references_and_retires_shims(self) -> None:
        with self.make_repo() as temp, self.taxonomy_patch():
            root = Path(temp)
            result = resolver.resolve_taxonomy(root, apply_changes=True)
            self.assertEqual(result["remediation_result"]["unresolved_after"], 0)
            self.assertEqual(result["remediation_result"]["shims_retired"], 19)
            self.assertIn(
                "contracts/control_schemas/previews/h14/connectors/source_need_candidate.v0.json",
                (root / "scripts/validate_demo.py").read_text(encoding="utf-8"),
            )

    def test_resolver_refuses_to_delete_schemas_unless_policy_allows(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            write_json(root / "control/policies/contract_migration_policy.json", {"deletion_allowed_current": True})
            result = resolver.resolve_taxonomy(root, apply_changes=False)
            self.assertEqual(result["remediation_result"]["status"], "blocked")

    def test_validator_fails_if_fixture_schema_remains_under_contracts(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            write_json(
                root / "control/inventory/r0_contract_taxonomy_remediation_result.json",
                {"schema_version": "r0_contract_taxonomy_remediation_result.v0", "unresolved_after": 0, "compatibility_shims_after": 0, "contracts_clean_enough_for_f0": True, "f0_decision": "resume_f0", "dev_to_main_decision": "promotion_plan_only", "production_readiness_claimed": False, "public_launch_readiness_claimed": False},
            )
            write_json(root / "control/inventory/r0_contract_taxonomy_final_state.json", {"schema_version": "r0_contract_taxonomy_final_state.v0", "contracts_root_status": "clean"})
            write_json(
                root / "control/inventory/r0_contract_taxonomy_resolved_items.json",
                {"schema_version": "r0_contract_taxonomy_resolved_items.v0", "resolved": [{"source_path": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json", "target_path": "contracts/control_schemas/fixtures/archive/software/synthetic_resolution_fixture.json", "classification": "fixture_schema"}]},
            )
            errors: list[str] = []
            validator.validate_moved_paths(root, {"r0_contract_taxonomy_resolved_items": json.loads((root / "control/inventory/r0_contract_taxonomy_resolved_items.json").read_text())}, errors)
            self.assertTrue(any("source path still exists" in error for error in errors))

    def test_validator_fails_if_h14_task_named_preview_remains_under_contracts(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            errors: list[str] = []
            validator.validate_moved_paths(
                root,
                {
                    "r0_contract_taxonomy_resolved_items": {
                        "resolved": [
                            {
                                "source_path": "contracts/connectors/h14_source_need_candidate.v0.json",
                                "target_path": "contracts/control_schemas/previews/h14/connectors/source_need_candidate.v0.json",
                                "classification": "preview_schema",
                            }
                        ]
                    }
                },
                errors,
            )
            self.assertTrue(any("source path still exists" in error for error in errors))

    def test_validator_passes_clean_final_state(self) -> None:
        with self.make_repo() as temp, self.taxonomy_patch():
            root = Path(temp)
            result = resolver.resolve_taxonomy(root, apply_changes=True)
            write_json(
                root / "control/inventory/r0_03b_2_final_contract_taxonomy.json",
                {"unresolved_contract_count": 0, "compatibility_shim_count": 0},
            )
            inventories = {
                "r0_contract_taxonomy_remediation_result": result["remediation_result"],
                "r0_contract_taxonomy_final_state": result["final_state"],
                "r0_contract_taxonomy_resolved_items": result["resolved_items"],
                "r0_contract_taxonomy_reference_update_report": result["reference_update_report"],
            }
            errors: list[str] = []
            validator.validate_final_state(root, inventories, errors)
            validator.validate_moved_paths(root, inventories, errors)
            validator.validate_reference_report(root, inventories, errors)
            self.assertEqual(errors, [])

    def test_no_network_api_model_provider_calls(self) -> None:
        for path in ("scripts/resolve_contract_taxonomy_blockers.py", "scripts/validate_contract_taxonomy_remediation.py"):
            source = Path(path).read_text(encoding="utf-8")
            for token in ("requests", "httpx", "aiohttp", "openai", "anthropic"):
                self.assertNotIn(f"import {token}", source)
                self.assertNotIn(f"from {token}", source)


if __name__ == "__main__":
    unittest.main()
