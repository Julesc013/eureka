from __future__ import annotations

import unittest

from tools.validators.validate_workbench_local_loop_closeout import validate


class ValidateWorkbenchLocalLoopCloseoutTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertTrue(result["script_checks"]["dry_run"])
        self.assertTrue(result["script_checks"]["temp_apply"])


if __name__ == "__main__":
    unittest.main()
