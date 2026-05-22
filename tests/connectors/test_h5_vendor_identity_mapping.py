from __future__ import annotations

import copy
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import detect_h5_truth_boundary_violations
from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.vendor_identity import build_h5_vendor_identity_candidate


class H5VendorIdentityMappingTests(unittest.TestCase):
    def test_vendor_identity_remains_candidate(self) -> None:
        record = {
            "source_id": "microsoft_download_center",
            "vendor_native_id": "synthetic",
            "vendor_name": "Microsoft",
            "product_name": "Synthetic Product",
            "product_family": "Synthetic Family",
            "support_page_ref": "fixture://support",
        }
        candidate = build_h5_vendor_identity_candidate(record)
        self.assertFalse(candidate["truth_boundary"]["vendor_identity_candidate_is_accepted_vendor_truth"])
        self.assertFalse(candidate["truth_boundary"]["vendor_source_proves_official_status"])
        self.assertFalse(candidate["truth_boundary"]["vendor_presence_proves_endorsement"])

    def test_vendor_truth_claim_is_rejected(self) -> None:
        record = build_h5_vendor_identity_candidate({"source_id": "x", "vendor_native_id": "y"})
        mutated = copy.deepcopy(record)
        mutated["truth_boundary"]["vendor_identity_candidate_is_accepted_vendor_truth"] = True
        self.assertTrue(detect_h5_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
