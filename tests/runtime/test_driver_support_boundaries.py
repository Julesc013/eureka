from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_driver_support


class DriverSupportBoundaryTests(unittest.TestCase):
    def test_driver_specific_boundary_flags_remain_false(self) -> None:
        result = run_seed_batch_driver_support(fixture=True)
        for key in (
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "download_performed",
            "file_fetch_performed",
            "extraction_executed",
            "install_execution_enabled",
            "model_provider_used",
            "deployment_performed",
            "malware_clean_claim_created",
            "compatibility_guarantee_created",
            "rights_clearance_claim_created",
            "cracks_keygens_serials_supported",
            "driver_updater_spam_supported",
        ):
            self.assertFalse(result[key], key)


if __name__ == "__main__":
    unittest.main()
