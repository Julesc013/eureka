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
from tests.e2e.test_source_observation_batch_06 import (
    _batch06_curated_observations,
    _seed_manual_gate_through_batch05,
)


class SourceObservationBatch07Tests(unittest.TestCase):
    def test_batch07_uses_high_throughput_curated_targets_after_batch06_duplicates(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch06(demo)

            batch07_path = demo.root / "source-observation-batch-07"
            demo.collection_path = batch07_path
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch07_path),
                "--target-records",
                "5",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch07_path),
                "--out",
                str(batch07_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch07_path / "source_candidate_plan.jsonl")
            _write_jsonl(batch07_path / "source_observations_input.jsonl", _batch07_curated_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch07_path),
                "--observations",
                str(batch07_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch07_path),
                "--out",
                str(batch07_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch07_packets = read_jsonl(batch07_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch07_packets
            _write_jsonl(batch07_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch07_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_07",
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
                str(batch07_path),
                "--out",
                str(batch07_path / "source_collection_report.json"),
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
        self.assertEqual(plan_payload["selected_candidate_count"], 4)
        self.assertEqual(plan_payload["selection_limit"], 4)
        self.assertEqual(plan_payload["curated_candidate_count"], 15)
        self.assertGreaterEqual(plan_payload["duplicate_candidate_count"], 11)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 4)
        targets = [row for row in plan_rows if row.get("source_collection_target") is True]
        self.assertEqual(
            {row["candidate_id"] for row in targets},
            {
                "artifact-gate-curated:notepad-plus-plus-8-6-windows",
                "artifact-gate-curated:inkscape-1-3-2-windows",
                "artifact-gate-curated:libreoffice-7-6-7-windows",
                "artifact-gate-curated:apache-openoffice-4-1-15-windows",
            },
        )
        self.assertTrue(_find_candidate(plan_rows, "vlc 3.0.20")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "gimp 2.10.38")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "putty 0.78")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "audacity 3.2.5")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "firefox")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "source evidence for article")["source_collection_duplicate"])
        self.assertFalse(_find_candidate(plan_rows, "windows 7 apps")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "driver for win98")["source_collection_target"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 6)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 4)
        self.assertEqual(
            {packet["artifact_title"] for packet in batch07_packets},
            {
                "Notepad++ v8.6 for Windows",
                "Inkscape 1.3.2 for Windows",
                "LibreOffice 7.6.7 Community for Windows",
                "Apache OpenOffice 4.1.15 for Windows",
            },
        )
        self.assertTrue(all(packet["artifact_verified"] for packet in batch07_packets))
        self.assertTrue(all(packet["binary_verified"] is False for packet in batch07_packets))
        self.assertTrue(all(packet["download_safe"] is False for packet in batch07_packets))
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 14)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 13)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 13)
        self.assertEqual(json.loads(manual_report.stdout)["gate_status"], "blocked")
        self.assertEqual(json.loads(source_report.stdout)["artifact_verified_packet_count"], 4)
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
                "Notepad++ v8.6 for Windows",
                "Inkscape 1.3.2 for Windows",
                "LibreOffice 7.6.7 Community for Windows",
                "Apache OpenOffice 4.1.15 for Windows",
            },
        )
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 13)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_duplicate_batch06_curated_identities_cannot_increment_gate_count(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch06(demo)
            batch06_packets = [
                packet
                for packet in cumulative
                if packet.get("artifact_title") in {"VLC 3.0.20 Vetinari", "GIMP 2.10.38 for Windows"}
            ]
            duplicates = []
            for packet in batch06_packets:
                duplicate = deepcopy(packet)
                duplicate["evidence_packet_id"] = f"{packet['evidence_packet_id']}:duplicate"
                duplicates.append(duplicate)
            _write_jsonl(demo.root / "duplicate_batch06_packets.jsonl", cumulative + duplicates)
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "duplicate_batch06_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_07",
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
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 12)
        self.assertEqual(review.code, 0, review.stderr)
        review_payload = json.loads(review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 9)
        duplicate_results = [item for item in review_payload["rejected_or_non_eligible"] if item.get("status") == "duplicate"]
        self.assertEqual(len(duplicate_results), 2)
        self.assertTrue(all(item["gate_exclusion_reason"] == "duplicate_artifact_identity" for item in duplicate_results))
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 9)


