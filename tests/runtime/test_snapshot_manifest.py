from __future__ import annotations

import unittest

from runtime.snapshots import build_snapshot_from_examples


class SnapshotManifestTests(unittest.TestCase):
    def test_manifest_is_reviewed_only_and_counts_records(self) -> None:
        manifest = build_snapshot_from_examples()["manifest"]

        self.assertEqual(manifest["schema_version"], "snapshot_manifest.v0")
        self.assertTrue(manifest["reviewed_only"])
        self.assertTrue(manifest["public_safe"])
        self.assertEqual(manifest["record_count"], len(manifest["record_refs"]))


if __name__ == "__main__":
    unittest.main()
