import unittest

from runtime.seed_batches import build_live_metadata_request_plans, select_live_metadata_seed_queries


class LiveMetadataPilotPlanningTests(unittest.TestCase):
    def test_seed_query_selection_has_domain_mix(self):
        queries = select_live_metadata_seed_queries()

        self.assertGreaterEqual(len([q for q in queries if q["seed_batch_id"] == "seed_batch_frontier_media_00"]), 4)
        self.assertGreaterEqual(len([q for q in queries if q["seed_batch_id"] == "seed_batch_legacy_software_00"]), 4)
        self.assertTrue(all(q["accepted_truth"] is False for q in queries))

    def test_request_plans_are_metadata_only(self):
        plans = build_live_metadata_request_plans(select_live_metadata_seed_queries())

        self.assertEqual(len(plans), 8)
        self.assertTrue(all(plan["source_family"] == "internet_archive_metadata" for plan in plans))
        self.assertTrue(all(plan["metadata_only"] is True for plan in plans))
        self.assertTrue(all(plan["downloads_enabled"] is False for plan in plans))


if __name__ == "__main__":
    unittest.main()
