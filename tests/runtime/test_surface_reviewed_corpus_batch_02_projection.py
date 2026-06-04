from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.reviewed_seed_corpus.batch_02 import (
    BASELINE_PROFILES,
    load_renderer_expected_outputs,
    load_review_decision_backed_outcomes,
    load_reviewed_seed_records,
    load_surface_projection_fixtures,
    outcome_records,
    project_outcome,
    project_reviewed_seed_record,
    reviewed_seed_record_records,
    validate_renderer_expected_outputs,
    validate_surface_projection_fixtures,
)


FORBIDDEN_PUBLIC_ACTIONS = (
    "review_candidate",
    "promote",
    "reject",
    "request_more_evidence",
    "rebuild_index",
    "download",
    "install",
    "launch_emulator",
    "crawl_source",
    "arbitrary_live_lookup",
)


class SurfaceReviewedCorpusBatchTwoProjectionTests(unittest.TestCase):
    def test_projection_fixtures_and_renderer_expectations_validate(self) -> None:
        outcomes = load_review_decision_backed_outcomes()

        self.assertEqual(validate_surface_projection_fixtures(load_surface_projection_fixtures(), outcomes), ())
        self.assertEqual(validate_renderer_expected_outputs(load_renderer_expected_outputs(), outcomes), ())

    def test_outcomes_project_honest_statuses_across_baseline_renderers(self) -> None:
        for outcome in outcome_records(load_review_decision_backed_outcomes()):
            for profile in BASELINE_PROFILES:
                with self.subTest(outcome=outcome["outcome_id"], profile=profile):
                    result = project_outcome(outcome, profile)

                    self.assertEqual(result["view_model"]["canonical_status"], outcome["public_projection_status"])
                    self.assertIn(outcome["public_projection_status"], repr(result["renderer_result"]["renderer_output"]))
                    self.assertFalse(result["surface_kernel_called_source_provider"])
                    self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
                    self.assertFalse(result["surface_kernel_mutated_public_index"])
                    self.assertFalse(result["surface_kernel_mutated_master_index"])

    def test_reviewed_seed_records_project_verified_without_index_mutation(self) -> None:
        for record in reviewed_seed_record_records(load_reviewed_seed_records()):
            for profile in BASELINE_PROFILES:
                with self.subTest(record=record["reviewed_seed_record_id"], profile=profile):
                    result = project_reviewed_seed_record(record, profile)
                    renderer = result["renderer_result"]

                    self.assertEqual(result["view_model"]["canonical_status"], "verified")
                    self.assertIn("verified", repr(renderer["renderer_output"]))
                    self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
                    self.assertFalse(result["surface_kernel_mutated_public_index"])
                    self.assertFalse(result["surface_kernel_mutated_master_index"])
                    self.assertFalse(renderer["renderer_called_source_provider"])
                    self.assertFalse(renderer["renderer_mutated_reviewed_index"])
                    self.assertFalse(renderer["renderer_mutated_public_index"])
                    self.assertFalse(renderer["renderer_mutated_master_index"])

    def test_public_projection_strips_operator_actions(self) -> None:
        for outcome in outcome_records(load_review_decision_backed_outcomes()):
            rendered = [project_outcome(outcome, profile) for profile in BASELINE_PROFILES]
            combined_output = repr([result["renderer_result"]["renderer_output"] for result in rendered])
            combined_view_model = repr([result["view_model"] for result in rendered])

            for action in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(action, combined_output, f"{outcome['outcome_id']} rendered {action}")
                self.assertNotIn(action, combined_view_model, f"{outcome['outcome_id']} view leaked {action}")
            for result in rendered:
                action_ids = {action["action_id"] for action in result["view_model"]["actions"]}
                self.assertTrue(action_ids.issubset({"view", "inspect_evidence", "compare", "cite", "export_manifest"}))

    def test_operator_projection_can_retain_review_actions(self) -> None:
        reviewed = next(outcome for outcome in outcome_records(load_review_decision_backed_outcomes()) if outcome["decision"] == "promote")
        result = project_outcome(reviewed, "json_v0", visibility_posture="operator_private")

        self.assertEqual(result["view_model"]["visibility_posture"], "operator_private")
        self.assertIn("operator_actions", result["view_model"]["payload"])
        self.assertIn("promote", result["view_model"]["payload"]["operator_actions"])

    def test_html_renderer_escapes_near_miss_text(self) -> None:
        near_miss = next(outcome for outcome in outcome_records(load_review_decision_backed_outcomes()) if outcome["outcome_status"] == "near_miss")
        html = project_outcome(near_miss, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;client&gt;", html)
        self.assertIn("&quot;Blue&quot;", html)
        self.assertNotIn("<client>", html)
        self.assertNotIn('"Blue"', html)

    def test_snapshot_outputs_are_deterministic(self) -> None:
        outcome = outcome_records(load_review_decision_backed_outcomes())[0]
        record = reviewed_seed_record_records(load_reviewed_seed_records())[0]

        first_outcome = project_outcome(outcome, "snapshot_v0")["renderer_result"]["renderer_output"]
        second_outcome = project_outcome(outcome, "snapshot_v0")["renderer_result"]["renderer_output"]
        first_record = project_reviewed_seed_record(record, "snapshot_v0")["renderer_result"]["renderer_output"]
        second_record = project_reviewed_seed_record(record, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first_outcome, second_outcome)
        self.assertEqual(first_record, second_record)

    def test_unknown_status_degrades_honestly(self) -> None:
        outcome = deepcopy(outcome_records(load_review_decision_backed_outcomes())[0])
        outcome["public_projection_status"] = "not_a_known_status"
        outcome["outcome_status"] = "not_a_known_status"

        for profile in BASELINE_PROFILES:
            with self.subTest(profile=profile):
                result = project_outcome(outcome, profile)

                self.assertEqual(result["view_model"]["canonical_status"], "unknown")
                self.assertIn("unknown", repr(result["renderer_result"]["renderer_output"]))


if __name__ == "__main__":
    unittest.main()
