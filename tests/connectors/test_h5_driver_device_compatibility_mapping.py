from __future__ import annotations

import copy
import unittest

from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.driver_device_compatibility import build_h5_driver_device_compatibility_candidates
from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import detect_h5_truth_boundary_violations


class H5DriverCompatibilityMappingTests(unittest.TestCase):
    def test_compatibility_remains_candidate(self) -> None:
        candidates = build_h5_driver_device_compatibility_candidates({
            "source_id": "nvidia_driver_downloads",
            "vendor_native_id": "synthetic",
            "driver_name": "Synthetic Driver",
            "driver_version": "1",
            "device_vendor_id": "VEN_1234",
            "architecture": "x86_64",
        })
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertFalse(candidate["truth_boundary"]["compatibility_candidate_is_verified_compatibility"])
        self.assertFalse(candidate["truth_boundary"]["device_id_match_proves_safe_installability"])
        self.assertFalse(candidate["truth_boundary"]["os_version_match_proves_runtime_correctness"])
        self.assertFalse(candidate["truth_boundary"]["architecture_match_proves_device_compatibility"])

    def test_compatibility_truth_claim_is_rejected(self) -> None:
        candidate = build_h5_driver_device_compatibility_candidates({"source_id": "x", "vendor_native_id": "y", "driver_name": "d"})[0]
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["compatibility_candidate_is_verified_compatibility"] = True
        self.assertTrue(detect_h5_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
