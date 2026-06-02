from __future__ import annotations

import unittest

from scripts.validate_review_batch_apply_next import validate


class ValidateReviewBatchApplyNextTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual(result["status"], "pass", result["failures"])


if __name__ == "__main__":
    unittest.main()
