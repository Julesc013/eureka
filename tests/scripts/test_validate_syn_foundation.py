from __future__ import annotations

from pathlib import Path
import unittest

from scripts.validate_syn_foundation import validate_syn_foundation


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateSynFoundationTests(unittest.TestCase):
    def test_validator_passes_repo_artifacts(self) -> None:
        report = validate_syn_foundation(REPO_ROOT)

        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertEqual(report["query_case_count"], 11)
        self.assertEqual(report["split_labels"], ["adversarial", "demo", "hard"])

    def test_stack_targets_cover_current_local_pipeline(self) -> None:
        report = validate_syn_foundation(REPO_ROOT)

        self.assertEqual(
            report["stack_targets"],
            ["HUNT", "IA_HUNT_BRIDGE", "IA_METADATA_PILOT", "LOCAL", "PLAY", "WORKBENCH_RESULT_LANES"],
        )


if __name__ == "__main__":
    unittest.main()
