from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class ContractTaxonomyOperationsTest(unittest.TestCase):
    def test_docs_define_authority_classes(self) -> None:
        doc = (REPO_ROOT / "docs" / "architecture" / "CONTRACT_TAXONOMY.md").read_text(
            encoding="utf-8"
        )

        for term in [
            "PRODUCT_PUBLIC_CONTRACT",
            "PRODUCT_INTERNAL_CONTRACT",
            "CONTROL_SCHEMA",
            "POLICY_DOCUMENT",
            "INVENTORY_RECORD",
            "AUDIT_SCHEMA_OR_REPORT",
            "FIXTURE_SCHEMA",
            "EXAMPLE_PAYLOAD",
            "GENERATED_ARTIFACT",
            "DEPRECATED_OR_QUARANTINE",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, doc)

    def test_required_families_are_inventoried(self) -> None:
        matrix = load_json("control/inventory/contract_taxonomy_authority_matrix.json")
        families = {item["family_id"]: item for item in matrix["families"]}

        for family_id in [
            "repo_layout_contracts",
            "source_registry_contracts",
            "source_record_contracts",
            "source_cache_contracts",
            "evidence_ledger_contracts",
            "candidate_index_contracts",
            "review_queue_contracts",
            "reviewed_index_contracts",
            "pack_contracts",
            "contribution_contracts",
            "archive_product_contracts",
            "runtime_contracts",
            "control_policy_schemas",
            "control_inventory_schemas",
            "generated_artifact_contracts",
            "testing_contracts",
            "IA_metadata_pilot_contracts",
            "Workbench_future_view_models",
            "Search_Interaction_future_packets",
        ]:
            with self.subTest(family_id=family_id):
                self.assertIn(family_id, families)

    def test_duplicate_risks_and_control_schema_decision_are_recorded(self) -> None:
        duplicate = load_json("control/inventory/contract_taxonomy_duplicate_authority_report.json")
        risks = {item["risk_id"]: item for item in duplicate["duplicate_risks"]}

        for risk_id in [
            "control_schemas_policies_packs_vs_contracts_packs",
            "contracts_source_registry_vs_contracts_sources",
            "contracts_source_cache_vs_contracts_stores",
            "contracts_runtime_vs_runtime_helpers",
            "contracts_archive_vs_archive_root",
            "control_inventory_schemas_vs_contracts_repo",
        ]:
            with self.subTest(risk_id=risk_id):
                self.assertIn(risk_id, risks)
                self.assertFalse(risks[risk_id]["blocks_workbench_foundation"])

        decision = load_json("control/inventory/contract_taxonomy_control_schemas_decision.json")
        self.assertEqual(
            "retain_as_control_schema_authority_with_migration_backlog",
            decision["decision"],
        )
        self.assertTrue(decision["control_schemas_allowed_now"])
        self.assertFalse(decision["product_contracts_allowed_under_control_schemas"])

    def test_examples_and_runtime_do_not_own_contract_authority(self) -> None:
        inventory = load_json("control/inventory/contract_taxonomy_root_inventory.json")
        roots = {item["path"]: item for item in inventory["roots"]}

        self.assertEqual("EXAMPLE_PAYLOAD", roots["examples"]["authority_class"])
        self.assertEqual("NOT_CONTRACT_AUTHORITY", roots["runtime"]["authority_class"])
        self.assertEqual("NOT_CONTRACT_AUTHORITY", roots["scripts"]["authority_class"])

    def test_testing_contracts_are_product_internal_contracts(self) -> None:
        matrix = load_json("control/inventory/contract_taxonomy_authority_matrix.json")
        families = {item["family_id"]: item for item in matrix["families"]}
        testing = families["testing_contracts"]

        self.assertEqual("PRODUCT_INTERNAL_CONTRACT", testing["authority_class"])
        self.assertEqual("contracts/testing/", testing["canonical_authority_path"])
        self.assertIn("contracts/testing/**", testing["current_paths"])
        self.assertFalse(testing["duplicate_authority_risk"])
        self.assertFalse(testing["migration_required"])

        inventory = load_json("control/inventory/contract_taxonomy_root_inventory.json")
        roots = {item["path"]: item for item in inventory["roots"]}
        self.assertEqual("PRODUCT_INTERNAL_CONTRACT", roots["contracts/testing"]["authority_class"])
        self.assertNotEqual("EXAMPLE_PAYLOAD", roots["contracts/testing"]["authority_class"])
        self.assertNotEqual("NOT_CONTRACT_AUTHORITY", roots["contracts/testing"]["authority_class"])
        self.assertTrue((REPO_ROOT / "contracts/testing/test_selection_result.v0.json").is_file())

    def test_future_contract_locations_are_reserved(self) -> None:
        matrix = load_json("control/inventory/contract_taxonomy_authority_matrix.json")
        families = {item["family_id"]: item for item in matrix["families"]}

        self.assertEqual(
            "contracts/view/pages/workbench/",
            families["Workbench_future_view_models"]["canonical_authority_path"],
        )
        self.assertEqual(
            "contracts/search/interaction/",
            families["Search_Interaction_future_packets"]["canonical_authority_path"],
        )

    def test_result_records_no_moves_or_runtime_changes(self) -> None:
        result = load_json("control/inventory/contract_taxonomy_result.json")

        self.assertEqual("pass", result["status"])
        self.assertFalse(result["large_file_moves_performed"])
        self.assertFalse(result["files_deleted"])
        self.assertFalse(result["runtime_behavior_changed"])
        self.assertTrue(result["product_contracts_assigned_to_contracts_root"])
        self.assertTrue(result["control_schemas_scope_limited_to_control"])
        self.assertEqual(0, result["hard_blockers_remaining"])
        self.assertEqual(0, result["warnings_remaining"])


if __name__ == "__main__":
    unittest.main()
