from __future__ import annotations

import unittest

from runtime.local_apply import run_local_apply_live_metadata_previews


class LocalApplyLiveMetadataPreviewsTests(unittest.TestCase):
    def test_temp_apply_creates_expected_limited_records(self) -> None:
        result = run_local_apply_live_metadata_previews(
            from_live_metadata_review_examples=True,
            use_temp_instance=True,
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["eligible_preview_count"], 3)
        self.assertEqual(result["reviewed_metadata_records_created"], 1)
        self.assertEqual(result["reviewed_source_leads_created"], 2)
        self.assertEqual(result["reviewed_record_delta_count"], 3)
        self.assertTrue(result["temp_instance_apply_passed"])


if __name__ == "__main__":
    unittest.main()
