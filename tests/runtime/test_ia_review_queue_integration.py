import tempfile
import unittest
from pathlib import Path

from runtime.review_queue import ReviewQueueStore
from runtime.source_observation.internet_archive_review import (
    apply_ia_review_decision,
    build_ia_review_items_from_candidates,
    load_default_ia_candidate_records,
    load_ia_review_policy,
    write_ia_review_decisions,
    write_ia_review_items,
)


ROOT = Path(__file__).resolve().parents[2]


class IAReviewQueueIntegrationTests(unittest.TestCase):
    def test_dry_run_does_not_mutate_review_queue(self):
        policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        items = build_ia_review_items_from_candidates(load_default_ia_candidate_records()[:4], policy)
        with tempfile.TemporaryDirectory() as tmp:
            with ReviewQueueStore.open(Path(tmp) / "review_queue.sqlite") as store:
                store.init()
                result = write_ia_review_items(store, items, dry_run=True)
                self.assertFalse(result["write_applied"])
                self.assertEqual(0, store.summarize().review_item_count)

    def test_apply_writes_review_items_and_decisions_to_temp_queue(self):
        policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        items = build_ia_review_items_from_candidates(load_default_ia_candidate_records(), policy)
        decisions = [apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", policy) for item in items]
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_fixture_replay" for item in items))
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_live_probe_preview" for item in items))
        with tempfile.TemporaryDirectory() as tmp:
            with ReviewQueueStore.open(Path(tmp) / "review_queue.sqlite") as store:
                item_result = write_ia_review_items(store, items, dry_run=False)
                decision_result = write_ia_review_decisions(store, decisions, dry_run=False)
                summary = store.summarize()
        self.assertTrue(item_result["write_applied"])
        self.assertTrue(decision_result["write_applied"])
        self.assertEqual(len(items), summary.review_item_count)
        self.assertEqual(len(decisions), summary.decision_count)


if __name__ == "__main__":
    unittest.main()
