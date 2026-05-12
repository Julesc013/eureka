import hashlib
import tempfile
import unittest
from pathlib import Path

from runtime.public_index import PublicIndexStore, rebuild_reviewed_public_index
from runtime.review_queue import ReviewDecisionKind
from scripts.demo_review_queue_store import run_demo as run_review_queue_demo


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PublicIndexRebuildTests(unittest.TestCase):
    def make_inputs(self, tmp: str, decision_kind: ReviewDecisionKind = ReviewDecisionKind.ACCEPT):
        root = Path(tmp)
        source_db = root / "source.sqlite"
        evidence_db = root / "evidence.sqlite"
        review_db = root / "review.sqlite"
        public_db = root / "public.sqlite"
        run_review_queue_demo(source_db, evidence_db, review_db, decision_kind=decision_kind)
        return source_db, evidence_db, review_db, public_db

    def test_rebuild_includes_accepted_local_review_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_db, evidence_db, review_db, public_db = self.make_inputs(tmp)
            report = rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=False)
            self.assertEqual(1, report["included_count"])
            with PublicIndexStore.open(public_db) as store:
                store.init()
                self.assertEqual(1, store.summarize().record_count)

    def test_rebuild_excludes_rejected_decision(self):
        self.assert_excluded(ReviewDecisionKind.REJECT)

    def test_rebuild_excludes_blocked_decision(self):
        self.assert_excluded(ReviewDecisionKind.BLOCK)

    def test_rebuild_excludes_superseded_decision(self):
        self.assert_excluded(ReviewDecisionKind.SUPERSEDE)

    def test_rebuild_excludes_needs_review_decision(self):
        self.assert_excluded(ReviewDecisionKind.NOTE_ONLY)

    def test_rebuild_preserves_evidence_source_cache_and_review_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_db, evidence_db, review_db, public_db = self.make_inputs(tmp)
            rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=False)
            with PublicIndexStore.open(public_db) as store:
                store.init()
                record = store.list_records()[0]
                self.assertTrue(record.evidence_id)
                self.assertTrue(record.source_cache_entry_id)
                self.assertTrue(record.review_item_id)
                self.assertTrue(record.review_decision_id)

    def test_rebuild_does_not_mutate_input_dbs(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_db, evidence_db, review_db, public_db = self.make_inputs(tmp)
            before = (digest(source_db), digest(evidence_db), digest(review_db))
            rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=False)
            after = (digest(source_db), digest(evidence_db), digest(review_db))
            self.assertEqual(before, after)

    def test_dry_run_does_not_write_public_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_db, evidence_db, review_db, public_db = self.make_inputs(tmp)
            report = rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=True)
            self.assertEqual("dry_run", report["status"])
            self.assertFalse(public_db.exists())

    def assert_excluded(self, decision_kind: ReviewDecisionKind):
        with tempfile.TemporaryDirectory() as tmp:
            source_db, evidence_db, review_db, public_db = self.make_inputs(tmp, decision_kind)
            report = rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=True)
            self.assertEqual(0, report["included_count"])


if __name__ == "__main__":
    unittest.main()
