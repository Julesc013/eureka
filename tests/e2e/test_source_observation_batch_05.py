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
from tests.e2e.test_source_observation_batch_03 import (
    _batch03_article_observations,
    _write_batch01_source_evidence,
    _write_batch02_source_evidence,
)
from tests.e2e.test_source_observation_batch_04 import _batch04_curated_observations


class SourceObservationBatch05Tests(unittest.TestCase):
    def test_batch05_uses_next_curated_targets_after_batch04_identities_are_duplicates(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch04(demo)

            batch05_path = demo.root / "source-observation-batch-05"
            demo.collection_path = batch05_path
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch05_path),
                "--target-records",
                "5",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch05_path),
                "--out",
                str(batch05_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch05_path / "source_candidate_plan.jsonl")
            _write_jsonl(batch05_path / "source_observations_input.jsonl", _batch05_curated_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch05_path),
                "--observations",
                str(batch05_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch05_path),
                "--out",
                str(batch05_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch05_packets = read_jsonl(batch05_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch05_packets
            _write_jsonl(batch05_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch05_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_05",
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
                str(batch05_path),
                "--out",
                str(batch05_path / "source_collection_report.json"),
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
        self.assertGreaterEqual(plan_payload["duplicate_candidate_count"], 7)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 2)
        targets = [row for row in plan_rows if row.get("source_collection_target") is True]
        self.assertEqual({row["candidate_id"] for row in targets}, {"artifact-gate-curated:putty-0-78-windows", "artifact-gate-curated:audacity-3-2-5-windows"})
        self.assertTrue(all(row.get("curated_source_collection_target") is True for row in targets))
        self.assertTrue(_find_candidate(plan_rows, "7-zip 19.00")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "winscp 5.21.8")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "firefox")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "source evidence for article")["source_collection_duplicate"])
        self.assertFalse(_find_candidate(plan_rows, "windows 7 apps")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "driver for win98")["source_collection_target"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 4)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 2)
        self.assertEqual({packet["artifact_title"] for packet in batch05_packets}, {"PuTTY 0.78 for Windows", "Audacity 3.2.5 for Windows"})
        self.assertTrue(all(packet["artifact_verified"] for packet in batch05_packets))
        self.assertTrue(all(packet["binary_verified"] is False for packet in batch05_packets))
        self.assertTrue(all(packet["download_safe"] is False for packet in batch05_packets))
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 8)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 7)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 7)
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
            },
        )
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 7)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_duplicate_batch04_curated_identities_cannot_increment_gate_count(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch04(demo)
            batch04_packets = [packet for packet in cumulative if packet.get("artifact_title") in {"7-Zip 19.00 for Windows", "WinSCP 5.21.8"}]
            duplicates = []
            for packet in batch04_packets:
                duplicate = deepcopy(packet)
                duplicate["evidence_packet_id"] = f"{packet['evidence_packet_id']}:duplicate"
                duplicates.append(duplicate)
            _write_jsonl(demo.root / "duplicate_batch04_packets.jsonl", cumulative + duplicates)
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "duplicate_batch04_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_05",
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
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 8)
        self.assertEqual(review.code, 0, review.stderr)
        review_payload = json.loads(review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 5)
        duplicate_results = [item for item in review_payload["rejected_or_non_eligible"] if item.get("status") == "duplicate"]
        self.assertEqual(len(duplicate_results), 2)
        self.assertTrue(all(item["gate_exclusion_reason"] == "duplicate_artifact_identity" for item in duplicate_results))
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 5)


