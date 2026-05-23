import json
import tempfile
import unittest
from pathlib import Path

from runtime.evidence.ledger import EvidenceCandidateRecord, EvidenceLedgerStore
from runtime.review.queue import (
    ReviewDecision,
    ReviewDecisionKind,
    ReviewEvent,
    ReviewEventKind,
    ReviewItemRecord,
    ReviewQueueStatus,
    ReviewQueueStore,
)
from runtime.review.queue.validation import (
    validate_no_public_truth_fields,
    validate_review_decision,
    validate_review_queue_path,
)
from runtime.source.cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source.observation import build_evidence_candidate
from scripts.demo_review_queue_store import run_demo
from scripts.demo_source_cache_store import build_demo_objects


def build_review_fixture():
    source_record, response, observation, normalized = build_demo_objects()
    candidate = build_evidence_candidate(normalized)
    cache_entry = build_cache_entry(source_record, response, observation, normalized, SourceCacheStatus.CACHED)
    evidence_record = EvidenceCandidateRecord.from_candidate(
        candidate,
        normalized_observation_id=normalized.normalized_observation_id,
        source_cache_entry_id=cache_entry.entry_id,
    )
    review_item = ReviewItemRecord.from_evidence(evidence_record, source_cache_entry_id=cache_entry.entry_id)
    return source_record, response, observation, normalized, cache_entry, evidence_record, review_item


