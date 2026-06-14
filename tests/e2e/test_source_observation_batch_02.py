from __future__ import annotations

from copy import deepcopy
import json
import unittest

from runtime.local.artifact_gate_seed import read_jsonl
from tests.e2e.test_artifact_evidence_source_collection import (
    _SourceCollectionDemo,
    _find_candidate,
    _load_json,
    _run_artifact_gate_main,
    _run_launch_gate_main,
    _sha256,
    _write_jsonl,
    _write_staging_and_rehearsal,
)
from tests.e2e.test_source_observation_batch_01 import (
    _ct1740_source_lead_observation,
    _firefox_release_notes_observation,
    _firefox_system_requirements_observation,
)


class SourceObservationBatch02Tests(unittest.TestCase):
    def test_batch02_adds_new_manual_identity_without_recounting_batch01(self) -> None:
        with _SourceCollectionDemo() as demo:
            batch01_path = demo.root / "source-observation-batch-01"
            demo.collection_path = batch01_path
            demo.write_source_plan_and_template()
            batch01_observations = [
                _firefox_system_requirements_observation(demo),
                _firefox_release_notes_observation(demo),
                _ct1740_source_lead_observation(demo),
            ]
            _write_jsonl(batch01_path / "source_observations_input.jsonl", batch01_observations)
            _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch01_path),
                "--observations",
                str(batch01_path / "source_observations_input.jsonl"),
            )
            _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch01_path),
                "--out",
                str(batch01_path / "manual_evidence_packets.jsonl"),
            )

            batch02_path = demo.root / "source-observation-batch-02"
            demo.collection_path = batch02_path
            demo.write_source_plan_and_template()
            _write_jsonl(batch02_path / "source_observations_input.jsonl", _batch02_observations(demo))
            protected_before = {
                "seed_report": _sha256(demo.seed_gate_path / "artifact_gate_report.json"),
                "candidate_plan": _sha256(demo.batch_path / "candidate_plan.jsonl"),
            }
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch02_path),
                "--observations",
                str(batch02_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch02_path),
                "--out",
                str(batch02_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            source_report = _run_artifact_gate_main(
                "source-report",
                "--collection",
                str(batch02_path),
                "--out",
                str(batch02_path / "source_collection_report.json"),
                "--json",
            )
            cumulative_packets = read_jsonl(batch01_path / "manual_evidence_packets.jsonl") + read_jsonl(
                batch02_path / "manual_evidence_packets.jsonl"
            )
            _write_jsonl(batch02_path / "manual_evidence_packets.cumulative.jsonl", cumulative_packets)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch02_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_02",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )
            manual_report = _run_artifact_gate_main(
                "manual-report",
                "--batch",
                str(demo.batch_path),
                "--out",
                str(demo.batch_path / "artifact_gate_report.json"),
                "--json",
            )
            _write_staging_and_rehearsal(demo)
            launch = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--artifact-gate-report",
                str(demo.batch_path / "artifact_gate_report.json"),
                "--out",
                str(demo.launch_gate_path),
            )
            batch02_packets = read_jsonl(batch02_path / "manual_evidence_packets.jsonl")
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")
            manual_payload = json.loads(manual_report.stdout)
            launch_report = _load_json(demo.launch_gate_path / "launch_gate_report.json")
            protected_after = {
                "seed_report": _sha256(demo.seed_gate_path / "artifact_gate_report.json"),
                "candidate_plan": _sha256(demo.batch_path / "candidate_plan.jsonl"),
            }

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 3)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["evidence_packet_count"], 1)
        self.assertEqual(json.loads(source_report.stdout)["artifact_verified_packet_count"], 1)
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 3)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        review_payload = json.loads(manual_review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 2)
        self.assertEqual(review_payload["rejected_or_non_eligible_count"], 1)
        self.assertEqual(manual_payload["reviewed_artifact_gate_count"], 2)
        self.assertEqual(manual_payload["gate_status"], "blocked")
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 2)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")
        self.assertEqual(len(batch02_packets), 1)
        batch02_packet = batch02_packets[0]
        self.assertEqual(batch02_packet["artifact_title"], "Creative Labs Sound Blaster 16 manual")
        self.assertTrue(batch02_packet["artifact_verified"])
        self.assertTrue(batch02_packet["gate_eligible"])
        self.assertTrue(any(item.get("duplicate_check_result") for item in batch02_packet["source_observations"]))
        titles = {record["title"] for record in records}
        self.assertEqual(titles, {"Firefox ESR 52.9.0", "Creative Labs Sound Blaster 16 manual"})
        self.assertEqual(len({record["dedupe_identity_key"] for record in records}), 2)
        self.assertTrue(all(record["artifact_verified"] for record in records))
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(protected_before, protected_after)

    def test_duplicate_firefox_identity_is_rejected_by_manual_review(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.collection_path = demo.root / "source-observation-batch-01"
            demo.write_source_plan_and_template()
            observations = [
                _firefox_system_requirements_observation(demo),
                _firefox_release_notes_observation(demo),
            ]
            _write_jsonl(demo.collection_path / "source_observations_input.jsonl", observations)
            _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.collection_path / "source_observations_input.jsonl"),
            )
            _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
            )
            firefox_packet = read_jsonl(demo.collection_path / "manual_evidence_packets.jsonl")[0]
            duplicate_packet = deepcopy(firefox_packet)
            duplicate_packet["evidence_packet_id"] = "source-derived-evidence:duplicate-firefox-esr-52-9"
            _write_jsonl(demo.root / "duplicate_firefox_packets.jsonl", [firefox_packet, duplicate_packet])
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "duplicate_firefox_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_02",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )
            report = _run_artifact_gate_main(
                "manual-report",
                "--batch",
                str(demo.batch_path),
                "--out",
                str(demo.batch_path / "artifact_gate_report.json"),
                "--json",
            )
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")
            review_payload = json.loads(review.stdout)

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 2)
        self.assertEqual(review.code, 0, review.stderr)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 1)
        self.assertEqual(review_payload["artifact_verified_count"], 1)
        self.assertEqual(review_payload["rejected_or_non_eligible_count"], 1)
        duplicate = review_payload["rejected_or_non_eligible"][0]
        self.assertEqual(duplicate["status"], "duplicate")
        self.assertEqual(duplicate["gate_exclusion_reason"], "duplicate_artifact_identity")
        self.assertEqual(duplicate["duplicate_of"], records[0]["reviewed_artifact_record_id"])
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 1)


