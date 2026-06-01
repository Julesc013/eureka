from __future__ import annotations

import unittest

from scripts.validate_review_live_metadata_candidates import validate


class ValidateReviewLiveMetadataCandidatesTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual("pass", result["status"])
        self.assertFalse(result["new_live_source_calls_performed"])
        self.assertFalse(result["raw_live_response_committed"])
        self.assertFalse(result["accepted_truth_created"])


if __name__ == "__main__":
    unittest.main()
