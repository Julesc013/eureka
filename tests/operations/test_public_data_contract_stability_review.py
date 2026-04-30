from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-data-contract-stability-review-v0"
REPORT = AUDIT_DIR / "public_data_stability_report.json"
PUBLIC_DATA = REPO_ROOT / "site/dist" / "data"
PUBLIC_DATA_CONTRACT = (
    REPO_ROOT / "control" / "inventory" / "publication" / "public_data_contract.json"
)
POLICY_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_DATA_STABILITY_POLICY.md"


class PublicDataContractStabilityReviewTest(unittest.TestCase):
    def load_report(self) -> dict:
        return json.loads(REPORT.read_text(encoding="utf-8"))

    def test_review_pack_exists(self) -> None:
        required = {
            "README.md",
            "CURRENT_PUBLIC_DATA.md",
            "FIELD_STABILITY_MATRIX.md",
            "FILE_STABILITY_DECISIONS.md",
            "VERSIONING_POLICY.md",
            "BREAKING_CHANGE_POLICY.md",
            "CLIENT_CONSUMPTION_GUIDANCE.md",
            "SNAPSHOT_NATIVE_RELAY_IMPACT.md",
            "RISKS.md",
            "NEXT_GUARDS.md",
            "public_data_stability_report.json",
        }
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((AUDIT_DIR / name).exists())

    def test_report_covers_all_public_data_json_files(self) -> None:
        report = self.load_report()
        covered = {entry["file_name"] for entry in report["public_data_files"]}
        current = {path.name for path in PUBLIC_DATA.glob("*.json")}
        self.assertEqual(covered, current)

    def test_stability_classes_are_present(self) -> None:
        report = self.load_report()
        self.assertTrue(
            {
                "stable_draft",
                "experimental",
                "volatile",
                "internal",
                "deprecated",
                "future",
            }.issubset(report["stability_classes"])
        )

    def test_no_file_marked_production_stable(self) -> None:
        report = self.load_report()
        for entry in report["public_data_files"]:
            with self.subTest(file_name=entry["file_name"]):
                self.assertNotIn(
                    entry["stability_class"],
                    {"stable", "production_stable", "production_ready"},
                )

    def test_source_id_is_stable_draft_when_source_summary_exists(self) -> None:
        report = self.load_report()
        fields = {
            (entry["file_name"], entry["field_path"])
            for entry in report["stable_draft_fields"]
        }
        self.assertTrue((PUBLIC_DATA / "source_summary.json").exists())
        self.assertIn(("source_summary.json", "sources[].source_id"), fields)

    def test_build_commit_and_built_at_are_not_stable(self) -> None:
        report = self.load_report()
        field_entries = report["field_stability"]["build_manifest.json"]
        by_field = {entry["field_path"]: entry["stability"] for entry in field_entries}
        self.assertEqual(by_field["commit"], "volatile")
        self.assertEqual(by_field["built_at"], "volatile")

    def test_policy_doc_mentions_no_production_api_guarantee(self) -> None:
        text = POLICY_DOC.read_text(encoding="utf-8").lower()
        self.assertIn("does not make public json a production api", text)
        self.assertIn("no current public json file is production-stable", text)

    def test_public_data_contract_references_stability_review(self) -> None:
        contract = json.loads(PUBLIC_DATA_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["stability_policy"],
            "docs/reference/PUBLIC_DATA_STABILITY_POLICY.md",
        )
        self.assertEqual(contract["client_consumption_status"], "field_level_stable_draft_only")
        self.assertIn("field_stability_summary", contract)


if __name__ == "__main__":
    unittest.main()
