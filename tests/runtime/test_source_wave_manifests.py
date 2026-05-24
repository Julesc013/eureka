from __future__ import annotations

import unittest

from runtime.source.action import (
    REQUIRED_SOURCE_WAVE_FAMILIES,
    get_source_family_manifest,
    validate_source_action_manifest,
)


class SourceWaveManifestTests(unittest.TestCase):
    def test_family_manifests_validate_as_source_action_manifests(self) -> None:
        for family in REQUIRED_SOURCE_WAVE_FAMILIES:
            with self.subTest(family=family):
                manifest = get_source_family_manifest(family)
                self.assertEqual("source_family_manifest.v0", manifest["schema_version"])
                self.assertEqual("pass", validate_source_action_manifest(manifest)["status"])
                self.assertFalse(manifest["live_enabled_default"])
                self.assertFalse(manifest["downloads_allowed"])
                self.assertFalse(manifest["extraction_allowed"])


if __name__ == "__main__":
    unittest.main()
