from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "contracts" / "packs" / "pack_import_report.v0.json"
EXAMPLES_ROOT = REPO_ROOT / "examples" / "import_reports"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_REPORT_FORMAT.md"
PIPELINE_DOC = REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md"
PACK_VALIDATION_DOC = REPO_ROOT / "docs" / "operations" / "PACK_VALIDATION.md"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "pack-import-report-format-v0"


class PackImportReportFormatTestCase(unittest.TestCase):
    def test_schema_exists_and_parses(self) -> None:
        payload = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(payload["properties"]["schema_version"]["const"], "pack_import_report.v0")
        self.assertIn("pack_results", payload["required"])
        self.assertIn("mutation_summary", payload["required"])
        for field in [
            "import_performed",
            "staging_performed",
            "indexing_performed",
            "upload_performed",
            "master_index_mutation_performed",
            "runtime_mutation_performed",
            "network_performed",
        ]:
            self.assertEqual(payload["properties"][field]["const"], False)

    def test_example_reports_exist_and_parse(self) -> None:
        examples = sorted(EXAMPLES_ROOT.glob("*.json"))
        self.assertEqual(
            [example.name for example in examples],
            [
                "validate_only_all_examples.passed.json",
                "validate_only_private_path.failed.json",
                "validate_only_unknown_pack_type.failed.json",
            ],
        )
        for example in examples:
            with self.subTest(example=example.name):
                payload = json.loads(example.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema_version"], "pack_import_report.v0")
                self.assertEqual(payload["report_kind"], "pack_import_report")
                self.assertEqual(payload["mode"], "validate_only")
                self.assertFalse(payload["import_performed"])
                self.assertFalse(payload["staging_performed"])
                self.assertFalse(payload["indexing_performed"])
                self.assertFalse(payload["upload_performed"])
                self.assertFalse(payload["master_index_mutation_performed"])
                self.assertFalse(payload["runtime_mutation_performed"])
                self.assertFalse(payload["network_performed"])
                self.assertFalse(payload["mutation_summary"]["import_performed"])
                self.assertFalse(payload["mutation_summary"]["staging_performed"])
                self.assertFalse(payload["mutation_summary"]["indexing_performed"])
                self.assertFalse(payload["mutation_summary"]["upload_performed"])
                self.assertFalse(payload["mutation_summary"]["master_index_mutation_performed"])
                self.assertFalse(payload["mutation_summary"]["runtime_mutation_performed"])
                self.assertFalse(payload["mutation_summary"]["network_performed"])

    def test_passed_and_failed_examples_have_expected_statuses(self) -> None:
        passed = _load("validate_only_all_examples.passed.json")
        private_path = _load("validate_only_private_path.failed.json")
        unknown = _load("validate_only_unknown_pack_type.failed.json")

        self.assertEqual(passed["report_status"], "validate_only_passed")
        self.assertEqual(passed["validation_summary"]["passed"], 6)
        self.assertTrue(all(result["validation_status"] == "passed" for result in passed["pack_results"]))

        self.assertEqual(private_path["report_status"], "validate_only_failed")
        self.assertEqual(private_path["pack_results"][0]["privacy_status"], "failed")
        self.assertEqual(private_path["pack_results"][0]["risk_status"], "private_data_risk")
        self.assertEqual(private_path["pack_results"][0]["issues"][0]["issue_type"], "private_path_detected")
        self.assertIn("<redacted-local-path>", json.dumps(private_path))

        self.assertEqual(unknown["report_status"], "unsupported_pack_type")
        self.assertEqual(unknown["pack_results"][0]["pack_type"], "unknown")
        self.assertEqual(unknown["pack_results"][0]["validation_status"], "unknown_type")
        self.assertEqual(unknown["pack_results"][0]["recommended_next_action"], "unsupported")

    def test_examples_do_not_contain_secrets_or_positive_authority_claims(self) -> None:
        forbidden_fragments = [
            "api_key",
            "auth_token",
            "private_key",
            "password",
            "rights clearance approved",
            "rights clearance complete",
            "malware safety approved",
            "canonical truth established",
            "accepted as canonical truth",
        ]
        for example in EXAMPLES_ROOT.glob("*.json"):
            text = example.read_text(encoding="utf-8").lower()
            with self.subTest(example=example.name):
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, text)
                self.assertNotRegex(text, r"[a-z]:\\\\users\\\\")

    def test_docs_and_audit_pack_record_no_runtime_or_mutation(self) -> None:
        for path in [REFERENCE_DOC, PIPELINE_DOC, PACK_VALIDATION_DOC]:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("pack import report format v0", text)
                self.assertIn("does not implement import", text)
                self.assertIn("does not stage packs", text)
                self.assertIn("does not mutate local index", text)
                self.assertIn("does not upload", text)
                self.assertIn("does not mutate the master index", text)

        required_audit_files = {
            "README.md",
            "REPORT_FORMAT_SUMMARY.md",
            "STATUS_AND_MODE_MODEL.md",
            "PACK_RESULT_MODEL.md",
            "ISSUE_MODEL.md",
            "PRIVACY_RIGHTS_RISK_SUMMARY.md",
            "MUTATION_SAFETY_FIELDS.md",
            "EXAMPLE_REPORT_REVIEW.md",
            "FUTURE_VALIDATE_ONLY_TOOLING_PATH.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "pack_import_report_format_report.json",
        }
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(required_audit_files.issubset({path.name for path in AUDIT_ROOT.iterdir()}))
        audit_report = json.loads((AUDIT_ROOT / "pack_import_report_format_report.json").read_text(encoding="utf-8"))
        self.assertFalse(audit_report["import_runtime_implemented"])
        self.assertFalse(audit_report["staging_implemented"])
        self.assertFalse(audit_report["indexing_implemented"])
        self.assertFalse(audit_report["upload_implemented"])
        self.assertFalse(audit_report["master_index_mutation_implemented"])


def _load(name: str) -> dict:
    return json.loads((EXAMPLES_ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
