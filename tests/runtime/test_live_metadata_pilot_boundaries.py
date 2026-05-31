import unittest

from runtime.seed_batches import run_live_metadata_pilot_batch


class LiveMetadataPilotBoundaryTests(unittest.TestCase):
    def test_no_live_or_mutation_without_approval(self):
        result = run_live_metadata_pilot_batch(fixture=True)
        boundary = result["boundary_report"]

        self.assertEqual(result["status"], "waiting_for_operator_live_metadata_approval")
        self.assertFalse(boundary["operator_live_metadata_run_performed"])
        self.assertFalse(boundary["raw_live_response_committed"])
        self.assertFalse(boundary["download_performed"])
        self.assertFalse(boundary["extraction_executed"])
        self.assertFalse(boundary["accepted_truth_created"])
        self.assertFalse(boundary["reviewed_index_mutated"])
        self.assertFalse(boundary["public_index_mutated"])


if __name__ == "__main__":
    unittest.main()
