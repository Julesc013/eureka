from __future__ import annotations

import copy
import unittest

from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.firmware_update import build_h5_firmware_update_candidates
from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import detect_h5_truth_boundary_violations
from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.payload_metadata import build_h5_payload_metadata_candidates
from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.runtime_redistributable import build_h5_runtime_redistributable_candidates


class H5FirmwareRuntimeMappingTests(unittest.TestCase):
    def test_firmware_runtime_payload_boundaries(self) -> None:
        firmware = build_h5_firmware_update_candidates({"source_id": "dell_support_downloads", "vendor_native_id": "f", "firmware_name": "fw"})[0]
        self.assertFalse(firmware["truth_boundary"]["firmware_update_candidate_is_approved_to_flash"])
        runtime = build_h5_runtime_redistributable_candidates({"source_id": "microsoft_runtime_redistributables", "vendor_native_id": "r", "runtime_name": "rt"})[0]
        self.assertFalse(runtime["truth_boundary"]["runtime_candidate_is_installability_truth"])
        payload = build_h5_payload_metadata_candidates({"source_id": "nvidia_driver_downloads", "vendor_native_id": "p", "package_or_payload_name": "payload"})[0]
        self.assertFalse(payload["download_allowed_current"])
        self.assertFalse(payload["installer_execution_allowed_current"])
        self.assertFalse(payload["firmware_flash_allowed_current"])
        self.assertFalse(payload["truth_boundary"]["payload_hash_proves_malware_safety"])
        self.assertFalse(payload["truth_boundary"]["signature_metadata_proves_authenticity"])

    def test_truth_claims_are_rejected(self) -> None:
        firmware = build_h5_firmware_update_candidates({"source_id": "x", "vendor_native_id": "f", "firmware_name": "fw"})[0]
        mutated = copy.deepcopy(firmware)
        mutated["truth_boundary"]["firmware_update_candidate_is_approved_to_flash"] = True
        self.assertTrue(detect_h5_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