def _seed_manual_gate_through_batch04(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    batch01_path = _write_batch01_source_evidence(demo)
    batch02_path = _write_batch02_source_evidence(demo)
    cumulative = read_jsonl(batch01_path / "manual_evidence_packets.jsonl") + read_jsonl(batch02_path / "manual_evidence_packets.jsonl")
    _write_jsonl(demo.root / "manual_evidence_packets.batch_01_02.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(demo.root / "manual_evidence_packets.batch_01_02.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_02",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))

    batch03_path = demo.root / "source-observation-batch-03"
    demo.collection_path = batch03_path
    _run_artifact_gate_main("source-plan", "--gate", str(demo.seed_gate_path), "--manual-batch", str(demo.batch_path), "--out", str(batch03_path), "--target-records", "5")
    _run_artifact_gate_main("source-template", "--collection", str(batch03_path), "--out", str(batch03_path / "source_observation_template.jsonl"))
    _write_jsonl(batch03_path / "source_observations_input.jsonl", _batch03_article_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch03_path), "--observations", str(batch03_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch03_path), "--out", str(batch03_path / "manual_evidence_packets.jsonl"))
    cumulative = cumulative + read_jsonl(batch03_path / "manual_evidence_packets.jsonl")
    _write_jsonl(batch03_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(batch03_path / "manual_evidence_packets.cumulative.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_03",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))

    batch04_path = demo.root / "source-observation-batch-04"
    demo.collection_path = batch04_path
    _run_artifact_gate_main("source-plan", "--gate", str(demo.seed_gate_path), "--manual-batch", str(demo.batch_path), "--out", str(batch04_path), "--target-records", "5")
    _run_artifact_gate_main("source-template", "--collection", str(batch04_path), "--out", str(batch04_path / "source_observation_template.jsonl"))
    _write_jsonl(batch04_path / "source_observations_input.jsonl", _batch04_curated_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch04_path), "--observations", str(batch04_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch04_path), "--out", str(batch04_path / "manual_evidence_packets.jsonl"))
    cumulative = cumulative + read_jsonl(batch04_path / "manual_evidence_packets.jsonl")
    _write_jsonl(batch04_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(batch04_path / "manual_evidence_packets.cumulative.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_04",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
    return cumulative


def _batch05_curated_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
    putty_id = next(row["candidate_id"] for row in plan_rows if row.get("candidate_id") == "artifact-gate-curated:putty-0-78-windows")
    audacity_id = next(row["candidate_id"] for row in plan_rows if row.get("candidate_id") == "artifact-gate-curated:audacity-3-2-5-windows")
    base = {
        "access_method": "bounded_page_observation",
        "batch_id": "source-observation-batch-05",
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-05",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_05",
        "reviewer": "source_observation_batch_05",
        "schema_version": "eureka.artifact_source_observation.v0",
        "source_authority": "primary",
        "wayback_replay_used": False,
    }
    putty_primary = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows SSH/Telnet client",
            "product": "PuTTY",
            "publisher_or_project": "Simon Tatham / PuTTY project",
            "release_date": "2022-10-29",
            "title": "PuTTY 0.78 for Windows",
            "version": "0.78",
        },
        "artifact_title": "PuTTY 0.78 for Windows",
        "artifact_type": "software",
        "candidate_id": putty_id,
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "does not verify binary safety or download integrity"],
        "observation_notes": "Official PuTTY release page identifies PuTTY 0.78, release date 2022-10-29, and Windows package context.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_platform", "publisher_or_project"],
        "platform_or_context": "Windows SSH/Telnet client",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "PuTTY project",
        "review_rationale": "Official PuTTY release metadata identifies a concrete PuTTY 0.78 for Windows artifact identity.",
        "short_evidence_summary": "Official PuTTY release page identifies PuTTY 0.78 for Windows and release date.",
        "source_id": "putty-official-release-0-78",
        "source_identifier": "PuTTY official 0.78 release page",
        "source_observation_id": "source-observation-batch-05:putty-0-78-release",
        "source_title": "PuTTY 0.78 release page",
        "source_type": "official_release_page",
        "source_url": "https://www.chiark.greenend.org.uk/~sgtatham/putty/releases/0.78.html",
    }
    putty_changelog = {
        **putty_primary,
        "confidence": "medium",
        "duplicate_check_result": "new_identity_release_note_corroboration",
        "observation_notes": "Official PuTTY change log corroborates PuTTY 0.78 release date and release notes.",
        "observed_artifact_fields": ["product", "version", "release_date", "release_notes"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official change log corroborates identity but is not a separate gate record.",
        "short_evidence_summary": "Official PuTTY change log corroborates PuTTY 0.78 identity.",
        "source_id": "putty-official-changelog-0-78",
        "source_identifier": "PuTTY official change log",
        "source_observation_id": "source-observation-batch-05:putty-0-78-changelog",
        "source_title": "PuTTY Change Log",
        "source_type": "official_release_notes",
        "source_url": "https://www.chiark.greenend.org.uk/~sgtatham/putty/changes.html",
    }
    audacity_primary = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows audio editor",
            "product": "Audacity",
            "release_date": "2023-03-01",
            "supported_windows_versions": ["Windows 10", "Windows 11", "Windows Vista", "Windows 7", "Windows 8.1"],
            "title": "Audacity 3.2.5 for Windows",
            "version": "3.2.5",
        },
        "artifact_title": "Audacity 3.2.5 for Windows",
        "artifact_type": "software",
        "candidate_id": audacity_id,
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_prior_gate_artifacts",
        "limitations": ["page observation only", "older Windows versions noted as untested"],
        "observation_notes": "Official Audacity support changelog identifies Audacity 3.2.5, release date 2023-03-01, and Windows support context.",
        "observed_artifact_fields": ["product", "version", "release_date", "supported_windows_versions", "release_notes"],
        "platform_or_context": "Windows audio editor",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "Audacity Team",
        "review_rationale": "Official Audacity changelog metadata identifies a concrete Audacity 3.2.5 for Windows artifact identity.",
        "short_evidence_summary": "Official Audacity support changelog identifies Audacity 3.2.5 and Windows support context.",
        "source_id": "audacity-official-changelog-3-2-5",
        "source_identifier": "Audacity official 3.2.5 changelog",
        "source_observation_id": "source-observation-batch-05:audacity-3-2-5-changelog",
        "source_title": "Audacity 3.2.5",
        "source_type": "official_release_notes",
        "source_url": "https://support.audacityteam.org/additional-resources/changelog/older-versions/audacity-3.2/audacity-3.2.5",
    }
    audacity_family = {
        **audacity_primary,
        "confidence": "medium",
        "duplicate_check_result": "new_identity_family_changelog_corroboration",
        "observation_notes": "Official Audacity 3.2 family changelog corroborates Audacity 3.2 release lineage and Windows audio-editor context.",
        "observed_artifact_fields": ["product", "major_version", "release_date", "feature_context", "windows_context"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official family changelog corroborates context but is not a separate gate record.",
        "short_evidence_summary": "Official Audacity 3.2 changelog corroborates release-line identity and context.",
        "source_id": "audacity-official-changelog-3-2-family",
        "source_identifier": "Audacity official 3.2 changelog",
        "source_observation_id": "source-observation-batch-05:audacity-3-2-family-changelog",
        "source_title": "Audacity 3.2",
        "source_type": "official_release_notes",
        "source_url": "https://support.audacityteam.org/additional-resources/changelog/older-versions/audacity-3.2",
    }
    return [putty_primary, putty_changelog, audacity_primary, audacity_family]


if __name__ == "__main__":
    unittest.main()
