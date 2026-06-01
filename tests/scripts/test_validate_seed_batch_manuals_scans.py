from __future__ import annotations

import unittest

from scripts.validate_seed_batch_manuals_scans import validate


class ValidateSeedBatchManualsScansTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()
        self.assertEqual("pass", result["status"], result["failures"])
        self.assertFalse(result["download_performed"])
        self.assertFalse(result["file_fetch_performed"])
        self.assertFalse(result["ocr_performed"])
        self.assertFalse(result["rights_clearance_claim_created"])


if __name__ == "__main__":
    unittest.main()