def _ct1740_candidate(demo: _SourceCollectionDemo) -> dict[str, object]:
    return _find_candidate(read_jsonl(demo.collection_path / "source_candidate_plan.jsonl"), "ct1740")


def _batch02_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    candidate = _ct1740_candidate(demo)
    candidate_id = candidate["candidate_id"]
    base = {
        "access_method": "bounded_page_observation",
        "artifact_title": "Creative Labs Sound Blaster 16 manual",
        "artifact_type": "manual",
        "candidate_id": candidate_id,
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-02",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": True,
        "no_download_performed": True,
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_02",
        "platform_or_context": "Sound Blaster 16 CT1740",
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "",
        "reviewer": "source_observation_batch_02",
        "schema_version": "eureka.artifact_source_observation.v0",
        "wayback_replay_used": False,
    }
    archive = {
        **base,
        "artifact_identity_fields": {
            "creator": "Creative Labs",
            "identifier": "creativelabssoundblaster16manual",
            "platform_or_context": "Sound Blaster 16 CT1740",
            "publication_date": "1995",
            "title": "Creative Labs Sound Blaster 16 manual",
        },
        "confidence": "medium",
        "duplicate_check_result": "new_identity_source_lead",
        "limitations": ["archive metadata page only", "archive metadata cannot verify an artifact by itself"],
        "observation_notes": "Internet Archive metadata identifies a Creative Labs Sound Blaster 16 manual entry.",
        "observed_artifact_fields": ["title", "creator", "publication_date", "identifier", "manual_description"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "metadata_only",
        "publisher_or_source_name": "Internet Archive",
        "review_rationale": "Archive metadata is retained as a source lead and requires independent corroboration.",
        "short_evidence_summary": "Archive metadata identifies a Creative Labs Sound Blaster 16 manual.",
        "source_authority": "archive_metadata",
        "source_id": "ia-creativelabssoundblaster16manual",
        "source_identifier": "creativelabssoundblaster16manual",
        "source_observation_id": "source-observation-batch-02:ia-sound-blaster-16-manual",
        "source_title": "Creative Labs Sound Blaster 16 manual",
        "source_type": "archive_metadata_page",
        "source_url": "https://archive.example.invalid/details/creativelabssoundblaster16manual",
    }
    catalog = {
        **base,
        "artifact_identity_fields": {
            "asin": "B001INAWGK",
            "author": "Creative Labs",
            "format": "paperback",
            "platform_or_context": "Sound Blaster 16 CT1740",
            "publication_date": "1994-01-01",
            "publisher": "Creative Labs",
            "title": "Creative Labs Sound Blaster 16 manual",
        },
        "confidence": "high",
        "duplicate_check_result": "new_identity_corroboration",
        "limitations": ["catalog page only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "Stable catalog metadata identifies a Sound Blaster 16 User's Guide by Creative Labs.",
        "observed_artifact_fields": ["title", "author", "publisher", "publication_date", "language", "asin"],
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "publisher_or_source_name": "Amazon catalog",
        "review_rationale": "Independent catalog metadata corroborates the Creative Labs Sound Blaster 16 manual identity.",
        "short_evidence_summary": "Catalog metadata corroborates a Creative Labs Sound Blaster 16 manual/user guide.",
        "source_authority": "stable_catalog",
        "source_id": "amazon-sound-blaster-16-users-guide",
        "source_identifier": "ASIN B001INAWGK",
        "source_observation_id": "source-observation-batch-02:amazon-sound-blaster-16-users-guide",
        "source_title": "Sound Blaster 16 User's Guide",
        "source_type": "stable_catalog_page",
        "source_url": "https://catalog.example.invalid/Sound-Blaster-16-Users-Guide/dp/B001INAWGK",
    }
    hardware_context = {
        **base,
        "artifact_identity_fields": {
            "bus": "ISA 16-bit",
            "card_family": "Sound Blaster 16",
            "model": "CT1740",
            "platform_or_context": "Sound Blaster 16 CT1740",
            "title": "Creative Labs Sound Blaster 16 manual",
        },
        "confidence": "medium",
        "duplicate_check_result": "new_identity_platform_context",
        "limitations": ["secondary hardware reference only", "does not verify a manual artifact by itself"],
        "observation_notes": "Secondary hardware reference identifies the CT1740 as an early Sound Blaster 16 ISA card.",
        "observed_artifact_fields": ["model", "card_family", "release_date", "bus", "hardware_context"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "publisher_or_source_name": "DOSDays",
        "review_rationale": "Hardware context supports the CT1740 identity but is not manual verification on its own.",
        "short_evidence_summary": "DOSDays identifies Sound Blaster 16 CT1740 hardware context.",
        "source_authority": "reputable_secondary",
        "source_id": "dosdays-creative-ct1740",
        "source_identifier": "DOSDays CT1740 page",
        "source_observation_id": "source-observation-batch-02:dosdays-ct1740",
        "source_title": "Sound Blaster 16 CT1740",
        "source_type": "reputable_secondary_reference",
        "source_url": "https://reference.example.invalid/topics/creative/ct1740.php",
    }
    return [archive, catalog, hardware_context]


if __name__ == "__main__":
    unittest.main()
