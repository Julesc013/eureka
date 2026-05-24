from __future__ import annotations

import unittest

from runtime.relay import build_relay_from_snapshot
from runtime.relay.validation import validate_relay_manifest
from runtime.snapshots import build_snapshot_from_examples


class RelayManifestTests(unittest.TestCase):
    def test_relay_manifest_is_read_only(self) -> None:
        relay = build_relay_from_snapshot(build_snapshot_from_examples())
        manifest = relay["relay_manifest"]

        self.assertEqual(validate_relay_manifest(manifest)["status"], "pass")
        self.assertTrue(manifest["read_only"])
        self.assertFalse(manifest["mutation_enabled"])
        self.assertFalse(manifest["live_source_actions_enabled"])


if __name__ == "__main__":
    unittest.main()
