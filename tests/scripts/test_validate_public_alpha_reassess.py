from __future__ import annotations

import unittest

from scripts.validate_public_alpha_reassess import validate


class ValidatePublicAlphaReassessTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual("pass", result["status"])
        self.assertFalse(result["deployment_performed"])
        self.assertFalse(result["public_launch_performed"])


if __name__ == "__main__":
    unittest.main()
