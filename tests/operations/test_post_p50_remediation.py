from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "post-p50-remediation-v0"
REPORT_PATH = AUDIT_ROOT / "post_p50_remediation_report.json"


class PostP50RemediationPackTestCase(unittest.TestCase):
    def test_audit_pack_files_exist(self) -> None:
        required = [
            "README.md",
            "REMEDIATION_SUMMARY.md",
            "P50_FINDINGS_REVIEW.md",
            "FIXED_ITEMS.md",
            "UNFIXED_OR_OPERATOR_GATED_ITEMS.md",
            "GOVERNANCE_DOCS_STATUS.md",
            "PACK_VALIDATOR_CLI_REMEDIATION.md",
            "GITHUB_PAGES_REMEDIATION_STATUS.md",
            "COMMAND_MATRIX_REMEDIATION.md",
            "TEST_REGISTRY_REMEDIATION.md",
            "GENERATED_ARTIFACT_RECHECK.md",
            "SECURITY_PRIVACY_RIGHTS_REMEDIATION.md",
            "CARGO_AND_RUST_STATUS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_BRANCH_RECOMMENDATION.md",
            "COMMAND_RESULTS.md",
            "post_p50_remediation_report.json",
        ]
        missing = [name for name in required if not (AUDIT_ROOT / name).exists()]
        self.assertEqual(missing, [])

    def test_report_records_required_status(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        item_ids = {item["item_id"] for item in report["remediation_items"]}
        self.assertIn("p51-pack-validator-cli-drift", item_ids)
        self.assertIn("p51-license-selection", item_ids)
        self.assertEqual(report["governance_docs_status"]["license"], "not_selected_no_root_license_added")
        self.assertFalse(report["github_pages_status"]["deployment_verified"])
        self.assertFalse(report["cargo_status"]["cargo_available"])
        self.assertEqual(report["pack_validator_cli_status"]["individual_all_examples"], "fixed")
        self.assertTrue(report["remaining_blockers"])
        self.assertTrue(report["next_milestones"])

    def test_no_product_expansion_claims(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in AUDIT_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".json"}
        )
        forbidden = [
            "github pages deployment succeeded",
            "hosted backend is implemented",
            "hosted public search is available",
            "ai runtime is implemented",
            "pack import runtime is implemented",
            "staging runtime is implemented",
            "production ready: true",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, text)

    def test_root_governance_docs_status(self) -> None:
        self.assertTrue((REPO_ROOT / "CONTRIBUTING.md").exists())
        self.assertTrue((REPO_ROOT / "SECURITY.md").exists())
        self.assertTrue((REPO_ROOT / "CODE_OF_CONDUCT.md").exists())
        self.assertFalse((REPO_ROOT / "LICENSE").exists())
        self.assertTrue((REPO_ROOT / "docs" / "operations" / "LICENSE_SELECTION_REQUIRED.md").exists())


if __name__ == "__main__":
    unittest.main()
