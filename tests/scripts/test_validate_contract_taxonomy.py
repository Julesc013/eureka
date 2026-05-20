from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_contract_taxonomy.py"


class ContractTaxonomyValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("status: valid", completed.stdout)
        self.assertIn("error_count: 0", completed.stdout)

    def test_validator_json_passes_and_records_non_claims(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual("valid", payload["status"])
        self.assertEqual([], payload["errors"])
        self.assertFalse(payload["network_calls_made"])
        self.assertFalse(payload["model_provider_calls_made"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])

    def test_validator_rejects_runtime_as_contract_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_required_files(root)
            matrix_path = root / "control/inventory/contract_taxonomy_authority_matrix.json"
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            for family in matrix["families"]:
                if family["family_id"] == "runtime_contracts":
                    family["canonical_authority_path"] = "runtime/schema.py"
            matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(root), "--json"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("invalid", payload["status"])
        self.assertTrue(
            any("assigns product authority to runtime" in error for error in payload["errors"])
        )

    def test_validator_rejects_missing_duplicate_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_required_files(root)
            duplicate_path = root / "control/inventory/contract_taxonomy_duplicate_authority_report.json"
            duplicate = json.loads(duplicate_path.read_text(encoding="utf-8"))
            duplicate["duplicate_risks"] = [
                item
                for item in duplicate["duplicate_risks"]
                if item["risk_id"] != "contracts_runtime_vs_runtime_helpers"
            ]
            duplicate_path.write_text(json.dumps(duplicate, indent=2) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(root), "--json"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("invalid", payload["status"])
        self.assertTrue(any("duplicate authority report missing risks" in error for error in payload["errors"]))

    def test_validator_rejects_missing_testing_contract_family(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_required_files(root)
            matrix_path = root / "control/inventory/contract_taxonomy_authority_matrix.json"
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            matrix["families"] = [
                item for item in matrix["families"] if item["family_id"] != "testing_contracts"
            ]
            matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(root), "--json"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("invalid", payload["status"])
        self.assertTrue(any("testing_contracts" in error for error in payload["errors"]))

    def test_validator_rejects_testing_contract_as_example_or_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_required_files(root)
            matrix_path = root / "control/inventory/contract_taxonomy_authority_matrix.json"
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            for family in matrix["families"]:
                if family["family_id"] == "testing_contracts":
                    family["authority_class"] = "EXAMPLE_PAYLOAD"
            matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(root), "--json"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("invalid", payload["status"])
        self.assertTrue(any("testing_contracts must be PRODUCT_INTERNAL_CONTRACT" in error for error in payload["errors"]))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_required_files(root)
            matrix_path = root / "control/inventory/contract_taxonomy_authority_matrix.json"
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            for family in matrix["families"]:
                if family["family_id"] == "testing_contracts":
                    family["canonical_authority_path"] = "runtime/testing/"
            matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(root), "--json"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("invalid", payload["status"])
        self.assertTrue(any("runtime implementation authority" in error for error in payload["errors"]))

    def test_validator_rejects_missing_test_selection_result_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_required_files(root)
            (root / "contracts/testing/test_selection_result.v0.json").unlink()

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(root), "--json"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("invalid", payload["status"])
        self.assertTrue(any("test_selection_result.v0.json" in error for error in payload["errors"]))


def copy_required_files(root: Path) -> None:
    json_files = [
        "control/inventory/contract_taxonomy_input_state.json",
        "control/inventory/contract_taxonomy_root_inventory.json",
        "control/inventory/contract_taxonomy_authority_matrix.json",
        "control/inventory/contract_taxonomy_duplicate_authority_report.json",
        "control/inventory/contract_taxonomy_control_schemas_decision.json",
        "control/inventory/contract_taxonomy_migration_backlog.json",
        "control/inventory/contract_taxonomy_validator_matrix.json",
        "control/inventory/contract_taxonomy_result.json",
        "control/inventory/contract_taxonomy_next_task_decision.json",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/contract_taxonomy_report.json",
        "control/inventory/test_lane_router_result.json",
        "contracts/testing/test_selection_result.v0.json",
    ]
    markdown_files = [
        "docs/architecture/CONTRACT_TAXONOMY.md",
        "docs/operations/CONTRACT_TAXONOMY_CLEANUP_PLAN.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/README.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/root_inventory.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/authority_matrix.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/duplicate_authority_report.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/control_schemas_decision.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/migration_backlog.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/validation.md",
        "control/audits/repo-layout-contract-taxonomy-cleanup-v0/generated/sample_summary.md",
    ]

    for rel in json_files + markdown_files:
        source = REPO_ROOT / rel
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
