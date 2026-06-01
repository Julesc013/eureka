from __future__ import annotations

import unittest

from runtime.review.live_metadata import run_live_metadata_candidate_review


class LiveMetadataLocalApplyHandoffTests(unittest.TestCase):
    def test_local_apply_is_handoff_only(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
        handoff = result["local_apply_handoff"]

        self.assertEqual("live_metadata_local_apply_handoff.v0", handoff["schema_version"])
        self.assertTrue(handoff["local_apply_handoff_only"])
        self.assertFalse(handoff["local_apply_executed"])
        self.assertTrue(handoff["requires_separate_local_apply_gate"])
        self.assertEqual(3, len(handoff["promotion_preview_refs"]))
        self.assertFalse(handoff["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
