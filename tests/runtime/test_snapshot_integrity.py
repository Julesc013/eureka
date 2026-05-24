from __future__ import annotations

import unittest

from runtime.snapshots import build_snapshot_from_examples


class SnapshotIntegrityTests(unittest.TestCase):
    def test_integrity_hashes_are_deterministic(self) -> None:
        first = build_snapshot_from_examples()["integrity_manifest"]
        second = build_snapshot_from_examples()["integrity_manifest"]

        self.assertEqual(first["entries"], second["entries"])
        self.assertEqual(first["hash_algorithm"], "sha256")
        self.assertFalse(first["private_signing_key_included"])


if __name__ == "__main__":
    unittest.main()
