from __future__ import annotations

import unittest

from scripts.validate_local_apply_live_metadata_previews import validate


class ValidateLocalApplyLiveMetadataPreviewsTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual(result["status"], "pass", result["failures"])


if __name__ == "__main__":
    unittest.main()
