from __future__ import annotations

import json
from pathlib import Path
import tomllib
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPO_ROOT / "contracts" / "repo"


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


class RepoStructureCanonContractTest(unittest.TestCase):
    def test_required_contracts_exist(self) -> None:
        required = [
            "root_allowlist.contract.toml",
            "naming.contract.toml",
            "generated_artifact_exceptions.contract.toml",
            "root_ownership.contract.toml",
        ]

        for name in required:
            with self.subTest(name=name):
                self.assertTrue((CONTRACT_ROOT / name).is_file())

    def test_root_allowlist_preserves_corrected_native_rule(self) -> None:
        allowlist = _load_toml(CONTRACT_ROOT / "root_allowlist.contract.toml")
        roots = {item["name"]: item for item in allowlist["roots"]}

        expected_roots = {
            ".aide",
            ".github",
            "control",
            "contracts",
            "runtime",
            "surfaces",
            "native",
            "crates",
            "site",
            "snapshots",
            "examples",
            "docs",
            "tests",
            "evals",
            "tools",
            "scripts",
            "release",
            "external",
            "archive",
        }

        self.assertEqual(expected_roots, set(roots))
        self.assertEqual(roots["native"]["class"], "native_client_project")
        self.assertFalse(roots["tools"]["required"])
        self.assertFalse(roots["release"]["required"])
        self.assertFalse(roots["archive"]["required"])
        self.assertIn("native_project_authority", roots["surfaces"]["must_not_own"])

    def test_ownership_contract_keeps_native_above_surfaces_native(self) -> None:
        ownership = _load_toml(CONTRACT_ROOT / "root_ownership.contract.toml")
        by_root = {item["root"]: item for item in ownership["ownership"]}

        self.assertIn("native_client_projects", by_root["native"]["owns"])
        self.assertIn("native_project_authority", by_root["surfaces"]["must_not_own"])
        self.assertIn("surfaces/web/workbench", by_root["surfaces"]["notes"])
        self.assertIn("Top-level native/", by_root["native"]["notes"])

    def test_generated_artifact_exceptions_have_no_manual_edit_policy(self) -> None:
        contract = _load_toml(CONTRACT_ROOT / "generated_artifact_exceptions.contract.toml")
        exact = {item["path"]: item for item in contract["exceptions"]}

        for path in [
            "site/dist",
            "snapshots/examples/static_snapshot_v0",
            "site/dist/data/public_index",
            ".aide/generated",
            ".aide/cache",
            ".aide/export",
            ".aide/reports",
        ]:
            with self.subTest(path=path):
                self.assertIn(path, exact)
                self.assertFalse(exact[path]["manual_edits_allowed"])
                self.assertTrue(exact[path]["check_command"])

        self.assertEqual(exact["site/dist/data/public_index"]["status"], "accepted_exception")

    def test_inventory_records_reconciled_debt(self) -> None:
        result = json.loads(
            (REPO_ROOT / "control" / "inventory" / "repo_layout_canon_result.json").read_text(
                encoding="utf-8"
            )
        )
        next_task = json.loads(
            (REPO_ROOT / "control" / "inventory" / "repo_layout_next_task_decision.json").read_text(
                encoding="utf-8"
            )
        )
        known_debt = json.loads(
            (REPO_ROOT / "control" / "inventory" / "repo_layout_known_debt.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(result["next_task"], "REPO-LAYOUT-INVENTORY-02")
        self.assertFalse(result["files_moved"])
        self.assertFalse(result["runtime_behavior_changed"])
        self.assertEqual(next_task["decision"], "REPO-LAYOUT-INVENTORY-02")
        self.assertEqual(known_debt["status"], "resolved_by_structure_reconcile")
        self.assertEqual(known_debt["known_debt"], [])
        self.assertTrue(known_debt["resolved_debt"])
        self.assertTrue(known_debt["no_runtime_behavior_change"])

        audit_root = REPO_ROOT / "control" / "audits" / "repo-layout-canon-01-v0"
        for name in [
            "README.md",
            "repo_layout_canon_report.json",
            "root_inventory.md",
            "known_debt.md",
            "validation.md",
        ]:
            with self.subTest(name=name):
                self.assertTrue((audit_root / name).is_file())

    def test_docs_state_no_product_claim(self) -> None:
        canon_doc = (REPO_ROOT / "docs" / "architecture" / "REPOSITORY_LAYOUT_CANON.md").read_text(
            encoding="utf-8"
        )
        migration_doc = (
            REPO_ROOT / "docs" / "operations" / "REPOSITORY_LAYOUT_MIGRATION_PLAN.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Do not absorb top-level `native/`", canon_doc)
        self.assertIn("EUREKA-STRUCTURE-BIG-BANG-01 reconciled the recorded layout debt", canon_doc)
        self.assertIn("does not claim production readiness", canon_doc)
        self.assertIn("superseded by `EUREKA-STRUCTURE-BIG-BANG-01`", migration_doc)


if __name__ == "__main__":
    unittest.main()
