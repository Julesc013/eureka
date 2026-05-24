from __future__ import annotations

import unittest

from tools.validators.validate_local_apply_gate import run_smoke


class LocalApplySmokeTests(unittest.TestCase):
    def test_validator_smoke_passes(self) -> None:
        result = run_smoke()

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["dry_run_preview_passed"])
        self.assertTrue(result["temp_instance_apply_passed"])
        self.assertTrue(result["rollback_passed"])


if __name__ == "__main__":
    unittest.main()
