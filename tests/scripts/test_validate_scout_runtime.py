from __future__ import annotations

import unittest

from scripts.validate_scout_runtime import validate


class ValidateScoutRuntimeTest(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()
        self.assertEqual(result["status"], "pass", result["failures"])
        self.assertFalse(result["accepted_truth_created"])
        self.assertFalse(result["live_source_call_performed"])
        self.assertFalse(result["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
