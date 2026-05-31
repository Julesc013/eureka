from __future__ import annotations

import unittest

from scripts.validate_snapshot_refresh import validate


class ValidateSnapshotRefreshTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual("pass", result["status"], result["failures"])
        self.assertFalse(result["accepted_truth_created"])
        self.assertFalse(result["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
