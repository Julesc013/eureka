from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PRIORITIZER_PATH = (
    REPO_ROOT
    / "evals"
    / "hard_queries"
    / "artifact_evidence_gaps"
    / "batch_02"
    / "gap_prioritizer.json"
)
DASHBOARD_PATH = REPO_ROOT / "docs" / "reference" / "public_alpha_blocker_dashboard_00" / "blocker_dashboard.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ArtifactEvidenceGapPrioritizerBatchTwoTestCase(unittest.TestCase):
    def test_prioritizer_tracks_current_artifact_gate(self) -> None:
        payload = _load(PRIORITIZER_PATH)
        gate = payload["public_alpha_artifact_gate"]

        self.assertEqual(payload["schema_version"], "artifact_evidence_gap_prioritizer_batch_02.v0")
        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertEqual(gate["reviewed_artifact_record_count"], 4)
        self.assertEqual(gate["minimum_public_alpha_reviewed_artifact_records"], 25)
        self.assertEqual(gate["reviewed_artifact_record_gap"], 21)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_promotion_blocked"])

    def test_prioritized_targets_are_bounded_and_counted(self) -> None:
        payload = _load(PRIORITIZER_PATH)
        targets = payload["prioritized_targets"]
        ready = [target for target in targets if target["status"] == "collection_ready"]
        blocked = [target for target in targets if target["status"] == "blocked_for_user_details"]

        self.assertEqual(payload["counts"]["collection_ready_target_count"], len(ready))
        self.assertEqual(payload["counts"]["blocked_for_user_details_target_count"], len(blocked))
        self.assertEqual(len(ready), 6)
        self.assertEqual(len(blocked), 1)
        self.assertEqual([target["rank"] for target in targets], sorted(target["rank"] for target in targets))
        for target in targets:
            self.assertFalse(target["download_allowed"], target["target_id"])

    def test_prioritizer_contract_resumes_after_valid_return_only(self) -> None:
        payload = _load(PRIORITIZER_PATH)
        contract = payload["collection_contract"]

        self.assertEqual(contract["resume_after_valid_return"], "MANUAL-ARTIFACT-OBSERVATION-BATCH-03")
        self.assertIn("validate_artifact_evidence_return.py", contract["validator_command"])
        self.assertFalse(contract["ai_session_runtime_source_calls_allowed"])
        self.assertFalse(contract["downloads_allowed"])
        self.assertFalse(contract["executables_fetched_allowed"])
        self.assertFalse(contract["install_or_execution_allowed"])
        self.assertFalse(contract["rights_clearance_claim_allowed"])
        self.assertFalse(contract["malware_safety_claim_allowed"])

    def test_prioritizer_truth_boundary_remains_false(self) -> None:
        payload = _load(PRIORITIZER_PATH)

        for key, value in payload["truth_boundary"].items():
            self.assertFalse(value, key)

    def test_dashboard_matches_prioritizer_gate_counts(self) -> None:
        prioritizer = _load(PRIORITIZER_PATH)
        dashboard = _load(DASHBOARD_PATH)

        self.assertEqual(
            dashboard["gate_counts"]["reviewed_artifact_record_count"],
            prioritizer["public_alpha_artifact_gate"]["reviewed_artifact_record_count"],
        )
        self.assertEqual(
            dashboard["gate_counts"]["reviewed_artifact_record_gap"],
            prioritizer["public_alpha_artifact_gate"]["reviewed_artifact_record_gap"],
        )
        self.assertTrue(dashboard["public_alpha_blocked"])
        self.assertTrue(dashboard["dev_to_main_promotion_blocked"])

    def test_dashboard_lists_current_waiting_statuses_and_forbidden_actions(self) -> None:
        dashboard = _load(DASHBOARD_PATH)

        self.assertIn("WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE", dashboard["waiting_statuses"])
        self.assertIn("WAITING_FOR_USER_HARDWARE_DETAILS", dashboard["waiting_statuses"])
        self.assertIn("WAITING_FOR_EXTERNAL_FULL_DISCOVERY", dashboard["waiting_statuses"])
        self.assertIn("public_alpha_launch", dashboard["forbidden_actions_now"])
        self.assertIn("dev_to_main_promotion", dashboard["forbidden_actions_now"])
        self.assertIn("verified_artifact_claim", dashboard["forbidden_actions_now"])
        for key, value in dashboard["truth_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()

