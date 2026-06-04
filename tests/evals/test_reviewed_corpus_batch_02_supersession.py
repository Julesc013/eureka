from __future__ import annotations

import unittest

from evals.hard_queries.reviewed_seed_corpus.batch_02 import (
    load_review_decision_backed_outcomes,
    load_source_reference_index,
    load_supersession_map,
    outcome_records,
    source_reference_records,
    supersession_records,
    validate_source_reference_index,
    validate_supersession_map,
)


class ReviewedCorpusBatchTwoSupersessionTests(unittest.TestCase):
    def test_supersession_map_links_duplicate_decisions_without_new_records(self) -> None:
        payload = load_supersession_map()

        self.assertEqual(validate_supersession_map(payload), ())
        supersessions = supersession_records(payload)
        self.assertEqual(len(supersessions), 3)
        for item in supersessions:
            self.assertFalse(item["counts_as_new_reviewed_record"])
            self.assertTrue(item["target_reviewed_seed_record_id"])
            self.assertEqual(item["public_projection_status"], "superseded")

    def test_superseded_outcomes_do_not_create_reviewed_records(self) -> None:
        superseded = [
            outcome
            for outcome in outcome_records(load_review_decision_backed_outcomes())
            if outcome["outcome_status"] == "superseded"
        ]

        self.assertEqual(len(superseded), 3)
        for outcome in superseded:
            self.assertEqual(outcome["decision"], "supersede")
            self.assertFalse(outcome["counts_as_reviewed"])
            self.assertFalse(outcome["reviewed_seed_record_created"])
            self.assertTrue(outcome["reviewed_seed_record_id"])

    def test_source_reference_index_preserves_batch_sources_without_runtime_calls(self) -> None:
        payload = load_source_reference_index()

        self.assertEqual(validate_source_reference_index(payload), ())
        refs = source_reference_records(payload)
        self.assertEqual(len(refs), 17)
        ref_ids = {item["source_ref_id"] for item in refs}
        self.assertIn("src_b01_7zip_official", ref_ids)
        self.assertIn("src_b01_firefox_xp_support_article", ref_ids)
        self.assertIn("src_missing_win98_driver_scope", ref_ids)
        for ref in refs:
            self.assertFalse(ref["runtime_live_source_call_performed"])


if __name__ == "__main__":
    unittest.main()
