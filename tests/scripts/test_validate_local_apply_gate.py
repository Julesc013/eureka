from __future__ import annotations

import unittest

from tools.validators.validate_local_apply_gate import validate


class ValidateLocalApplyGateScriptTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["smoke"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
