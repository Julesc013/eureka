from __future__ import annotations

import unittest

from runtime.review.live_metadata import (
    build_live_metadata_review_packet,
    load_live_metadata_candidates,
    run_live_metadata_candidate_review,
)


class ReviewLiveMetadataCandidatesTests(unittest.TestCase):
    def test_loads_eight_live_metadata_candidates(self) -> None:
        candidates = load_live_metadata_candidates()

        self.assertEqual(8, len(candidates))
        self.assertTrue(all(candidate["source_family"] == "internet_archive_metadata" for candidate in candidates))
        self.assertTrue(all(candidate["accepted_truth"] is False for candidate in candidates))
        self.assertTrue(all(candidate["raw_response_included"] is False for candidate in candidates))

    def test_review_packet_builds(self) -> None:
        candidates = load_live_metadata_candidates()
        packet = build_live_metadata_review_packet(candidates)

        self.assertEqual("live_metadata_candidate_review_packet.v0", packet["schema_version"])
        self.assertEqual(8, packet["candidate_count"])
        self.assertFalse(packet["accepted_truth"])

    def test_full_review_result_counts(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)

        self.assertEqual("pass", result["status"])
        self.assertEqual(8, result["live_metadata_candidates_reviewed"])
        self.assertEqual(1, result["reviewed_metadata_record_preview_count"])
        self.assertEqual(2, result["reviewed_source_lead_preview_count"])
        self.assertEqual(1, result["useful_lead_count"])
        self.assertEqual(2, result["needs_more_evidence_count"])
        self.assertEqual(2, result["rejected_or_duplicate_count"])


if __name__ == "__main__":
    unittest.main()
