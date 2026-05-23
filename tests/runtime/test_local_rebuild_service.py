import hashlib
import tempfile
import unittest
from pathlib import Path

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.review import rebuild_reviewed_index, record_review_decision
from scripts.eureka_init_instance import initialize_instance
from scripts.validate_local_review_rebuild import seed_review_records


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LocalRebuildServiceTests(unittest.TestCase):
    def test_rebuild_includes_accepted_and_excludes_rejected_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                seed = seed_review_records(runtime)
                record_review_decision(runtime, seed["accepted_review_item_id"], "accept", None, "operator", True)
                record_review_decision(runtime, seed["rejected_review_item_id"], "reject", "not enough support", "operator", False)
                record_review_decision(runtime, seed["blocked_review_item_id"], "block", "blocked locally", "operator", False)
                result = rebuild_reviewed_index(runtime, "operator", dry_run=False)
                search = runtime.public_index.search("local08 accepted artifact", limit=10)
            finally:
                close_local_appliance(runtime)

        excluded_ids = {item["review_item_id"] for item in result["excluded"]}
        self.assertEqual(1, result["included_count"])
        self.assertIn(seed["rejected_review_item_id"], excluded_ids)
        self.assertIn(seed["blocked_review_item_id"], excluded_ids)
        self.assertEqual(1, len(search))

    def test_rebuild_does_not_mutate_input_stores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                seed = seed_review_records(runtime)
                record_review_decision(runtime, seed["accepted_review_item_id"], "accept", None, "operator", True)
            finally:
                close_local_appliance(runtime)
            source_db = instance / "db" / "source_cache.sqlite"
            evidence_db = instance / "db" / "evidence_ledger.sqlite"
            review_db = instance / "db" / "review_queue.sqlite"
            before = (digest(source_db), digest(evidence_db), digest(review_db))
            runtime = open_local_appliance(instance)
            try:
                rebuild_reviewed_index(runtime, "operator", dry_run=False)
            finally:
                close_local_appliance(runtime)
            after = (digest(source_db), digest(evidence_db), digest(review_db))

        self.assertEqual(before, after)

    def test_dry_run_does_not_add_public_index_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                seed = seed_review_records(runtime)
                record_review_decision(runtime, seed["accepted_review_item_id"], "accept", None, "operator", True)
                result = rebuild_reviewed_index(runtime, "operator", dry_run=True)
                summary = runtime.public_index.summarize()
            finally:
                close_local_appliance(runtime)

        self.assertTrue(result["dry_run"])
        self.assertEqual(0, summary.record_count)


if __name__ == "__main__":
    unittest.main()
