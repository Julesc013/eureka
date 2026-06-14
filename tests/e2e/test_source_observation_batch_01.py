from __future__ import annotations

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


class SourceObservationBatch01Tests(unittest.TestCase):
    def test_batch_observations_materialize_one_reviewed_artifact_and_keep_launch_blocked(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.collection_path = demo.root / "source-observation-batch-01"
            demo.write_source_plan_and_template()
            source_url_list = [_firefox_system_requirements_url(demo), _firefox_release_notes_url(demo), _ct1740_source_lead_url(demo)]
            _write_jsonl(demo.collection_path / "source_url_list.jsonl", source_url_list)
            observations = [_firefox_system_requirements_observation(demo), _firefox_release_notes_observation(demo), _ct1740_source_lead_observation(demo)]
            _write_jsonl(demo.root / "batch_01_observations.jsonl", observations)
            protected_before = {
                "seed_report": _sha256(demo.seed_gate_path / "artifact_gate_report.json"),
                "candidate_plan": _sha256(demo.batch_path / "candidate_plan.jsonl"),
            }

            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.root / "batch_01_observations.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            source_report = _run_artifact_gate_main(
                "source-report",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "source_collection_report.json"),
                "--json",
            )
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_01",
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
            packets = read_jsonl(demo.collection_path / "manual_evidence_packets.jsonl")
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")
            source_payload = json.loads(source_report.stdout)
            manual_payload = json.loads(manual_report.stdout)
            launch_report = _load_json(demo.launch_gate_path / "launch_gate_report.json")
            protected_after = {
                "seed_report": _sha256(demo.seed_gate_path / "artifact_gate_report.json"),
                "candidate_plan": _sha256(demo.batch_path / "candidate_plan.jsonl"),
            }

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 3)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["evidence_packet_count"], 2)
        self.assertEqual(source_payload["status"], "PASS")
        self.assertEqual(source_payload["artifact_verified_packet_count"], 1)
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 1)
        self.assertEqual(manual_payload["reviewed_artifact_gate_count"], 1)
        self.assertEqual(manual_payload["gate_status"], "blocked")
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 1)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")
        self.assertEqual(len(source_url_list), 3)
        firefox_packet = next(packet for packet in packets if packet.get("artifact_title") == "Firefox ESR 52.9.0")
        ct1740_packet = next(packet for packet in packets if packet.get("artifact_title") == "Sound Blaster 16 CT1740")
        self.assertTrue(firefox_packet["artifact_verified"])
        self.assertTrue(firefox_packet["gate_eligible"])
        self.assertFalse(ct1740_packet["artifact_verified"])
        self.assertFalse(ct1740_packet["gate_eligible"])
        self.assertEqual(records[0]["title"], "Firefox ESR 52.9.0")
        self.assertFalse(records[0]["binary_verified"])
        self.assertFalse(records[0]["download_safe"])
        self.assertFalse(records[0]["execution_safe"])
        self.assertFalse(records[0]["rights_cleared"])
        self.assertEqual(protected_before, protected_after)


def _firefox_candidate(demo: _SourceCollectionDemo) -> dict[str, object]:
    return _find_candidate(read_jsonl(demo.collection_path / "source_candidate_plan.jsonl"), "firefox")


def _ct1740_candidate(demo: _SourceCollectionDemo) -> dict[str, object]:
    return _find_candidate(read_jsonl(demo.collection_path / "source_candidate_plan.jsonl"), "ct1740")


def _firefox_system_requirements_url(demo: _SourceCollectionDemo) -> dict[str, object]:
    return {
        "artifact_title": "Firefox ESR 52.9.0",
        "candidate_id": _firefox_candidate(demo)["candidate_id"],
        "collection_id": "source-collection:source-observation-batch-01",
        "expected_fields": ["product", "version", "channel", "windows_xp_support"],
        "forbidden_actions": ["download binaries", "fetch files", "replay Wayback"],
        "notes": "Official Firefox system requirements page; page observation only.",
        "source_authority": "primary",
        "source_identifier": "Firefox ESR 52.9.0 system requirements",
        "source_type": "official_support_page",
        "source_url": "https://www.firefox.com/en-US/firefox/52.9.0/system-requirements/",
    }


def _firefox_release_notes_url(demo: _SourceCollectionDemo) -> dict[str, object]:
    return {
        "artifact_title": "Firefox ESR 52.9.0",
        "candidate_id": _firefox_candidate(demo)["candidate_id"],
        "collection_id": "source-collection:source-observation-batch-01",
        "expected_fields": ["product", "version", "channel", "release_date"],
        "forbidden_actions": ["download binaries", "fetch files", "replay Wayback"],
        "notes": "Official Firefox release notes page; page observation only.",
        "source_authority": "primary",
        "source_identifier": "Firefox ESR 52.9.0 release notes",
        "source_type": "official_release_notes",
        "source_url": "https://www.firefox.com/en-US/firefox/52.9.0/releasenotes/",
    }


def _ct1740_source_lead_url(demo: _SourceCollectionDemo) -> dict[str, object]:
    return {
        "artifact_title": "Sound Blaster 16 CT1740",
        "candidate_id": _ct1740_candidate(demo)["candidate_id"],
        "collection_id": "source-collection:source-observation-batch-01",
        "expected_fields": ["model", "card_family", "hardware_characteristics"],
        "forbidden_actions": ["download binaries", "download drivers", "fetch files", "replay Wayback"],
        "notes": "Secondary retro hardware page; source lead only.",
        "source_authority": "reputable_secondary",
        "source_identifier": "Phil's Computer Lab CT1740 page",
        "source_type": "reputable_secondary_reference",
        "source_url": "https://www.philscomputerlab.com/ct1740.html",
    }


