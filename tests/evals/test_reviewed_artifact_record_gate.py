from __future__ import annotations

import unittest

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS
from evals.hard_queries.artifact_record_gate.gate_00 import loader


class ReviewedArtifactRecordGateTests(unittest.TestCase):
    def test_required_outputs_exist_and_validate(self) -> None:
        self.assertEqual(loader.validate_required_outputs(), ())

        self.assertEqual(
            loader.validate_artifact_evidence_levels(loader.load_artifact_evidence_levels()),
            (),
        )
        self.assertEqual(
            loader.validate_existing_seed_record_classification(loader.load_existing_seed_record_classification()),
            (),
        )
        self.assertEqual(
            loader.validate_hard_query_artifact_coverage(loader.load_hard_query_artifact_coverage()),
            (),
        )
        self.assertEqual(
            loader.validate_public_alpha_artifact_gate(loader.load_public_alpha_artifact_gate()),
            (),
        )
        self.assertEqual(
            loader.validate_source_reference_index(loader.load_source_reference_index()),
            (),
        )
        self.assertEqual(
            loader.validate_renderer_projection_fixtures(loader.load_renderer_projection_fixtures()),
            (),
        )

    def test_artifact_levels_do_not_allow_false_verified_claims(self) -> None:
        payload = loader.load_artifact_evidence_levels()
        levels = payload["levels"]

        self.assertEqual(tuple(item["level_id"] for item in levels), loader.ARTIFACT_LEVELS)
        for item in levels[:-1]:
            self.assertFalse(item["verified_artifact_claim_allowed"], item["level_id"])
        self.assertTrue(levels[-1]["verified_artifact_claim_allowed"])
        self.assertFalse(payload["truth_boundary"]["metadata_is_artifact_truth"])
        self.assertFalse(payload["truth_boundary"]["source_observation_self_promotes"])

    def test_current_seed_records_are_support_facts_not_artifact_records(self) -> None:
        payload = loader.load_existing_seed_record_classification()
        records = loader.classification_records(payload)
        reviewed_seed_records = [item for item in records if item["record_kind"] == "reviewed_seed_record"]

        self.assertEqual(len(reviewed_seed_records), 3)
        self.assertEqual(payload["counts"]["reviewed_support_fact_count"], 3)
        self.assertEqual(payload["counts"]["reviewed_artifact_record_count"], 0)
        self.assertEqual(payload["counts"]["verified_artifact_count"], 0)
        for record in reviewed_seed_records:
            self.assertEqual(record["current_status"], "verified")
            self.assertEqual(record["artifact_evidence_level"], "artifact_level_1_metadata_or_source_lead")
            self.assertEqual(record["public_claim_allowed"], ["support_fact"])
            self.assertFalse(record["qualifies_as_reviewed_artifact_record"])
            self.assertFalse(record["qualifies_as_verified_artifact"])
            self.assertIn("support", record["required_disclaimer"])

    def test_source_and_metadata_leads_do_not_satisfy_artifact_gate(self) -> None:
        records = loader.classification_records(loader.load_existing_seed_record_classification())
        leads = [
            item
            for item in records
            if item["artifact_evidence_level"] in {
                "artifact_level_1_metadata_or_source_lead",
                "artifact_level_2_source_observed_artifact_listing",
            }
        ]

        self.assertGreaterEqual(len(leads), 10)
        for item in leads:
            self.assertFalse(item["qualifies_as_verified_artifact"], item["record_id"])
            self.assertFalse(item["qualifies_as_reviewed_artifact_record"], item["record_id"])

    def test_public_alpha_artifact_gate_fails_honestly(self) -> None:
        gate = loader.load_public_alpha_artifact_gate()

        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_promotion_blocked"])
        self.assertEqual(gate["reviewed_artifact_record_count"], 0)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertEqual(gate["next_recommended_task"], "MANUAL-ARTIFACT-OBSERVATION-BATCH-00")
        self.assertEqual(
            gate["source_snapshot_release_gate_after_this_task"],
            "green_at_prior_head_but_stale_after_this_commit",
        )
        self.assertIn("verified artifact", gate["forbidden_public_claims_now"])

    def test_hard_query_coverage_preserves_blockers(self) -> None:
        coverage = loader.load_hard_query_artifact_coverage()
        records = loader.coverage_records(coverage)
        by_query = {item["query_id"]: item for item in records}

        self.assertEqual(set(by_query), set(REQUIRED_HARD_QUERY_IDS))
        self.assertEqual(coverage["artifact_level_2_or_higher_reviewed_outcome_coverage"], "2/6")
        self.assertEqual(coverage["artifact_level_3_or_higher_reviewed_outcome_coverage"], "0/6")
        self.assertTrue(by_query["hq_driver_win98"]["blocked_for_user_details"])
        self.assertEqual(
            by_query["hq_driver_win98"]["highest_artifact_evidence_level"],
            "artifact_level_0_mention_only",
        )
        self.assertEqual(
            by_query["hq_sound_blaster_ct1740_manual"]["highest_artifact_evidence_level"],
            "artifact_level_2_source_observed_artifact_listing",
        )
        self.assertEqual(
            by_query["hq_ray_tracing_1994_magazine"]["highest_artifact_evidence_level"],
            "artifact_level_2_source_observed_artifact_listing",
        )

    def test_public_projection_fixtures_strip_operator_actions(self) -> None:
        fixtures = loader.load_renderer_projection_fixtures()["fixtures"]

        self.assertGreaterEqual(len(fixtures), 4)
        for fixture in fixtures:
            actions = set(fixture["public_actions"])
            self.assertFalse(actions & loader.FORBIDDEN_PUBLIC_ACTIONS, fixture["fixture_id"])
            self.assertFalse(fixture["qualifies_as_reviewed_artifact_record"])
            self.assertFalse(fixture["qualifies_as_verified_artifact"])
            self.assertTrue(fixture["public_label"])
            self.assertTrue(fixture["required_disclaimer"])

    def test_no_live_source_calls_or_mutation_claims(self) -> None:
        source_index = loader.load_source_reference_index()
        for source in loader.source_records(source_index):
            self.assertFalse(source["runtime_live_source_call_performed"], source["source_ref_id"])

        report = loader.read_gate_text("truth_boundary_report.md")
        self.assertIn("did not create reviewed artifact records", report)
        self.assertIn("downloads", report)
        self.assertIn("Wayback replays", report)
        self.assertIn("Synthetic eval fixtures are not evidence", report)

    def test_windows_98_driver_remains_blocked_without_hardware_details(self) -> None:
        user_blocks = loader.read_gate_text("blocked_for_user_details.yml")

        self.assertIn("block_artifact_win98_driver_hardware_identity", user_blocks)
        self.assertIn("hardware_vendor", user_blocks)
        self.assertIn("device_id_or_chipset", user_blocks)
        self.assertIn("USER-HARDWARE-DETAILS-00", user_blocks)


if __name__ == "__main__":
    unittest.main()
