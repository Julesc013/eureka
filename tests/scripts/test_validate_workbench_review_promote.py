from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_workbench_review_promote import validate


class ValidateWorkbenchReviewPromoteTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate(ROOT)
        self.assertEqual("pass", result["status"], result)
        self.assertTrue(result["operator_token_required"])
        self.assertTrue(result["public_projection_blocked"])
        self.assertTrue(result["native_read_only_projection_blocked"])
        self.assertTrue(result["temp_reviewed_index_refresh_passed"])


if __name__ == "__main__":
    unittest.main()
