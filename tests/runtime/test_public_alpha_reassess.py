from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess


class PublicAlphaReassessTests(unittest.TestCase):
    def test_reassessment_builds_full_packet(self) -> None:
        result = run_public_alpha_reassess(from_snapshot_refresh_examples=True)

        self.assertEqual("public_alpha_reassess_result.v0", result["schema_version"])
        self.assertEqual("PUBLIC-ALPHA-REASSESS-00", result["task"])
        self.assertEqual(1, result["reviewed_record_count"])
        self.assertEqual(28, result["candidate_count"])
        self.assertFalse(result["launch_recommended"])
        self.assertTrue(result["demo_mode_recommended"])


if __name__ == "__main__":
    unittest.main()
