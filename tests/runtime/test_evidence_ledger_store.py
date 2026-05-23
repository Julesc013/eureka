import json
import tempfile
import unittest
from pathlib import Path

from runtime.evidence.ledger import (
    EvidenceCandidateRecord,
    EvidenceConflict,
    EvidenceEvent,
    EvidenceEventKind,
    EvidenceLedgerStore,
    EvidenceReviewStatus,
)
from runtime.evidence.ledger.validation import (
    validate_evidence_ledger_path,
    validate_no_public_truth_fields,
)
from runtime.source.cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source.observation import build_evidence_candidate
from scripts.demo_source_cache_store import build_demo_objects


def build_record():
    source_record, response, observation, normalized = build_demo_objects()
    candidate = build_evidence_candidate(normalized)
    cache_entry = build_cache_entry(source_record, response, observation, normalized, SourceCacheStatus.CACHED)
    record = EvidenceCandidateRecord.from_candidate(
        candidate,
        normalized_observation_id=normalized.normalized_observation_id,
        source_cache_entry_id=cache_entry.entry_id,
    )
    return source_record, response, observation, normalized, cache_entry, record


class EvidenceLedgerStoreTests(unittest.TestCase):
    def test_init_creates_schema(self):
        with EvidenceLedgerStore.open(":memory:") as store:
            applied = store.init()
            self.assertEqual(1, len(applied))
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_in_memory_store_works(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            self.assertEqual(record.evidence_id, store.get_evidence_candidate(record.evidence_id).evidence_id)

    def test_file_backed_tempdir_store_works(self):
        *_, record = build_record()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            with EvidenceLedgerStore.open(path) as store:
                store.init()
                store.write_evidence_candidate(record)
            with EvidenceLedgerStore.open(path) as store:
                store.init()
                self.assertIsNotNone(store.get_evidence_candidate(record.evidence_id))

    def test_invalid_db_path_is_rejected(self):
        self.assertTrue(validate_evidence_ledger_path("runtime/out.sqlite"))

    def test_hidden_private_roots_are_rejected(self):
        self.assertTrue(validate_evidence_ledger_path(".cache/evidence.sqlite"))

    def test_write_read_evidence_candidate(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            fetched = store.get_evidence_candidate(record.evidence_id)
            self.assertEqual(record.claim_kind, fetched.claim_kind)
            self.assertEqual(EvidenceReviewStatus.CANDIDATE, fetched.status)

    def test_append_list_evidence_event(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            event = EvidenceEvent(record.evidence_id, EvidenceEventKind.NOTE_ADDED, {"note": "one"})
            store.append_event(event)
            self.assertIn(event.event_id, [item.event_id for item in store.list_events(record.evidence_id)])

    def test_event_order_is_preserved(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            first = EvidenceEvent(record.evidence_id, EvidenceEventKind.NOTE_ADDED, {"order": 1})
            second = EvidenceEvent(record.evidence_id, EvidenceEventKind.NOTE_ADDED, {"order": 2})
            store.append_event(first)
            store.append_event(second)
            ids = [item.event_id for item in store.list_events(record.evidence_id)]
            self.assertLess(ids.index(first.event_id), ids.index(second.event_id))

    def test_source_cache_link_works(self):
        *_, cache_entry, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            store.link_source_cache_entry(record.evidence_id, cache_entry.entry_id)
            fetched = store.get_evidence_candidate(record.evidence_id)
            self.assertEqual(cache_entry.entry_id, fetched.source_cache_entry_id)

    def test_conflict_recording_works(self):
        *_, record = build_record()
        conflict = EvidenceConflict("conflict-1", record.evidence_id, "field_disagreement", {"field": "version"})
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            store.record_conflict(conflict)
            self.assertEqual(1, len(store.list_conflicts(record.evidence_id)))

    def test_review_status_can_be_set_explicitly(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            store.set_review_status(record.evidence_id, EvidenceReviewStatus.ACCEPTED, reason="explicit test status")
            fetched = store.get_evidence_candidate(record.evidence_id)
            self.assertEqual(EvidenceReviewStatus.ACCEPTED, fetched.status)

    def test_list_filters_work(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            by_source = store.list_evidence_candidates(source_id=record.source_id)
            by_status = store.list_evidence_candidates(status=EvidenceReviewStatus.CANDIDATE)
            by_claim = store.list_evidence_candidates(claim_kind=record.claim_kind)
            self.assertEqual(1, len(by_source))
            self.assertEqual(1, len(by_status))
            self.assertEqual(1, len(by_claim))

    def test_summarize_and_integrity(self):
        *_, record = build_record()
        with EvidenceLedgerStore.open(":memory:") as store:
            store.init()
            store.write_evidence_candidate(record)
            summary = store.summarize()
            self.assertEqual(1, summary.evidence_candidate_count)
            self.assertEqual("pass", store.check_integrity()["status"])

    def test_serialized_evidence_contains_no_boundary_fields(self):
        *_, record = build_record()
        text = record.to_json()
        self.assertNotIn("truth_boundary", text)
        self.assertNotIn("product_boundary", text)

    def test_payload_with_accepted_truth_field_is_rejected(self):
        self.assertTrue(validate_no_public_truth_fields({"accepted_truth": True}))

    def test_store_does_not_write_review_queue_or_indexes(self):
        from scripts.demo_evidence_ledger_store import run_demo

        output = run_demo(":memory:", ":memory:")
        self.assertFalse(output["review_queue_writes_enabled"])
        self.assertFalse(output["public_index_writes_enabled"])
        self.assertFalse(output["master_index_writes_enabled"])

    def test_source_cache_store_still_works_separately(self):
        source_record, response, observation, normalized, cache_entry, _ = build_record()
        with SourceCacheStore.open(":memory:") as store:
            store.init()
            store.write_source_record(source_record)
            store.write_metadata_response(response)
            store.write_source_observation(observation)
            store.write_normalized_observation(normalized)
            store.write_cache_entry(cache_entry)
            self.assertEqual(cache_entry.entry_id, store.get_cache_entry(cache_entry.entry_id).entry_id)


if __name__ == "__main__":
    unittest.main()
