from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "control" / "inventory" / "packs" / "example_packs.json"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "pack-import-validator-aggregator-v0"
REPORT = AUDIT_ROOT / "pack_validator_aggregator_report.json"
PACK_VALIDATION_DOC = REPO_ROOT / "docs" / "operations" / "PACK_VALIDATION.md"
IMPORT_PIPELINE_DOC = REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md"
IMPORT_PLANNING_DOC = REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_PLANNING.md"


class PackImportValidatorAggregatorTestCase(unittest.TestCase):
    def test_example_pack_registry_shape(self) -> None:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(payload["inventory_kind"], "eureka.example_pack_registry")
        examples = payload["examples"]
        self.assertEqual(len(examples), 5)
        self.assertEqual(
            {example["pack_type"] for example in examples},
            {"source_pack", "evidence_pack", "index_pack", "contribution_pack", "master_index_review_queue"},
        )
        for example in examples:
            self.assertTrue((REPO_ROOT / example["path"]).exists(), example["path"])
            self.assertEqual(example["expected_validation_status"], "pass")

    def test_audit_pack_and_report_record_current_results(self) -> None:
        required = [
            "README.md",
            "VALIDATOR_SUMMARY.md",
            "EXAMPLE_PACK_REGISTRY.md",
            "VALIDATION_RESULTS.md",
            "MUTATION_AND_SAFETY_REVIEW.md",
            "FUTURE_IMPORT_PIPELINE_IMPACT.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "pack_validator_aggregator_report.json",
        ]
        for name in required:
            self.assertTrue((AUDIT_ROOT / name).exists(), name)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_validation_reporting_only")
        self.assertEqual(report["current_validation"]["summary"]["passed"], 5)
        self.assertEqual(report["current_validation"]["summary"]["failed"], 0)
        self.assertFalse(report["mutation_performed"])
        self.assertFalse(report["import_performed"])
        self.assertFalse(report["staging_performed"])
        self.assertFalse(report["indexing_performed"])
        self.assertFalse(report["network_performed"])

    def test_docs_state_validate_only_boundaries(self) -> None:
        combined = (
            PACK_VALIDATION_DOC.read_text(encoding="utf-8")
            + "\n"
            + IMPORT_PIPELINE_DOC.read_text(encoding="utf-8")
            + "\n"
            + IMPORT_PLANNING_DOC.read_text(encoding="utf-8")
        ).lower()
        for phrase in [
            "pack import validator aggregator v0",
            "validate-only",
            "does not implement import",
            "does not stage",
            "does not mutate local indexes",
            "does not upload",
            "does not mutate the master index",
            "validation success is not import",
            "rights clearance",
            "malware safety",
        ]:
            self.assertIn(phrase, combined)

    def test_report_does_not_claim_truth_or_acceptance(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertFalse(report["rights_clearance_claimed"])
        self.assertFalse(report["malware_safety_claimed"])
        self.assertFalse(report["canonical_truth_claimed"])
        self.assertFalse(report["production_readiness_claimed"])
        notes = " ".join(report["notes"]).lower()
        self.assertIn("successful validation is not import", notes)
        self.assertIn("master-index acceptance", notes)


if __name__ == "__main__":
    unittest.main()
