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
    _write_jsonl,
    _write_staging_and_rehearsal,
)
from tests.e2e.test_source_observation_batch_05 import (
    _batch05_curated_observations,
    _seed_manual_gate_through_batch04,
)


class SourceObservationBatch06Tests(unittest.TestCase):
    def test_batch06_uses_next_curated_targets_after_batch05_identities_are_duplicates(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch05(demo)

            batch06_path = demo.root / "source-observation-batch-06"
            demo.collection_path = batch06_path
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch06_path),
                "--target-records",
                "5",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch06_path),
                "--out",
                str(batch06_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch06_path / "source_candidate_plan.jsonl")
            _write_jsonl(batch06_path / "source_observations_input.jsonl", _batch06_curated_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch06_path),
                "--observations",
                str(batch06_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch06_path),
                "--out",
                str(batch06_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch06_packets = read_jsonl(batch06_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch06_packets
            _write_jsonl(batch06_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch06_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_06",
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
            source_report = _run_artifact_gate_main(
                "source-report",
                "--collection",
                str(batch06_path),
                "--out",
                str(batch06_path / "source_collection_report.json"),
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
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")
            launch_report = _load_json(demo.launch_gate_path / "launch_gate_report.json")

        self.assertEqual(plan.code, 0, plan.stderr)
        plan_payload = json.loads(plan.stdout)
        self.assertEqual(plan_payload["selected_candidate_count"], 2)
        self.assertEqual(plan_payload["curated_candidate_count"], 6)
        self.assertGreaterEqual(plan_payload["duplicate_candidate_count"], 9)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 2)
        targets = [row for row in plan_rows if row.get("source_collection_target") is True]
        self.assertEqual(
            {row["candidate_id"] for row in targets},
            {
                "artifact-gate-curated:vlc-3-0-20-windows",
                "artifact-gate-curated:gimp-2-10-38-windows",
            },
        )
        self.assertTrue(all(row.get("curated_source_collection_target") is True for row in targets))
        self.assertTrue(_find_candidate(plan_rows, "7-zip 19.00")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "winscp 5.21.8")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "putty 0.78")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "audacity 3.2.5")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "firefox")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "source evidence for article")["source_collection_duplicate"])
        self.assertFalse(_find_candidate(plan_rows, "windows 7 apps")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "driver for win98")["source_collection_target"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 5)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 2)
        self.assertEqual({packet["artifact_title"] for packet in batch06_packets}, {"VLC 3.0.20 Vetinari", "GIMP 2.10.38 for Windows"})
        self.assertTrue(all(packet["artifact_verified"] for packet in batch06_packets))
        self.assertTrue(all(packet["binary_verified"] is False for packet in batch06_packets))
        self.assertTrue(all(packet["download_safe"] is False for packet in batch06_packets))
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 10)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 9)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 9)
        self.assertEqual(json.loads(manual_report.stdout)["gate_status"], "blocked")
        self.assertEqual(json.loads(source_report.stdout)["artifact_verified_packet_count"], 2)
        self.assertEqual(
            {record["title"] for record in records},
            {
                "Firefox ESR 52.9.0",
                "Creative Labs Sound Blaster 16 manual",
                "Mike Miller's Many Hats",
                "7-Zip 19.00 for Windows",
                "WinSCP 5.21.8",
                "PuTTY 0.78 for Windows",
                "Audacity 3.2.5 for Windows",
                "VLC 3.0.20 Vetinari",
                "GIMP 2.10.38 for Windows",
            },
        )
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 9)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_duplicate_batch05_curated_identities_cannot_increment_gate_count(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch05(demo)
            batch05_packets = [
                packet
                for packet in cumulative
                if packet.get("artifact_title") in {"PuTTY 0.78 for Windows", "Audacity 3.2.5 for Windows"}
            ]
            duplicates = []
            for packet in batch05_packets:
                duplicate = deepcopy(packet)
                duplicate["evidence_packet_id"] = f"{packet['evidence_packet_id']}:duplicate"
                duplicates.append(duplicate)
            _write_jsonl(demo.root / "duplicate_batch05_packets.jsonl", cumulative + duplicates)
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "duplicate_batch05_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_06",
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

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 10)
        self.assertEqual(review.code, 0, review.stderr)
        review_payload = json.loads(review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 7)
        duplicate_results = [item for item in review_payload["rejected_or_non_eligible"] if item.get("status") == "duplicate"]
        self.assertEqual(len(duplicate_results), 2)
        self.assertTrue(all(item["gate_exclusion_reason"] == "duplicate_artifact_identity" for item in duplicate_results))
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 7)


