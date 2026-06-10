from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.artifact_evidence_gaps.batch_00 import (
    BASELINE_PROFILES,
    FORBIDDEN_PUBLIC_ACTIONS,
    blocked_gap_fixture,
    evidence_gap_records,
    load_evidence_gap_triage,
    load_renderer_expected_outputs,
    load_surface_projection_fixtures,
    load_verification_gap_triage,
    project_gap_item,
    validate_renderer_expected_outputs,
    validate_surface_projection_fixtures,
    verification_gap_records,
)


class SurfaceArtifactEvidenceGapProjectionTests(unittest.TestCase):
    def test_surface_and_renderer_fixtures_validate(self) -> None:
        self.assertEqual(validate_surface_projection_fixtures(load_surface_projection_fixtures()), ())
        self.assertEqual(validate_renderer_expected_outputs(load_renderer_expected_outputs()), ())

    def test_gap_items_project_as_needs_without_verified_artifact_claims(self) -> None:
        items = [
            *evidence_gap_records(load_evidence_gap_triage()),
            *verification_gap_records(load_verification_gap_triage()),
            blocked_gap_fixture(),
        ]

        for item in items:
            for profile in BASELINE_PROFILES:
                with self.subTest(gap=item["gap_id"], profile=profile):
                    result = project_gap_item(item, profile)
                    payload = result["view_model"]["payload"]

                    self.assertEqual(result["view_model"]["canonical_status"], "need")
                    self.assertFalse(payload["verified_artifact"])
                    self.assertFalse(payload["runtime_source_call_allowed"])
                    self.assertFalse(payload["download_allowed"])

    def test_public_projection_strips_operator_actions(self) -> None:
        item = evidence_gap_records(load_evidence_gap_triage())[0]

        for profile in BASELINE_PROFILES:
            actions = [action["action_id"] for action in project_gap_item(item, profile)["view_model"]["actions"]]
            for forbidden in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(forbidden, actions)

    def test_html_renderer_escapes_gap_text(self) -> None:
        item = deepcopy(evidence_gap_records(load_evidence_gap_triage())[0])
        item["collection_target"] = "7-Zip <package> \"identity\""

        html = project_gap_item(item, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;package&gt;", html)
        self.assertIn("&quot;identity&quot;", html)
        self.assertNotIn("<package>", html)
        self.assertNotIn('"identity"', html)

    def test_snapshot_output_is_deterministic(self) -> None:
        item = evidence_gap_records(load_evidence_gap_triage())[0]

        first = project_gap_item(item, "snapshot_v0")["renderer_result"]["renderer_output"]
        second = project_gap_item(item, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first, second)
        self.assertEqual(first["content"]["canonical_status"], "need")

    def test_projection_does_not_call_sources_or_mutate_indexes(self) -> None:
        item = evidence_gap_records(load_evidence_gap_triage())[0]

        for profile in BASELINE_PROFILES:
            result = project_gap_item(item, profile)
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

