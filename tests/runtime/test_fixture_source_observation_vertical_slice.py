import copy
import hashlib
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime.local.foundry.fixture_source_observation_slice import (
    ABSENCE_QUERY,
    POSITIVE_QUERY,
    REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION,
    SURFACE_SCHEMA_VERSION,
    absence_from_reviewed_index_artifact,
    get_reviewed_index_artifact_object,
    load_reviewed_index_artifact,
    run_fixture_source_observation_slice,
    search_reviewed_index_artifact,
    validate_reviewed_index_artifact,
    validate_fixture_slice_report,
)
from runtime.index.public import PublicIndexStore, rebuild_reviewed_public_index
from runtime.review.queue import ReviewDecisionKind
from scripts.demo_review_queue_store import run_demo as run_review_queue_demo


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixtureSourceObservationVerticalSliceTests(unittest.TestCase):
    def test_full_fixture_loop_produces_search_and_absence_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_fixture_source_observation_slice(Path(tmp))

        self.assertEqual("pass", report["status"])
        self.assertEqual([], validate_fixture_slice_report(report))
        self.assertTrue(report["source_observation"]["observation_id"].startswith("obs_"))
        self.assertTrue(report["normalized_observation"]["normalized_observation_id"].startswith("norm_"))
        self.assertTrue(report["evidence_candidate"]["candidate_id"].startswith("evc_"))
        self.assertEqual("accepted", report["review_decision"]["decision_status"])
        self.assertEqual(1, len(report["public_index_records"]))
        self.assertEqual(POSITIVE_QUERY, report["search"]["query"])
        self.assertEqual(1, report["search"]["result_count"])
        self.assertEqual("Demo Project", report["object_result"]["title"])
        self.assertEqual(ABSENCE_QUERY, report["absence"]["query"])
        self.assertEqual(0, report["absence"]["result_count"])
        self.assertEqual(SURFACE_SCHEMA_VERSION, report["surface_packets"]["schema_version"])
        self.assertEqual(
            REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION,
            report["persistent_reviewed_index"]["schema_version"],
        )

    def test_fixture_loop_runs_with_network_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(socket, "socket", side_effect=AssertionError("network disabled")):
                report = run_fixture_source_observation_slice(Path(tmp))
        self.assertEqual("pass", report["status"])

    def test_fixture_loop_uses_default_temp_root(self):
        report = run_fixture_source_observation_slice()
        self.assertEqual("pass", report["status"])
        self.assertTrue(report["no_live_no_mutation"]["fixture_store_root_isolated"])
        for path in report["paths"].values():
            self.assertNotIn("\\runtime\\", path.lower())
            self.assertNotIn("\\contracts\\", path.lower())
            self.assertTrue(Path(path).is_file())

    def test_fixture_ids_are_deterministic_across_runs(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            report_a = run_fixture_source_observation_slice(Path(first))
            report_b = run_fixture_source_observation_slice(Path(second))

        stable_paths = (
            ("metadata_request", "request_id"),
            ("metadata_response", "response_id"),
            ("source_observation", "observation_id"),
            ("normalized_observation", "normalized_observation_id"),
            ("source_cache_entry", "entry_id"),
            ("evidence_candidate", "candidate_id"),
            ("evidence_record", "evidence_id"),
            ("review_item", "review_item_id"),
            ("review_decision", "decision_id"),
            ("reviewed_index_candidate", "record_id"),
            ("search", "query"),
            ("absence", "query"),
        )
        for section, key in stable_paths:
            self.assertEqual(report_a[section][key], report_b[section][key], (section, key))
        self.assertEqual(report_a["search"]["results"][0]["record_id"], report_b["search"]["results"][0]["record_id"])
        self.assertEqual(report_a["surface_packets"], report_b["surface_packets"])
        self.assertEqual(
            report_a["persistent_reviewed_index"]["artifact"],
            report_b["persistent_reviewed_index"]["artifact"],
        )
        self.assertEqual(
            report_a["persistent_reviewed_index"]["artifact_file_sha256"],
            report_b["persistent_reviewed_index"]["artifact_file_sha256"],
        )

    def test_reviewed_index_artifact_is_persisted_and_rebuilds_byte_identically(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            report_a = run_fixture_source_observation_slice(Path(first))
            report_b = run_fixture_source_observation_slice(Path(second))
            artifact_a = Path(report_a["persistent_reviewed_index"]["artifact_path"])
            artifact_b = Path(report_b["persistent_reviewed_index"]["artifact_path"])

            self.assertTrue(artifact_a.is_file())
            self.assertTrue(artifact_b.is_file())
            self.assertEqual(artifact_a.read_bytes(), artifact_b.read_bytes())
            self.assertEqual(file_digest(artifact_a), report_a["persistent_reviewed_index"]["artifact_file_sha256"])
            self.assertEqual(file_digest(artifact_b), report_b["persistent_reviewed_index"]["artifact_file_sha256"])

    def test_reviewed_index_artifact_loads_and_serves_search_object_and_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_fixture_source_observation_slice(Path(tmp))
            artifact = load_reviewed_index_artifact(report["persistent_reviewed_index"]["artifact_path"])

        self.assertEqual([], validate_reviewed_index_artifact(artifact))
        search_packet = search_reviewed_index_artifact(artifact, POSITIVE_QUERY)
        self.assertEqual(1, search_packet["result_count"])
        self.assertEqual(report["object_result"]["record_id"], search_packet["results"][0]["object_id"])
        object_packet = get_reviewed_index_artifact_object(artifact, search_packet["results"][0]["object_id"])
        self.assertTrue(object_packet["found"])
        self.assertEqual(
            report["surface_packets"]["object_detail_packet"]["object_id"],
            object_packet["object_detail_packet"]["object_id"],
        )
        absence_packet = absence_from_reviewed_index_artifact(artifact, ABSENCE_QUERY)
        self.assertEqual(0, absence_packet["result_count"])
        self.assertEqual(REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION, artifact["schema_version"])
        self.assertFalse(artifact["production_public_index"])

    def test_reviewed_index_artifact_reports_missing_corrupt_and_nonaccepted_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = run_fixture_source_observation_slice(root / "stores")
            artifact = copy.deepcopy(report["persistent_reviewed_index"]["artifact"])

            with self.assertRaisesRegex(ValueError, "missing; rebuild fixture slice"):
                load_reviewed_index_artifact(root / "missing.json")

            corrupt = root / "corrupt.json"
            corrupt.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not valid JSON"):
                load_reviewed_index_artifact(corrupt)

            artifact["records"][0]["review_status"] = "needs_review"
            artifact["artifact_hash"] = "sha256:invalid"
            errors = validate_reviewed_index_artifact(artifact)
            self.assertIn("artifact records must be accepted before indexing", errors)
            with self.assertRaisesRegex(ValueError, "validation failed"):
                search_reviewed_index_artifact(artifact, POSITIVE_QUERY)

    def test_surface_packets_expose_result_object_evidence_source_and_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_fixture_source_observation_slice(Path(tmp))

        packets = report["surface_packets"]
        result_packet = packets["result_packet"]
        result = result_packet["results"][0]
        object_packet = packets["object_detail_packet"]
        evidence_packet = packets["evidence_summary_packet"]
        source_packet = packets["source_provenance_packet"]
        absence_packet = packets["absence_packet"]

        self.assertEqual(POSITIVE_QUERY, result_packet["query"])
        self.assertEqual(1, result_packet["result_count"])
        self.assertEqual("Demo Project", result["title"])
        self.assertEqual("fixture.demo-project", result["artifact_id"])
        self.assertEqual(report["evidence_record"]["evidence_id"], result["evidence_id"])
        self.assertEqual("accepted", result["review_status"])
        self.assertEqual(report["object_result"]["record_id"], object_packet["object_id"])
        self.assertEqual(report["evidence_record"]["evidence_id"], object_packet["refs"]["evidence_id"])
        self.assertEqual(report["review_decision"]["decision_id"], object_packet["refs"]["review_decision_id"])
        self.assertTrue(object_packet["local_only"])
        self.assertTrue(object_packet["fixture_only"])
        self.assertEqual(report["evidence_record"]["evidence_id"], evidence_packet["evidence_id"])
        self.assertTrue(evidence_packet["review"]["accepted_for_local_index"])
        self.assertEqual(report["source_record"]["id"], source_packet["source_id"])
        self.assertFalse(source_packet["no_live"]["network_calls"])
        self.assertEqual(ABSENCE_QUERY, absence_packet["query"])
        self.assertEqual(0, absence_packet["result_count"])
        self.assertIn(report["source_record"]["id"], absence_packet["checked_sources"])
        self.assertTrue(absence_packet["local_only"])
        self.assertTrue(absence_packet["fixture_only"])

    def test_no_live_no_mutation_flags_are_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_fixture_source_observation_slice(Path(tmp))
        proof = report["no_live_no_mutation"]
        for key in (
            "network_calls",
            "provider_model_calls",
            "live_source_probes",
            "crawling_downloading_scraping",
            "source_sync",
            "registry_mutation",
            "production_source_cache_writes",
            "production_evidence_ledger_writes",
            "production_public_index_writes",
            "site_deploy",
            "release_publish",
            "branch_mutation",
            "canonical_product_store_writes",
        ):
            self.assertFalse(proof[key], key)
        self.assertTrue(proof["fixture_store_root_isolated"])

    def test_product_output_roots_are_rejected(self):
        with self.assertRaises(ValueError):
            run_fixture_source_observation_slice("runtime/q58-fixture")

    def test_validate_report_rejects_mismatched_refs_and_mutation_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_fixture_source_observation_slice(Path(tmp))

        bad_report = copy.deepcopy(report)
        bad_report["object_result"]["evidence_id"] = "evc_wrong"
        bad_report["rebuild_report"]["master_index_mutated"] = True
        bad_report["no_live_no_mutation"]["network_calls"] = True
        bad_report["surface_packets"]["result_packet"]["results"][0]["review_status"] = "needs_review"
        bad_report["surface_packets"]["source_provenance_packet"]["no_live"]["network_calls"] = True

        errors = validate_fixture_slice_report(bad_report)
        self.assertIn("object result evidence ref does not match evidence record", errors)
        self.assertIn("rebuild report must prove master index was not mutated", errors)
        self.assertIn("no_live_no_mutation.network_calls must be False", errors)
        self.assertIn("result packet review status must be accepted", errors)
        self.assertIn("source provenance packet must prove no network calls", errors)

    def test_rejected_review_decision_is_not_indexed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_db = root / "source.sqlite"
            evidence_db = root / "evidence.sqlite"
            review_db = root / "review.sqlite"
            public_db = root / "public.sqlite"
            run_review_queue_demo(source_db, evidence_db, review_db, decision_kind=ReviewDecisionKind.REJECT)

            input_digests_before = (file_digest(source_db), file_digest(evidence_db), file_digest(review_db))
            report = rebuild_reviewed_public_index(source_db, evidence_db, review_db, public_db, dry_run=False)
            input_digests_after = (file_digest(source_db), file_digest(evidence_db), file_digest(review_db))

            self.assertEqual(0, report["included_count"])
            self.assertEqual(1, report["excluded_count"])
            self.assertFalse(report["input_stores_mutated"])
            self.assertFalse(report["master_index_mutated"])
            self.assertEqual(input_digests_before, input_digests_after)
            with PublicIndexStore.open(public_db) as store:
                store.init()
                self.assertEqual(0, store.summarize().record_count)


if __name__ == "__main__":
    unittest.main()