def _seed_manual_gate_through_batch06(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    cumulative = _seed_manual_gate_through_batch05(demo)
    batch06_path = demo.root / "source-observation-batch-06"
    demo.collection_path = batch06_path
    _run_artifact_gate_main("source-plan", "--gate", str(demo.seed_gate_path), "--manual-batch", str(demo.batch_path), "--out", str(batch06_path), "--target-records", "5")
    _run_artifact_gate_main("source-template", "--collection", str(batch06_path), "--out", str(batch06_path / "source_observation_template.jsonl"))
    _write_jsonl(batch06_path / "source_observations_input.jsonl", _batch06_curated_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch06_path), "--observations", str(batch06_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch06_path), "--out", str(batch06_path / "manual_evidence_packets.jsonl"))
    cumulative = cumulative + read_jsonl(batch06_path / "manual_evidence_packets.jsonl")
    _write_jsonl(batch06_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(batch06_path / "manual_evidence_packets.cumulative.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_06",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
    return cumulative


def _batch07_curated_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
    candidate_ids = {
        row["candidate_id"]: row["candidate_id"]
        for row in plan_rows
        if str(row.get("candidate_id") or "").startswith("artifact-gate-curated:")
    }
    base = {
        "access_method": "bounded_page_observation",
        "batch_id": "source-observation-batch-07",
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-07",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_07",
        "reviewer": "source_observation_batch_07",
        "schema_version": "eureka.artifact_source_observation.v0",
        "source_authority": "primary",
        "wayback_replay_used": False,
    }
    notepad = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows text editor",
            "product": "Notepad++",
            "publisher_or_project": "Notepad++ project",
            "release_date": "2023-11-23",
            "release_name": "20th-Year Anniversary",
            "title": "Notepad++ v8.6 for Windows",
            "version": "8.6",
        },
        "artifact_title": "Notepad++ v8.6 for Windows",
        "artifact_type": "software",
        "candidate_id": candidate_ids["artifact-gate-curated:notepad-plus-plus-8-6-windows"],
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "Official Notepad++ page identifies v8.6, release date 2023-11-23, Windows package context, and release notes.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_platform", "release_notes"],
        "platform_or_context": "Windows text editor",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "Notepad++ project",
        "review_rationale": "Official Notepad++ release metadata identifies a concrete Notepad++ v8.6 Windows artifact identity.",
        "short_evidence_summary": "Official Notepad++ page identifies v8.6 and release date.",
        "source_id": "notepad-plus-plus-official-v8-6",
        "source_identifier": "Notepad++ official v8.6 release/download page",
        "source_observation_id": "source-observation-batch-07:notepad-plus-plus-v8-6-release-page",
        "source_title": "Download Notepad++ v8.6: 20th-Year Anniversary",
        "source_type": "official_release_page",
        "source_url": "https://notepad-plus-plus.org/downloads/v8.6/",
    }
    inkscape = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows vector graphics editor",
            "product": "Inkscape",
            "publisher_or_project": "Inkscape project",
            "release_date": "2023-11-26",
            "title": "Inkscape 1.3.2 for Windows",
            "version": "1.3.2",
        },
        "artifact_title": "Inkscape 1.3.2 for Windows",
        "artifact_type": "software",
        "candidate_id": candidate_ids["artifact-gate-curated:inkscape-1-3-2-windows"],
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "Official Inkscape 1.3.2 release notes identify release date, bugfix scope, and Windows-specific context.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_context", "release_notes"],
        "platform_or_context": "Windows vector graphics editor",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "Inkscape project",
        "review_rationale": "Official Inkscape release notes identify a concrete Inkscape 1.3.2 Windows artifact identity.",
        "short_evidence_summary": "Official Inkscape release notes identify Inkscape 1.3.2 and release date.",
        "source_id": "inkscape-official-1-3-2-release-notes",
        "source_identifier": "Inkscape official 1.3.2 release notes",
        "source_observation_id": "source-observation-batch-07:inkscape-1-3-2-release-notes",
        "source_title": "Release notes/1.3.2",
        "source_type": "official_release_notes",
        "source_url": "https://wiki.inkscape.org/wiki/Release_notes/1.3.2",
    }
    inkscape_context = {
        **inkscape,
        "confidence": "medium",
        "duplicate_check_result": "new_identity_release_line_corroboration",
        "observation_notes": "Official Inkscape 1.3 release notes corroborate Windows-specific context for the 1.3 release line.",
        "observed_artifact_fields": ["product", "major_version", "windows_context", "release_line_notes"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official 1.3 release notes corroborate context but are not a separate gate record.",
        "short_evidence_summary": "Official Inkscape 1.3 release notes corroborate Windows context.",
        "source_id": "inkscape-official-1-3-release-notes",
        "source_identifier": "Inkscape official 1.3 release notes",
        "source_observation_id": "source-observation-batch-07:inkscape-1-3-release-notes",
        "source_title": "Release notes/1.3",
        "source_url": "https://wiki.inkscape.org/wiki/index.php/Release_notes/1.3",
    }
    libreoffice = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows office suite",
            "product": "LibreOffice Community",
            "publisher_or_project": "The Document Foundation",
            "release_date": "2024-05-10",
            "release_line": "7.6",
            "title": "LibreOffice 7.6.7 Community for Windows",
            "version": "7.6.7",
        },
        "artifact_title": "LibreOffice 7.6.7 Community for Windows",
        "artifact_type": "software",
        "candidate_id": candidate_ids["artifact-gate-curated:libreoffice-7-6-7-windows"],
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "The Document Foundation blog identifies LibreOffice 7.6.7 Community, date, final 7.6 line context, and Windows availability.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_platform", "release_line"],
        "platform_or_context": "Windows office suite",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "The Document Foundation",
        "review_rationale": "Official TDF release metadata identifies a concrete LibreOffice 7.6.7 Community Windows artifact identity.",
        "short_evidence_summary": "Official TDF blog identifies LibreOffice 7.6.7 Community and Windows availability.",
        "source_id": "tdf-libreoffice-7-6-7-release-blog",
        "source_identifier": "The Document Foundation LibreOffice 7.6.7 release blog",
        "source_observation_id": "source-observation-batch-07:libreoffice-7-6-7-release-blog",
        "source_title": "LibreOffice 7.6.7 for productivity environments",
        "source_type": "official_release_notes",
        "source_url": "https://blog.documentfoundation.org/blog/2024/05/10/libreoffice-7-6-7/",
    }
    openoffice = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows office suite",
            "product": "Apache OpenOffice",
            "publisher_or_project": "Apache OpenOffice project / Apache Software Foundation",
            "release_date": "2023-12-22",
            "title": "Apache OpenOffice 4.1.15 for Windows",
            "version": "4.1.15",
        },
        "artifact_title": "Apache OpenOffice 4.1.15 for Windows",
        "artifact_type": "software",
        "candidate_id": candidate_ids["artifact-gate-curated:apache-openoffice-4-1-15-windows"],
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
        "observation_notes": "Official Apache OpenOffice announcement identifies 4.1.15, date 2023-12-22, Windows/macOS/Linux availability, and maintenance-release scope.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_platform", "release_notes"],
        "platform_or_context": "Windows office suite",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "Apache OpenOffice project",
        "review_rationale": "Official Apache OpenOffice announcement identifies a concrete Apache OpenOffice 4.1.15 Windows artifact identity.",
        "short_evidence_summary": "Official Apache OpenOffice announcement identifies 4.1.15 and Windows availability.",
        "source_id": "apache-openoffice-4-1-15-announcement",
        "source_identifier": "Apache OpenOffice official 4.1.15 announcement",
        "source_observation_id": "source-observation-batch-07:apache-openoffice-4-1-15-announcement",
        "source_title": "Announcing Apache OpenOffice 4.1.15",
        "source_type": "official_release_page",
        "source_url": "https://openoffice.apache.org/blog/announcing-apache-openoffice-4-1-15.html",
    }
    openoffice_notes = {
        **openoffice,
        "artifact_identity_fields": {
            **openoffice["artifact_identity_fields"],
            "build_id": "AOO4115m2 / Build ID 9813 / Rev. 5f13fa0070",
        },
        "confidence": "medium",
        "duplicate_check_result": "new_identity_release_note_corroboration",
        "observation_notes": "Official Apache OpenOffice 4.1.15 release notes corroborate identity, build reference, and Windows platform support.",
        "observed_artifact_fields": ["product", "version", "build_id", "platforms", "security_context"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official release notes corroborate identity and platform support but are not a separate gate record.",
        "short_evidence_summary": "Official Apache OpenOffice release notes corroborate 4.1.15 identity and Windows support.",
        "source_id": "apache-openoffice-4-1-15-release-notes",
        "source_identifier": "Apache OpenOffice 4.1.15 release notes",
        "source_observation_id": "source-observation-batch-07:apache-openoffice-4-1-15-release-notes",
        "source_title": "AOO 4.1.15 Release Notes",
        "source_type": "official_release_notes",
        "source_url": "https://cwiki.apache.org/confluence/display/OOOUSERS/AOO%2B4.1.15%2BRelease%2BNotes",
    }
    return [notepad, inkscape, inkscape_context, libreoffice, openoffice, openoffice_notes]


if __name__ == "__main__":
    unittest.main()
