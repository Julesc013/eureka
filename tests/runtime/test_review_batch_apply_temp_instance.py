from __future__ import annotations

import unittest

from runtime.local_apply import run_review_batch_apply_next


class ReviewBatchApplyTempInstanceTests(unittest.TestCase):
    def test_temp_instance_apply_readback_passes(self) -> None:
        result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)
        temp_result = result["temp_apply_result"]

        self.assertTrue(temp_result["temp_instance_initialized"])
        self.assertTrue(temp_result["temp_instance_apply_passed"])
        self.assertTrue(temp_result["readback_validation_passed"])
        self.assertTrue(temp_result["temp_instance_path_redacted"])


if __name__ == "__main__":
    unittest.main()