def _seed_manual_gate_through_batch05(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    cumulative = _seed_manual_gate_through_batch04(demo)
    batch05_path = demo.root / "source-observation-batch-05"
    demo.collection_path = batch05_path
    _run_artifact_gate_main("source-plan", "--gate", str(demo.seed_gate_path), "--manual-batch", str(demo.batch_path), "--out", str(batch05_path), "--target-records", "5")
    _run_artifact_gate_main("source-template", "--collection", str(batch05_path), "--out", str(batch05_path / "source_observation_template.jsonl"))
    _write_jsonl(batch05_path / "source_observations_input.jsonl", _batch05_curated_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch05_path), "--observations", str(batch05_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch05_path), "--out", str(batch05_path / "manual_evidence_packets.jsonl"))
    cumulative = cumulative + read_jsonl(batch05_path / "manual_evidence_packets.jsonl")
    _write_jsonl(batch05_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(batch05_path / "manual_evidence_packets.cumulative.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_05",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
    return cumulative


def _batch06_curated_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
    vlc_id = next(row["candidate_id"] for row in plan_rows if row.get("candidate_id") == "artifact-gate-curated:vlc-3-0-20-windows")
    gimp_id = next(row["candidate_id"] for row in plan_rows if row.get("candidate_id") == "artifact-gate-curated:gimp-2-10-38-windows")
    base = {
        "access_method": "bounded_page_observation",
        "batch_id": "source-observation-batch-06",
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-06",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_06",
        "reviewer": "source_observation_batch_06",
        "schema_version": "eureka.artifact_source_observation.v0",
        "source_authority": "primary",
        "wayback_replay_used": False,
    }
    vlc_primary = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows media player",
            "product": "VLC media player",
            "publisher_or_project": "VideoLAN",
            "release_branch": "Vetinari",
            "release_date_or_period": "November 2023",
            "title": "VLC 3.0.20 Vetinari",
            "version": "3.0.20",
        },
        "artifact_title": "VLC 3.0.20 Vetinari",
        "artifact_type": "software",
        "candidate_id": vlc_id,
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "Official VideoLAN release page identifies VLC 3.0.20 Vetinari and Windows-related release context.",
        "observed_artifact_fields": ["product", "version", "release_branch", "release_notes", "windows_context"],
        "platform_or_context": "Windows media player",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "VideoLAN",
        "review_rationale": "Official VideoLAN release metadata identifies a concrete VLC 3.0.20 Vetinari artifact identity.",
        "short_evidence_summary": "Official VideoLAN release metadata identifies VLC 3.0.20 Vetinari and Windows release context.",
        "source_id": "videolan-vlc-3-0-20-release",
        "source_identifier": "VideoLAN official VLC 3.0.20 release page",
        "source_observation_id": "source-observation-batch-06:vlc-3-0-20-release-page",
        "source_title": "VLC 3.0.20 Vetinari",
        "source_type": "official_release_page",
        "source_url": "https://images.videolan.org/vlc/releases/3.0.20.html",
    }
    vlc_news = {
        **vlc_primary,
        "confidence": "medium",
        "duplicate_check_result": "new_identity_release_note_corroboration",
        "observation_notes": "Official VideoLAN 3.0.x NEWS changelog corroborates release-line, Windows, and security context.",
        "observed_artifact_fields": ["product", "version", "release_notes", "windows_context", "security_context"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official changelog corroborates release-line context but is not a separate gate record.",
        "short_evidence_summary": "Official VideoLAN changelog corroborates VLC 3.0.x release context.",
        "source_id": "videolan-vlc-3-0-x-news",
        "source_identifier": "VideoLAN VLC 3.0.x NEWS changelog",
        "source_observation_id": "source-observation-batch-06:vlc-3-0-x-news",
        "source_title": "VLC 3.0.x NEWS",
        "source_type": "official_release_notes",
        "source_url": "https://code.videolan.org/videolan/vlc/-/raw/3.0.x/NEWS",
    }
    vlc_security = {
        **vlc_primary,
        "confidence": "medium",
        "duplicate_check_result": "new_identity_security_bulletin_corroboration",
        "observation_notes": "Official VideoLAN security bulletin identifies VLC 3.0.20 as the solution for VideoLAN-SB-VLC-3020.",
        "observed_artifact_fields": ["product", "version", "security_bulletin_id", "affected_versions", "solution"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official security bulletin corroborates identity and security context but is not a separate gate record.",
        "short_evidence_summary": "Official VideoLAN security bulletin says VLC 3.0.20 addresses the 3.0.19-and-earlier issue.",
        "source_id": "videolan-vlc-3-0-20-security-bulletin",
        "source_identifier": "VideoLAN Security Bulletin VLC 3.0.20",
        "source_observation_id": "source-observation-batch-06:vlc-3-0-20-security-bulletin",
        "source_title": "Security Bulletin VLC 3.0.20",
        "source_type": "official_security_bulletin",
        "source_url": "https://images.videolan.org/security/sb-vlc3020.html",
    }
    gimp_primary = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows image editor",
            "product": "GIMP",
            "publisher_or_project": "GIMP Team",
            "release_date": "2024-05-05",
            "title": "GIMP 2.10.38 for Windows",
            "version": "2.10.38",
        },
        "artifact_title": "GIMP 2.10.38 for Windows",
        "artifact_type": "software",
        "candidate_id": gimp_id,
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "Official GIMP release page identifies GIMP 2.10.38, release date 2024-05-05, and Windows build context.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_platform", "release_notes"],
        "platform_or_context": "Windows image editor",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "GIMP Team",
        "review_rationale": "Official GIMP release metadata identifies a concrete GIMP 2.10.38 for Windows artifact identity.",
        "short_evidence_summary": "Official GIMP release metadata identifies GIMP 2.10.38 and Windows build context.",
        "source_id": "gimp-official-2-10-38-release",
        "source_identifier": "GIMP official 2.10.38 release page",
        "source_observation_id": "source-observation-batch-06:gimp-2-10-38-release-page",
        "source_title": "GIMP 2.10.38 Released",
        "source_type": "official_release_notes",
        "source_url": "https://www.gimp.org/news/2024/05/05/gimp-2-10-38-released/",
    }
    gimp_downloads = {
        **gimp_primary,
        "artifact_identity_fields": {
            **gimp_primary["artifact_identity_fields"],
            "source_tarball": "gimp-2.10.38.tar.bz2",
            "source_tarball_sha256": "50a845eec11c8831fe8661707950f5b8446e35f30edfb9acf98f85c1133f856e",
        },
        "confidence": "medium",
        "duplicate_check_result": "new_identity_downloads_page_corroboration",
        "observation_notes": "Official GIMP downloads page lists gimp-2.10.38.tar.bz2 and its SHA256 hash as page text.",
        "observed_artifact_fields": ["product", "version", "source_tarball", "sha256", "official_download_context"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official downloads page corroborates source tarball and hash metadata but is not a separate gate record.",
        "short_evidence_summary": "Official GIMP downloads page corroborates gimp-2.10.38.tar.bz2 and SHA256 metadata.",
        "source_id": "gimp-official-downloads-2-10-38",
        "source_identifier": "GIMP official downloads page",
        "source_observation_id": "source-observation-batch-06:gimp-2-10-38-downloads-page",
        "source_title": "GIMP Downloads",
        "source_type": "official_support_page",
        "source_url": "https://www.gimp.org/downloads/",
    }
    return [vlc_primary, vlc_news, vlc_security, gimp_primary, gimp_downloads]


if __name__ == "__main__":
    unittest.main()
