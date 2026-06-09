from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.reviewed_artifact_corpus.batch_01 import (
    BASELINE_PROFILES,
    FORBIDDEN_PUBLIC_ACTIONS,
    artifact_decision_outcome_records,
    blocked_for_user_details_fixture,
    load_artifact_decision_backed_outcomes,
    load_renderer_expected_outputs,
    load_reviewed_artifact_records,
    load_surface_projection_fixtures,
    project_artifact_corpus_item,
    reviewed_artifact_record_records,
    validate_renderer_expected_outputs,
    validate_surface_projection_fixtures,
)


class SurfaceReviewedArtifactCorpusProjectionTests(unittest.TestCase):
    def test_surface_and_renderer_fixtures_validate(self) -> None:
        self.assertEqual(validate_surface_projection_fixtures(load_surface_projection_fixtures()), ())
        self.assertEqual(validate_renderer_expected_outputs(load_renderer_expected_outputs()), ())

    def test_reviewed_artifact_records_project_with_truth_limits(self) -> None:
        for record in reviewed_artifact_record_records(load_reviewed_artifact_records()):
            for profile in BASELINE_PROFILES:
                with self.subTest(record=record["artifact_record_id"], profile=profile):
                    result = project_artifact_corpus_item(record, profile)
                    payload = result["view_model"]["payload"]

                    self.assertEqual(result["view_model"]["canonical_status"], "verified")
                    self.assertEqual(payload["artifact_claim_status"], "reviewed_artifact_record")
                    self.assertFalse(payload["verified_artifact"])
                    self.assertEqual(
                        [action["action_id"] for action in result["view_model"]["actions"]],
                        ["view", "inspect_evidence", "cite"],
                    )

    def test_non_promoted_outcomes_project_as_non_truth_states(self) -> None:
        outcomes = [
            item
            for item in artifact_decision_outcome_records(load_artifact_decision_backed_outcomes())
            if item["decision"] != "promote"
        ]

        for outcome in outcomes:
            for profile in BASELINE_PROFILES:
                with self.subTest(outcome=outcome["outcome_id"], profile=profile):
                    result = project_artifact_corpus_item(outcome, profile)
                    payload = result["view_model"]["payload"]

                    self.assertIn(result["view_model"]["canonical_status"], {"need", "near_miss", "unavailable"})
                    self.assertNotEqual(payload["artifact_claim_status"], "reviewed_artifact_record")
                    self.assertFalse(payload["verified_artifact"])

    def test_blocked_driver_projects_as_need(self) -> None:
        item = blocked_for_user_details_fixture()
        result = project_artifact_corpus_item(item, "text_v0")
        text = result["renderer_result"]["renderer_output"]["content"]

        self.assertEqual(result["view_model"]["canonical_status"], "need")
        self.assertIn("Windows 98 driver query blocked", text)
        self.assertIn("hardware", text)
        self.assertFalse(result["view_model"]["payload"]["verified_artifact"])

    def test_public_projection_strips_operator_actions(self) -> None:
        samples = [
            *reviewed_artifact_record_records(load_reviewed_artifact_records()),
            *artifact_decision_outcome_records(load_artifact_decision_backed_outcomes()),
            blocked_for_user_details_fixture(),
        ]

        for item in samples:
            for profile in BASELINE_PROFILES:
                actions = [
                    action["action_id"]
                    for action in project_artifact_corpus_item(item, profile)["view_model"]["actions"]
                ]
                for forbidden in FORBIDDEN_PUBLIC_ACTIONS:
                    self.assertNotIn(forbidden, actions)

    def test_html_renderer_escapes_corpus_text(self) -> None:
        record = deepcopy(reviewed_artifact_record_records(load_reviewed_artifact_records())[0])
        record["title"] = "Firefox <ESR> \"115\""

        html = project_artifact_corpus_item(record, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;ESR&gt;", html)
        self.assertIn("&quot;115&quot;", html)
        self.assertNotIn("<ESR>", html)
        self.assertNotIn('"115"', html)

    def test_snapshot_output_is_deterministic(self) -> None:
        record = reviewed_artifact_record_records(load_reviewed_artifact_records())[0]

        first = project_artifact_corpus_item(record, "snapshot_v0")["renderer_result"]["renderer_output"]
        second = project_artifact_corpus_item(record, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first, second)
        self.assertEqual(first["content"]["canonical_status"], "verified")

    def test_projection_does_not_call_sources_or_mutate_indexes(self) -> None:
        items = [
            *reviewed_artifact_record_records(load_reviewed_artifact_records()),
            *artifact_decision_outcome_records(load_artifact_decision_backed_outcomes()),
            blocked_for_user_details_fixture(),
        ]

        for item in items:
            for profile in BASELINE_PROFILES:
                result = project_artifact_corpus_item(item, profile)
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

