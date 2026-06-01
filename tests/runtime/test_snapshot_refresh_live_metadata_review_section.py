from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_02


class SnapshotRefreshLiveMetadataReviewSectionTests(unittest.TestCase):
    def test_live_metadata_review_section_projects_review_outcomes(self) -> None:
        result = run_snapshot_refresh_02(from_live_metadata_review_examples=True)
        section = result["live_metadata_review_section"]

        self.assertEqual("snapshot_live_metadata_review_section.v0", section["schema_version"])
        self.assertEqual(8, section["review_decision_count"])
        self.assertEqual(1, section["reviewed_metadata_record_preview_count"])
        self.assertEqual(2, section["reviewed_source_lead_preview_count"])
        self.assertEqual(1, section["useful_lead_count"])
        self.assertEqual(2, section["needs_more_evidence_count"])
        self.assertEqual(2, section["rejected_or_duplicate_count"])
        self.assertFalse(section["accepted_truth"])
        self.assertFalse(section["review_preview_applied"])
        self.assertFalse(section["raw_response_included"])
        self.assertFalse(section["verified_download_claim_created"])
        self.assertFalse(section["malware_clean_claim_created"])
        self.assertFalse(section["rights_clearance_claim_created"])

        for decision in section["decisions"]:
            self.assertFalse(decision["accepted_truth"])
            self.assertFalse(decision["reviewed_artifact_claim"])
            self.assertFalse(decision["download_claim"])
            self.assertFalse(decision["malware_clean_claim"])
            self.assertFalse(decision["rights_clearance_claim"])

    def test_public_alpha_input_includes_review_counts(self) -> None:
        result = run_snapshot_refresh_02(from_live_metadata_review_examples=True)
        reassess_input = result["public_alpha_reassess_input"]

        self.assertEqual(1, reassess_input["reviewed_metadata_record_preview_count"])
        self.assertEqual(2, reassess_input["reviewed_source_lead_preview_count"])
        self.assertTrue(reassess_input["needs_local_apply_for_reviewed_previews"])
        self.assertFalse(reassess_input["public_launch_readiness_claimed"])


if __name__ == "__main__":
    unittest.main()
