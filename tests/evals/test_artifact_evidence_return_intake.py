from __future__ import annotations

from pathlib import Path
import unittest

from scripts.validate_artifact_evidence_return import validate_return_file


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_ROOT = REPO_ROOT / "evals" / "hard_queries" / "artifact_evidence_returns" / "examples"


class ArtifactEvidenceReturnIntakeTestCase(unittest.TestCase):
    def test_valid_minimal_return_becomes_reviewable_input_only(self) -> None:
        report = validate_return_file(EXAMPLES_ROOT / "valid_minimal_return" / "artifact_evidence_collection_summary.json", strict=True)
        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertEqual(report["target_result_count"], 2)
        self.assertEqual(report["resume_recommended_task"], "MANUAL-ARTIFACT-OBSERVATION-BATCH-03")
        self.assertFalse(report["truth_created"])
        self.assertFalse(report["network_performed"])
        self.assertFalse(report["mutation_performed"])

    def test_invalid_verified_claim_is_rejected(self) -> None:
        report = validate_return_file(EXAMPLES_ROOT / "invalid_verified_claim" / "artifact_evidence_collection_summary.json")
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("verified_artifact_created" in error for error in report["errors"]))
        self.assertFalse(report["truth_created"])

    def test_driver_without_hardware_identity_is_rejected(self) -> None:
        report = validate_return_file(EXAMPLES_ROOT / "invalid_driver_missing_hardware" / "artifact_evidence_collection_summary.json")
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("lacks hardware identity" in error for error in report["errors"]))

    def test_fixture_directory_is_not_external_evidence(self) -> None:
        readme = (REPO_ROOT / "evals" / "hard_queries" / "artifact_evidence_returns" / "README.md").read_text(encoding="utf-8")
        self.assertIn("not external evidence", readme)
        self.assertIn("must not directly create", readme)


if __name__ == "__main__":
    unittest.main()
