from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.artifact_observations.batch_00 import BASELINE_PROFILES, FORBIDDEN_PUBLIC_ACTIONS
from evals.hard_queries.reviewed_artifact_records.batch_00 import (
    load_non_promoted_artifact_leads,
    load_reviewed_artifact_records,
    non_promoted_lead_records,
    project_non_promoted_artifact_lead,
    project_reviewed_artifact_record,
    reviewed_artifact_record_records,
)


class SurfaceArtifactReviewProjectionTests(unittest.TestCase):
    def test_reviewed_artifact_records_project_as_reviewed_not_verified_artifacts(self) -> None:
        for record in reviewed_artifact_record_records(load_reviewed_artifact_records()):
            for profile in BASELINE_PROFILES:
                with self.subTest(record=record["reviewed_artifact_record_id"], profile=profile):
                    result = project_reviewed_artifact_record(record, profile)
                    payload = result["view_model"]["payload"]

                    self.assertEqual(result["view_model"]["canonical_status"], "verified")
                    self.assertEqual(payload["artifact_claim_status"], "reviewed_artifact_record")
                    self.assertFalse(payload["verified_artifact"])
                    self.assertIn("reviewed artifact record", result["view_model"]["title"].lower())
                    self.assertEqual(
                        [action["action_id"] for action in result["view_model"]["actions"]],
                        ["view", "inspect_evidence", "cite"],
                    )

    def test_non_promoted_artifact_leads_project_as_non_truth_states(self) -> None:
        for lead in non_promoted_lead_records(load_non_promoted_artifact_leads()):
            for profile in BASELINE_PROFILES:
                with self.subTest(lead=lead["artifact_observation_id"], profile=profile):
                    result = project_non_promoted_artifact_lead(lead, profile)
                    payload = result["view_model"]["payload"]

                    self.assertIn(result["view_model"]["canonical_status"], {"need", "near_miss", "unavailable"})
                    self.assertEqual(payload["artifact_claim_status"], "artifact_lead")
                    self.assertFalse(payload["verified_artifact"])

    def test_public_projection_strips_operator_only_actions(self) -> None:
        action_ids = []
        for record in reviewed_artifact_record_records(load_reviewed_artifact_records()):
            for profile in BASELINE_PROFILES:
                action_ids.extend(
                    action["action_id"]
                    for action in project_reviewed_artifact_record(record, profile)["view_model"]["actions"]
                )
        for lead in non_promoted_lead_records(load_non_promoted_artifact_leads()):
            for profile in BASELINE_PROFILES:
                action_ids.extend(
                    action["action_id"]
                    for action in project_non_promoted_artifact_lead(lead, profile)["view_model"]["actions"]
                )

        for action in FORBIDDEN_PUBLIC_ACTIONS:
            self.assertNotIn(action, action_ids)

    def test_html_renderer_escapes_reviewed_record_text(self) -> None:
        record = deepcopy(reviewed_artifact_record_records(load_reviewed_artifact_records())[0])
        record["artifact_identity"]["name"] = "Firefox <ESR>"
        record["artifact_identity"]["version"] = "\"115\""

        html = project_reviewed_artifact_record(record, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;ESR&gt;", html)
        self.assertIn("&quot;115&quot;", html)
        self.assertNotIn("<ESR>", html)
        self.assertNotIn('"115"', html)

    def test_snapshot_output_is_deterministic(self) -> None:
        record = reviewed_artifact_record_records(load_reviewed_artifact_records())[0]

        first = project_reviewed_artifact_record(record, "snapshot_v0")["renderer_result"]["renderer_output"]
        second = project_reviewed_artifact_record(record, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first, second)
        self.assertEqual(first["content"]["canonical_status"], "verified")

    def test_unknown_non_promoted_status_degrades_honestly(self) -> None:
        lead = deepcopy(non_promoted_lead_records(load_non_promoted_artifact_leads())[0])
        lead["status"] = "impossible_status"

        result = project_non_promoted_artifact_lead(lead, "json_v0")

        self.assertEqual(result["view_model"]["canonical_status"], "unknown")

    def test_projection_does_not_call_sources_or_mutate_indexes(self) -> None:
        samples = [
            *(project_reviewed_artifact_record(record, profile) for record in reviewed_artifact_record_records(load_reviewed_artifact_records()) for profile in BASELINE_PROFILES),
            *(project_non_promoted_artifact_lead(lead, profile) for lead in non_promoted_lead_records(load_non_promoted_artifact_leads()) for profile in BASELINE_PROFILES),
        ]

        for result in samples:
            renderer = result["renderer_result"]
            self.assertFalse(result["surface_kernel_called_source_provider"])
            self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
            self.assertFalse(result["surface_kernel_mutated_public_index"])
            self.assertFalse(result["surface_kernel_mutated_master_index"])
            self.assertFalse(renderer["renderer_called_source_provider"])
            self.assertFalse(renderer["renderer_created_verified_state"])
            self.assertFalse(renderer["renderer_mutated_reviewed_index"])
            self.assertFalse(renderer["renderer_mutated_public_index"])
            self.assertFalse(renderer["renderer_mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
