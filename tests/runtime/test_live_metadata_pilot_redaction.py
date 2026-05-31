import unittest

from runtime.seed_batches import (
    build_live_metadata_request_plans,
    redact_live_metadata_transport_results,
    run_live_metadata_requests,
    select_live_metadata_seed_queries,
)


class LiveMetadataPilotRedactionTests(unittest.TestCase):
    def test_fixture_redaction_never_commits_raw_response(self):
        plans = build_live_metadata_request_plans(select_live_metadata_seed_queries())
        transport = run_live_metadata_requests(plans, mode="fixture")
        redacted = redact_live_metadata_transport_results(transport)

        self.assertEqual(redacted["redacted_result_count"], len(plans))
        self.assertFalse(redacted["raw_live_response_committed"])
        self.assertTrue(all("candidate_identifier_hash" in row for row in redacted["redacted_results"]))


if __name__ == "__main__":
    unittest.main()
