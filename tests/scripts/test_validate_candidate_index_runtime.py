from __future__ import annotations

import unittest

from scripts.validate_candidate_index_runtime import validate


class ValidateCandidateIndexRuntimeTest(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()
        self.assertEqual(result["status"], "pass", result["failures"])
        self.assertFalse(result["accepted_truth_created"])
        self.assertFalse(result["reviewed_index_mutated"])
        self.assertFalse(result["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
