from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_legacy_software


class LegacySoftwareBoundaryTests(unittest.TestCase):
    def test_boundary_flags_stay_false(self) -> None:
        result = run_seed_batch_legacy_software(fixture=True)
        for key in (
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "raw_live_response_committed",
            "download_performed",
            "extraction_executed",
            "install_execution_enabled",
            "model_provider_used",
            "deployment_performed",
            "cracks_keygens_serials_supported",
            "malware_clean_claims_created",
        ):
            self.assertFalse(result[key], key)


if __name__ == "__main__":
    unittest.main()