class ReviewQueueStoreTests(unittest.TestCase):
    def test_init_creates_schema(self):
        with ReviewQueueStore.open(":memory:") as store:
            applied = store.init()
            self.assertEqual(1, len(applied))
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_in_memory_store_works(self):
        *_, review_item = build_review_fixture()
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            fetched = store.get_review_item(review_item.review_item_id)
            self.assertEqual(review_item.review_item_id, fetched.review_item_id)

    def test_file_backed_tempdir_store_works(self):
        *_, review_item = build_review_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.sqlite"
            with ReviewQueueStore.open(path) as store:
                store.init()
                store.enqueue_review_item(review_item)
            with ReviewQueueStore.open(path) as store:
                store.init()
                self.assertIsNotNone(store.get_review_item(review_item.review_item_id))

    def test_invalid_db_path_is_rejected(self):
        self.assertTrue(validate_review_queue_path("runtime/out.sqlite"))

    def test_hidden_private_roots_are_rejected(self):
        self.assertTrue(validate_review_queue_path(".cache/review.sqlite"))

    def test_enqueue_get_review_item(self):
        *_, review_item = build_review_fixture()
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            fetched = store.get_review_item(review_item.review_item_id)
            self.assertEqual(ReviewQueueStatus.NEEDS_REVIEW, fetched.queue_status)

    def test_append_list_review_event(self):
        *_, review_item = build_review_fixture()
        event = ReviewEvent(review_item.review_item_id, ReviewEventKind.NOTE_ADDED, {"note": "one"})
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            store.append_event(event)
            self.assertIn(event.event_id, [item.event_id for item in store.list_events(review_item.review_item_id)])

    def test_event_order_is_preserved(self):
        *_, review_item = build_review_fixture()
        first = ReviewEvent(review_item.review_item_id, ReviewEventKind.NOTE_ADDED, {"order": 1})
        second = ReviewEvent(review_item.review_item_id, ReviewEventKind.NOTE_ADDED, {"order": 2})
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            store.append_event(first)
            store.append_event(second)
            ids = [item.event_id for item in store.list_events(review_item.review_item_id)]
            self.assertLess(ids.index(first.event_id), ids.index(second.event_id))

    def test_evidence_and_source_cache_links_work(self):
        *_, cache_entry, evidence_record, review_item = build_review_fixture()
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            store.link_evidence(review_item.review_item_id, evidence_record.evidence_id)
            store.link_source_cache_entry(review_item.review_item_id, cache_entry.entry_id)
            fetched = store.get_review_item(review_item.review_item_id)
            self.assertEqual(evidence_record.evidence_id, fetched.evidence_id)
            self.assertEqual(cache_entry.entry_id, fetched.source_cache_entry_id)

    def test_explicit_accept_decision_records_local_status(self):
        *_, review_item = build_review_fixture()
        decision = ReviewDecision(review_item.review_item_id, ReviewDecisionKind.ACCEPT, "operator:local")
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            store.record_decision(review_item.review_item_id, decision)
            fetched = store.get_review_item(review_item.review_item_id)
            self.assertEqual(ReviewQueueStatus.ACCEPTED, fetched.queue_status)
            self.assertEqual(1, len(store.list_decisions(review_item.review_item_id)))

    def test_reject_and_block_decisions_require_reason(self):
        *_, review_item = build_review_fixture()
        rejected = ReviewDecision(review_item.review_item_id, ReviewDecisionKind.REJECT, "operator:local")
        blocked = ReviewDecision(review_item.review_item_id, ReviewDecisionKind.BLOCK, "operator:local")
        self.assertTrue(validate_review_decision(rejected))
        self.assertTrue(validate_review_decision(blocked))

    def test_request_more_evidence_decision_records_status(self):
        *_, review_item = build_review_fixture()
        decision = ReviewDecision(review_item.review_item_id, ReviewDecisionKind.REQUEST_MORE_EVIDENCE, "operator:local")
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            store.record_decision(review_item.review_item_id, decision)
            self.assertEqual(ReviewQueueStatus.NEEDS_MORE_EVIDENCE, store.get_review_item(review_item.review_item_id).queue_status)

    def test_list_filters_and_summary_work(self):
        *_, review_item = build_review_fixture()
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            store.enqueue_review_item(review_item)
            self.assertEqual(1, len(store.list_review_items(status=ReviewQueueStatus.NEEDS_REVIEW)))
            self.assertEqual(1, len(store.list_review_items(subject_kind="evidence_candidate")))
            summary = store.summarize()
            self.assertEqual(1, summary.review_item_count)
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_serialized_review_item_contains_no_boundary_fields(self):
        *_, review_item = build_review_fixture()
        text = review_item.to_json()
        self.assertNotIn("truth_boundary", text)
        self.assertNotIn("product_boundary", text)

    def test_payload_with_public_truth_field_is_rejected(self):
        self.assertTrue(validate_no_public_truth_fields({"public_truth": True}))

    def test_decision_does_not_mutate_indexes(self):
        output = run_demo(":memory:", ":memory:", ":memory:")
        self.assertFalse(output["public_index_writes_enabled"])
        self.assertFalse(output["master_index_writes_enabled"])
        self.assertFalse(output["automatic_acceptance_enabled"])

    def test_store_layers_remain_separate(self):
        source_record, response, observation, normalized, cache_entry, evidence_record, _ = build_review_fixture()
        with SourceCacheStore.open(":memory:") as cache_store:
            cache_store.init()
            cache_store.write_source_record(source_record)
            cache_store.write_metadata_response(response)
            cache_store.write_source_observation(observation)
            cache_store.write_normalized_observation(normalized)
            cache_store.write_cache_entry(cache_entry)
            self.assertEqual(cache_entry.entry_id, cache_store.get_cache_entry(cache_entry.entry_id).entry_id)
        with EvidenceLedgerStore.open(":memory:") as ledger:
            ledger.init()
            ledger.write_evidence_candidate(evidence_record)
            self.assertEqual(evidence_record.evidence_id, ledger.get_evidence_candidate(evidence_record.evidence_id).evidence_id)

    def test_json_round_trip(self):
        *_, review_item = build_review_fixture()
        clone = ReviewItemRecord.from_json(review_item.to_json())
        self.assertEqual(json.loads(review_item.to_json()), json.loads(clone.to_json()))


if __name__ == "__main__":
    unittest.main()
