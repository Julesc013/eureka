import unittest

from scripts.validate_live_metadata_pilot_batch import validate


class ValidateLiveMetadataPilotBatchTests(unittest.TestCase):
    def test_validator_passes(self):
        result = validate()

        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["operator_live_metadata_run_performed"])
        self.assertFalse(result["raw_live_response_committed"])


if __name__ == "__main__":
    unittest.main()
