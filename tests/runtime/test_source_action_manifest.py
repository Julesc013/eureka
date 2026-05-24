from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.connectors.internet_archive_metadata import build_registration
from runtime.source.action import validate_source_action_manifest


class SourceActionManifestTests(unittest.TestCase):
    def test_fixture_manifest_validates(self) -> None:
        result = validate_source_action_manifest(build_adapter().manifest())
        self.assertEqual("pass", result["status"])

    def test_ia_reference_registration_is_not_enabled_by_default(self) -> None:
        registration = build_registration()
        self.assertFalse(registration["default_enabled"])
        self.assertFalse(registration["public_fanout_allowed"])
        self.assertFalse(registration["downloads_allowed"])


if __name__ == "__main__":
    unittest.main()
