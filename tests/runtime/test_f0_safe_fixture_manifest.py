from __future__ import annotations

from pathlib import Path
import unittest

from runtime.extraction_safe_fixtures import build_container_descriptor_from_fixture, build_member_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0SafeFixtureManifestTests(unittest.TestCase):
    def test_safe_zip_manifest_enumerates_without_extraction(self) -> None:
        descriptor = build_container_descriptor_from_fixture(REPO_ROOT / "examples/f0/safe_zip_basic.zip")
        manifest = build_member_manifest(descriptor)
        self.assertTrue(manifest["manifest_only"])
        self.assertFalse(manifest["extracted_to_filesystem"])
        self.assertGreaterEqual(manifest["member_count"], 2)
        self.assertEqual(manifest["risk_report"]["blocked_member_count"], 0)

    def test_safe_zip_members_are_observations_not_truth(self) -> None:
        manifest = build_member_manifest(build_container_descriptor_from_fixture(REPO_ROOT / "examples/f0/safe_zip_basic.zip"))
        for member in manifest["members"]:
            self.assertTrue(member["review_required"])
            self.assertFalse(member["accepted_truth"])
            self.assertFalse(member["non_claims"]["filesystem_extraction_performed"])


if __name__ == "__main__":
    unittest.main()
