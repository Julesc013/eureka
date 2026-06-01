from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_03


class SnapshotRefreshLocalApplySectionTests(unittest.TestCase):
    def test_local_apply_section_projects_temp_apply_counts(self) -> None:
        result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        section = result["local_apply_section"]

        self.assertEqual("pass", result["status"])
        self.assertEqual(3, section["eligible_preview_count"])
        self.assertEqual(1, section["reviewed_metadata_records_created"])
        self.assertEqual(2, section["reviewed_source_leads_created"])
        self.assertEqual(3, section["reviewed_record_delta_count"])
        self.assertTrue(section["temp_instance_apply_passed"])
        self.assertFalse(section["operator_instance_mutated"])
        self.assertFalse(section["public_index_mutated"])
        self.assertFalse(section["master_index_mutated"])

    def test_public_alpha_reassess_input_exists_without_launch_claims(self) -> None:
        result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        reassess = result["public_alpha_reassess_input"]

        self.assertEqual(4, reassess["total_limited_reviewed_record_projection_count"])
        self.assertFalse(reassess["launch_recommended"])
        self.assertTrue(reassess["needs_public_alpha_reassess_after_apply"])
        self.assertFalse(reassess["public_launch_readiness_claimed"])
        self.assertFalse(reassess["production_readiness_claimed"])


if __name__ == "__main__":
    unittest.main()
