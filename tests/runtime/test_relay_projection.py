from __future__ import annotations

import unittest

from runtime.relay import build_relay_from_snapshot, project_relay_response, query_relay_snapshot
from runtime.snapshots import build_snapshot_from_examples


class RelayProjectionTests(unittest.TestCase):
    def test_query_and_projection_return_read_only_response(self) -> None:
        relay = build_relay_from_snapshot(build_snapshot_from_examples(), "public_api_read_only")
        query = query_relay_snapshot(relay["relay_record_index"], "sampleproject")
        projection = project_relay_response(query, "lite_client_read_only")

        self.assertEqual(query["result_count"], 1)
        self.assertTrue(query["read_only"])
        self.assertEqual(projection["projection_profile"], "lite_client_read_only")
        self.assertTrue(projection["read_only"])


if __name__ == "__main__":
    unittest.main()
