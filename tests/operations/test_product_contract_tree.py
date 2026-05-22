import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts import validate_product_contract_tree as validator


def contract(path: str, contract_class: str) -> dict:
    return {"path": path, "contract_class": contract_class, "signals": [], "recommended_action": "keep"}


def write_reference_result(root: Path) -> None:
    path = root / "control/inventory/r0_03b_2_reference_update_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "r0_03b_2_reference_update_result.v0",
                "task": "R0-03B-2",
                "f0_should_remain_blocked": True,
                "dev_to_main_should_remain_blocked": True,
                "blocked_moves": [],
                "moved_in_this_task": [],
                "updates_completed": 0,
                "updates_blocked": 0,
            }
        ),
        encoding="utf-8",
    )


class ProductContractTreeTests(unittest.TestCase):
    def validate_with_contracts(self, contracts: list[dict], root: Path | None = None) -> dict:
        if root is None:
            temp = tempfile.TemporaryDirectory()
            self.addCleanup(temp.cleanup)
            root = Path(temp.name)
        write_reference_result(root)
        with mock.patch.object(
            validator,
            "load_contract_taxonomy",
            return_value={"contract_taxonomy_inventory": {"contracts": contracts}},
        ), mock.patch.object(validator, "validate_no_forbidden_paths_modified"), mock.patch.object(
            validator, "validate_static_only"
        ), mock.patch.object(
            validator, "validate_moved_schema_targets"
        ):
            return validator.validate_contract_tree(root)

    def test_product_contract_validator_passes_clean_product_contract_fixture(self) -> None:
        result = self.validate_with_contracts([contract("contracts/domain/source_record.v0.json", "product_domain_contract")])
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["product_contract_cleanup_result"]["product_contract_count"], 1)

    def test_product_contract_validator_fails_audit_schema_under_contracts_fixture(self) -> None:
        result = self.validate_with_contracts([contract("contracts/audits/report.v0.json", "audit_schema")])
        self.assertEqual(result["status"], "invalid")
        self.assertIn("clear non-product schema remains", result["errors"][0])

    def test_product_contract_validator_fails_fixture_schema_under_contracts_fixture(self) -> None:
        result = self.validate_with_contracts([contract("contracts/archive/fixtures/demo.json", "fixture_schema")])
        self.assertEqual(result["status"], "invalid")

    def test_product_contract_validator_fails_task_phase_named_product_contract_fixture(self) -> None:
        result = self.validate_with_contracts(
            [contract("contracts/connectors/h14_source_record.v0.json", "connector_interface_contract")]
        )
        self.assertEqual(result["status"], "valid_with_warnings")
        self.assertEqual(result["product_contract_cleanup_result"]["task_named_contract_count"], 1)

    def test_product_contract_validator_reports_unknown_schema(self) -> None:
        result = self.validate_with_contracts([contract("contracts/archive/unknown.bundle", "unknown")])
        self.assertEqual(result["status"], "valid_with_warnings")
        self.assertEqual(result["product_contract_cleanup_result"]["unknown_contract_count"], 1)
        self.assertEqual(result["final_contract_taxonomy"]["unresolved_contract_count"], 1)

    def test_product_contract_validator_detects_deleted_moved_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_reference_result(root)
            (root / "control/inventory/r0_03b_1_migration_result.json").write_text(
                json.dumps({"moved": [{"source_path": "contracts/a.v0.json", "target_path": "contracts/control_schemas/a.v0.json"}]}),
                encoding="utf-8",
            )
            with mock.patch.object(
                validator,
                "load_contract_taxonomy",
                return_value={"contract_taxonomy_inventory": {"contracts": []}},
            ), mock.patch.object(validator, "validate_no_forbidden_paths_modified"), mock.patch.object(
                validator, "validate_static_only"
            ):
                result = validator.validate_contract_tree(root)
            self.assertEqual(result["status"], "invalid")
            self.assertIn("moved schema target is missing", "\n".join(result["errors"]))

    def test_product_contract_validator_detects_runtime_file_modification(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            errors: list[str] = []
            fake = SimpleNamespace(returncode=0, stdout=" M runtime/example.py\n", stderr="")
            with mock.patch.object(validator.subprocess, "run", return_value=fake):
                validator.validate_no_forbidden_paths_modified(root, errors)
            self.assertIn("forbidden product path modified: runtime/example.py", errors)

    def test_r0_03b_2_blockers_remain_set(self) -> None:
        result = self.validate_with_contracts([])
        self.assertTrue(result["f0_should_remain_blocked"])
        self.assertTrue(result["dev_to_main_should_remain_blocked"])

    def test_no_network_api_model_provider_imports(self) -> None:
        source = Path("scripts/validate_product_contract_tree.py").read_text(encoding="utf-8")
        forbidden = ("requests", "httpx", "openai", "anthropic")
        for token in forbidden:
            self.assertNotIn(f"import {token}", source)
            self.assertNotIn(f"from {token}", source)


if __name__ == "__main__":
    unittest.main()