def _firefox_system_requirements_observation(demo: _SourceCollectionDemo) -> dict[str, object]:
    candidate_id = _firefox_candidate(demo)["candidate_id"]
    return {
        "access_method": "bounded_page_observation",
        "artifact_identity_fields": {
            "channel": "ESR",
            "platform_or_context": "Windows XP",
            "product": "Firefox ESR",
            "title": "Firefox ESR 52.9.0",
            "version": "52.9.0",
            "windows_xp_minimum": "Windows XP SP2",
        },
        "artifact_title": "Firefox ESR 52.9.0",
        "artifact_type": "software",
        "candidate_id": candidate_id,
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-01",
        "confidence": "high",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "live_network_used": True,
        "no_download_performed": True,
        "observation_notes": "Official Firefox requirements identify Firefox ESR 52.9.0 and Windows XP SP2 support.",
        "observed_artifact_fields": ["product", "version", "channel", "windows_xp_sp2_support"],
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_01",
        "platform_or_context": "Windows XP",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "Mozilla / Firefox",
        "review_rationale": "Primary Firefox support metadata identifies a concrete Firefox ESR 52.9.0 artifact and XP support posture.",
        "reviewer": "source_observation_batch_01",
        "schema_version": "eureka.artifact_source_observation.v0",
        "short_evidence_summary": "Official Firefox requirements identify Firefox ESR 52.9.0 and Windows XP SP2 support.",
        "source_authority": "primary",
        "source_id": "firefox-52-9-system-requirements",
        "source_identifier": "Firefox ESR 52.9.0 system requirements",
        "source_observation_id": "source-observation-batch-01:firefox-52-9-system-requirements",
        "source_title": "Firefox ESR 52.9.0 System Requirements",
        "source_type": "official_support_page",
        "source_url": "https://www.firefox.com/en-US/firefox/52.9.0/system-requirements/",
        "wayback_replay_used": False,
    }


def _firefox_release_notes_observation(demo: _SourceCollectionDemo) -> dict[str, object]:
    observation = _firefox_system_requirements_observation(demo)
    observation.update(
        {
            "artifact_identity_fields": {
                "channel": "ESR",
                "platform_or_context": "Windows XP",
                "product": "Firefox ESR",
                "release_date": "2018-06-26",
                "title": "Firefox ESR 52.9.0",
                "version": "52.9.0",
            },
            "observation_notes": "Official Firefox release notes identify 52.9.0 Firefox ESR and its June 26, 2018 ESR release date.",
            "observed_artifact_fields": ["product", "version", "channel", "release_date"],
            "review_rationale": "Primary Firefox release notes corroborate Firefox ESR 52.9.0 artifact identity, channel, and release date.",
            "short_evidence_summary": "Official Firefox release notes identify Firefox ESR 52.9.0 and its June 26, 2018 release date.",
            "source_id": "firefox-52-9-release-notes",
            "source_identifier": "Firefox ESR 52.9.0 release notes",
            "source_observation_id": "source-observation-batch-01:firefox-52-9-release-notes",
            "source_title": "Firefox ESR 52.9.0 Release Notes",
            "source_type": "official_release_notes",
            "source_url": "https://www.firefox.com/en-US/firefox/52.9.0/releasenotes/",
        }
    )
    return observation


def _ct1740_source_lead_observation(demo: _SourceCollectionDemo) -> dict[str, object]:
    return {
        "access_method": "bounded_page_observation",
        "artifact_identity_fields": {
            "card_family": "Sound Blaster 16",
            "dsp_version": "4.05",
            "model": "CT1740",
            "platform_or_context": "Sound Blaster CT1740",
            "title": "Sound Blaster 16 CT1740",
        },
        "artifact_title": "Sound Blaster 16 CT1740",
        "artifact_type": "hardware_reference",
        "candidate_id": _ct1740_candidate(demo)["candidate_id"],
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-01",
        "confidence": "medium",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "limitations": ["secondary source lead only", "does not verify a manual artifact"],
        "live_network_used": True,
        "no_download_performed": True,
        "observation_notes": "Secondary page identifies Sound Blaster 16 CT1740 hardware details; no linked downloads are fetched.",
        "observed_artifact_fields": ["model", "card_family", "hardware_characteristics"],
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_01",
        "platform_or_context": "Sound Blaster CT1740",
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "publisher_or_source_name": "Phil's Computer Lab",
        "review_rationale": "Secondary hardware page supports a CT1740 source lead but does not verify the requested manual artifact.",
        "reviewer": "source_observation_batch_01",
        "schema_version": "eureka.artifact_source_observation.v0",
        "short_evidence_summary": "Secondary CT1740 page identifies Sound Blaster 16 CT1740 hardware details as a source lead.",
        "source_authority": "reputable_secondary",
        "source_id": "philscomputerlab-ct1740",
        "source_identifier": "Phil's Computer Lab CT1740 page",
        "source_observation_id": "source-observation-batch-01:ct1740-philscomputerlab",
        "source_title": "Sound Blaster 16 CT1740",
        "source_type": "reputable_secondary_reference",
        "source_url": "https://www.philscomputerlab.com/ct1740.html",
        "wayback_replay_used": False,
    }


if __name__ == "__main__":
    unittest.main()
