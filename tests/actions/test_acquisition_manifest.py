from __future__ import annotations

import copy
import unittest

from runtime.actions.acquisition_manifest import build_acquisition_manifest, validate_acquisition_manifest


class AcquisitionManifestTests(unittest.TestCase):
    def test_acquisition_manifest_builds_but_does_not_download(self) -> None:
        manifest = build_acquisition_manifest({
            "subject_ref": "candidate.example.v0",
            "source_refs": ["source.example.v0"],
            "source_locator": "fixture-source-locator",
        })
        self.assertEqual(manifest["acquisition_status"], "descriptive_only")
        self.assertIn("download", manifest["blocked_actions"])
        self.assertFalse(manifest["truth_boundary"]["acquisition_manifest_downloads_file"])
        self.assertEqual(validate_acquisition_manifest(manifest), [])

    def test_acquisition_manifest_does_not_claim_rights_malware_installability(self) -> None:
        manifest = build_acquisition_manifest({"subject_ref": "candidate.example.v0"})
        for field in ("rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed", "compatibility_certification_claimed"):
            self.assertFalse(manifest["truth_boundary"][field])

    def test_download_claim_is_rejected(self) -> None:
        manifest = build_acquisition_manifest({"subject_ref": "candidate.example.v0"})
        bad = copy.deepcopy(manifest)
        bad["truth_boundary"]["acquisition_manifest_downloads_file"] = True
        self.assertTrue(any("acquisition_manifest_downloads_file" in error for error in validate_acquisition_manifest(bad)))


if __name__ == "__main__":
    unittest.main()
