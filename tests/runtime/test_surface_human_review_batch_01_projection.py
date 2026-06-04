from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.human_reviews.batch_01 import (
    BASELINE_PROFILES,
    load_renderer_expected_outputs,
    load_review_decisions,
    load_reviewed_seed_records,
    load_surface_projection_fixtures,
    project_review_decision,
    project_reviewed_seed_record,
    review_decision_records,
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
    "freeze_review",
    "download",
    "install",
    "launch_emulator",
    "run_extraction",
    "submit_direct_evidence",
    "crawl_source",
    "arbitrary_live_lookup",
)


class SurfaceHumanReviewBatchOneProjectionTests(unittest.TestCase):
    def test_surface_and_renderer_fixtures_validate(self) -> None:
        decisions = load_review_decisions()

        self.assertEqual(validate_surface_projection_fixtures(load_surface_projection_fixtures(), decisions), ())
        self.assertEqual(validate_renderer_expected_outputs(load_renderer_expected_outputs(), decisions), ())

    def test_review_decisions_project_honest_statuses_across_baseline_renderers(self) -> None:
        for decision in review_decision_records(load_review_decisions()):
            for profile in BASELINE_PROFILES:
                with self.subTest(decision=decision["review_decision_id"], profile=profile):
                    result = project_review_decision(decision, profile)

                    self.assertEqual(result["view_model"]["canonical_status"], decision["resulting_status"])
                    self.assertIn(decision["resulting_status"], repr(result["renderer_result"]["renderer_output"]))
                    self.assertFalse(result["surface_kernel_called_source_provider"])
                    self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
                    self.assertFalse(result["surface_kernel_mutated_public_index"])
                    self.assertFalse(result["surface_kernel_mutated_master_index"])

    def test_reviewed_seed_record_projects_verified_without_index_mutation(self) -> None:
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
        for decision in review_decision_records(load_review_decisions()):
            rendered = [project_review_decision(decision, profile) for profile in BASELINE_PROFILES]
            combined = repr([result["renderer_result"]["renderer_output"] for result in rendered])
            view_repr = repr([result["view_model"] for result in rendered])

            for action in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(action, combined, f"{decision['review_decision_id']} rendered {action}")
                self.assertNotIn(action, view_repr, f"{decision['review_decision_id']} view leaked {action}")
            for result in rendered:
                actions = {action["action_id"] for action in result["view_model"]["actions"]}
                self.assertTrue(actions.issubset({"view", "inspect_evidence", "compare", "cite", "export_manifest"}))

    def test_operator_projection_can_retain_review_actions(self) -> None:
        promote = next(decision for decision in review_decision_records(load_review_decisions()) if decision["decision"] == "promote")
        result = project_review_decision(promote, "json_v0", visibility_posture="operator_private")

        self.assertEqual(result["view_model"]["visibility_posture"], "operator_private")
        self.assertIn("operator_actions", result["view_model"]["payload"])
        self.assertIn("promote", result["view_model"]["payload"]["operator_actions"])

    def test_need_near_miss_and_superseded_outputs_preserve_uncertainty(self) -> None:
        decisions = review_decision_records(load_review_decisions())
        need = next(decision for decision in decisions if decision["review_decision_id"] == "hrd_b01_hq_driver_win98_mark_need")
        near_miss = next(decision for decision in decisions if decision["review_decision_id"] == "hrd_b01_hq_blue_ftp_flashfxp_mark_near_miss")
        superseded = next(decision for decision in decisions if decision["decision"] == "supersede")

        need_text = project_review_decision(need, "text_v0")["renderer_result"]["renderer_output"]["content"]
        near_miss_text = project_review_decision(near_miss, "text_v0")["renderer_result"]["renderer_output"]["content"]
        superseded_text = project_review_decision(superseded, "text_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("Status: need", need_text)
        self.assertIn("hardware", need_text)
        self.assertIn("Status: near_miss", near_miss_text)
        self.assertIn("visual clue", near_miss_text)
        self.assertIn("Status: superseded", superseded_text)

    def test_html_renderer_escapes_review_decision_text(self) -> None:
        decision = deepcopy(next(item for item in review_decision_records(load_review_decisions()) if item["decision"] == "mark_near_miss"))
        decision["title"] = "Old \"Blue\" FTP <client> review"

        html = project_review_decision(decision, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;client&gt;", html)
        self.assertIn("&quot;Blue&quot;", html)
        self.assertNotIn("<client>", html)
        self.assertNotIn('"Blue"', html)

    def test_snapshot_outputs_are_deterministic(self) -> None:
        decision = review_decision_records(load_review_decisions())[0]
        record = reviewed_seed_record_records(load_reviewed_seed_records())[0]

        first_decision = project_review_decision(decision, "snapshot_v0")["renderer_result"]["renderer_output"]
        second_decision = project_review_decision(decision, "snapshot_v0")["renderer_result"]["renderer_output"]
        first_record = project_reviewed_seed_record(record, "snapshot_v0")["renderer_result"]["renderer_output"]
        second_record = project_reviewed_seed_record(record, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first_decision, second_decision)
        self.assertEqual(first_record, second_record)


if __name__ == "__main__":
    unittest.main()
