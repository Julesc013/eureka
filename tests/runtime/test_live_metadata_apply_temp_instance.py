from __future__ import annotations

import unittest

from runtime.local_apply import run_local_apply_live_metadata_previews


class LiveMetadataApplyTempInstanceTests(unittest.TestCase):
    def test_temp_apply_readback_validates_without_committed_state(self) -> None:
        result = run_local_apply_live_metadata_previews(
            from_live_metadata_review_examples=True,
            use_temp_instance=True,
        )
        temp_apply = result["temp_apply_result"]

        self.assertTrue(temp_apply["temp_instance_initialized"])
        self.assertTrue(temp_apply["readback_validation_passed"])
        self.assertEqual(temp_apply["temp_instance_locator"], "system_temp_explicit_instance")
        self.assertTrue(temp_apply["temp_instance_path_redacted"])
        self.assertFalse(temp_apply["committed_instance_state"])


if __name__ == "__main__":
    unittest.main()
