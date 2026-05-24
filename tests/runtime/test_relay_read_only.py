from __future__ import annotations

import unittest

from runtime.relay import build_relay_from_snapshot
from runtime.snapshots import build_snapshot_from_examples


class RelayReadOnlyTests(unittest.TestCase):
    def test_relay_boundary_flags_are_false(self) -> None:
        relay = build_relay_from_snapshot(build_snapshot_from_examples())
        boundary = relay["relay_boundary_report"]

        for field in (
            "operator_instance_mutated",
            "master_index_mutated",
            "committed_data_public_index_mutated",
            "live_source_call_performed",
            "download_performed",
            "extraction_executed",
            "deployment_performed",
        ):
            self.assertFalse(boundary[field], field)


if __name__ == "__main__":
    unittest.main()
