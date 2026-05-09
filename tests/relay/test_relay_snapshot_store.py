import unittest

from runtime.relay.profiles import load_relay_policy
from runtime.relay.snapshot_store import get_snapshot_record, load_snapshot_for_relay, query_snapshot_records


class RelaySnapshotStoreTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_relay_policy()

    def test_snapshot_store_reads_explicit_fixture_only(self):
        store = load_snapshot_for_relay("examples/snapshots/fixtures/search_snapshot_input_v0.json", self.policy)
        self.assertEqual(store["schema_version"], "relay_snapshot_store.v0")
        self.assertEqual(len(store["records"]), 2)

    def test_search_query_reads_fixture_records(self):
        store = load_snapshot_for_relay("examples/snapshots/fixtures/search_snapshot_input_v0.json", self.policy)
        results = query_snapshot_records(store, "driver", self.policy)
        self.assertTrue(results)
        self.assertEqual(results[0]["record_type"], "search_result")

    def test_object_record_lookup_from_object_fixture(self):
        store = load_snapshot_for_relay("examples/snapshots/fixtures/object_snapshot_input_v0.json", self.policy)
        record = get_snapshot_record(store, "object_record", "demo", self.policy)
        self.assertIsNotNone(record)
        self.assertEqual(record["record_type"], "object_record")

    def test_no_write_mutation_occurs(self):
        store = load_snapshot_for_relay("examples/snapshots/fixtures/search_snapshot_input_v0.json", self.policy)
        before = len(store["records"])
        query_snapshot_records(store, "driver", self.policy)
        self.assertEqual(before, len(store["records"]))

    def test_no_outbound_network_call_occurs(self):
        store = load_snapshot_for_relay("examples/snapshots/fixtures/search_snapshot_input_v0.json", self.policy)
        self.assertIn("no live source access", " ".join(store["limitations"]).casefold())


if __name__ == "__main__":
    unittest.main()

