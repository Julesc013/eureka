from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_ia_live_metadata_lane import validate_repo


class ValidateIALiveMetadataLaneTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate_repo(ROOT)
        self.assertEqual("valid", result["status"], result)
        self.assertTrue(result["dry_run_passed"])
        self.assertTrue(result["mock_live_passed"])
        self.assertTrue(result["public_projection_blocked"])
        self.assertFalse(result["raw_response_committed"])


if __name__ == "__main__":
    unittest.main()
