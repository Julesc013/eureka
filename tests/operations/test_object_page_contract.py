import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "object-page-contract-v0"
REPORT_PATH = AUDIT_DIR / "object_page_contract_report.json"
CONTRACT_PATH = ROOT / "contracts" / "pages" / "object_page.v0.json"
DOC_PATH = ROOT / "docs" / "reference" / "OBJECT_PAGE_CONTRACT.md"


class ObjectPageContractAuditTests(unittest.TestCase):
    def test_required_audit_files_exist(self) -> None:
        required = {
            "README.md",
            "CONTRACT_SUMMARY.md",
            "OBJECT_PAGE_SCHEMA.md",
            "OBJECT_IDENTITY_MODEL.md",
            "OBJECT_STATUS_AND_LANE_MODEL.md",
            "VERSION_STATE_RELEASE_MODEL.md",
            "REPRESENTATION_MODEL.md",
            "MEMBER_AND_CONTAINER_MODEL.md",
            "SOURCE_EVIDENCE_PROVENANCE_MODEL.md",
            "COMPATIBILITY_MODEL.md",
            "RIGHTS_RISK_ACTION_POSTURE_MODEL.md",
            "CONFLICT_AND_DUPLICATE_MODEL.md",
            "ABSENCE_NEAR_MISS_AND_GAP_MODEL.md",
            "RESULT_CARD_AND_SEARCH_PROJECTION.md",
            "API_PROJECTION.md",
            "STATIC_DEMO_PROJECTION.md",
            "PRIVACY_AND_REDACTION_POLICY.md",
            "NO_DOWNLOAD_INSTALL_EXECUTION_POLICY.md",
            "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
            "INTEGRATION_BOUNDARIES.md",
            "EXAMPLE_OBJECT_PAGE_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "object_page_contract_report.json",
        }
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required.issubset(present))

    def test_schema_and_examples_exist(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["x-status"], "contract_only")
        for rel in (
            "minimal_software_object_page_v0",
            "minimal_driver_object_page_v0",
            "minimal_container_member_object_page_v0",
            "minimal_conflicted_object_page_v0",
        ):
            self.assertTrue((ROOT / "examples" / "object_pages" / rel / "OBJECT_PAGE.json").is_file())

    def test_report_no_runtime_no_mutation(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "object_page_contract_v0")
        for key, value in report["no_runtime_no_mutation_guarantees"].items():
            self.assertFalse(value, key)
        self.assertEqual(report["next_recommended_branch"], "P80 Source Page Contract v0")

    def test_docs_state_contract_only_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8").casefold()
        for phrase in (
            "contract-only",
            "no runtime object pages",
            "no source cache mutation",
            "no evidence ledger mutation",
            "no candidate promotion",
            "not an app store",
            "not a downloader",
            "no rights clearance",
            "no malware safety",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
