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


class SourceObservationBatch04Tests(unittest.TestCase):
    def test_batch04_uses_curated_targets_after_existing_candidates_are_duplicates_or_too_vague(self) -> None:
        with _SourceCollectionDemo() as demo:
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
            _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch03_path),
                "--target-records",
                "5",
            )
            _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch03_path),
                "--out",
                str(batch03_path / "source_observation_template.jsonl"),
            )
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
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch04_path),
                "--target-records",
                "5",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch04_path),
                "--out",
                str(batch04_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch04_path / "source_candidate_plan.jsonl")
            _write_jsonl(batch04_path / "source_observations_input.jsonl", _batch04_curated_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch04_path),
                "--observations",
                str(batch04_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch04_path),
                "--out",
                str(batch04_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch04_packets = read_jsonl(batch04_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch04_packets
            _write_jsonl(batch04_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch04_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_04",
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
                str(batch04_path),
                "--out",
                str(batch04_path / "source_collection_report.json"),
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
        self.assertEqual(plan_payload["curated_candidate_count"], 2)
        self.assertGreaterEqual(plan_payload["duplicate_candidate_count"], 5)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 2)
        targets = [row for row in plan_rows if row.get("source_collection_target") is True]
        self.assertEqual({row["candidate_id"] for row in targets}, {"artifact-gate-curated:7zip-19-00-windows", "artifact-gate-curated:winscp-5-21-8"})
        self.assertTrue(all(row.get("curated_source_collection_target") is True for row in targets))
        self.assertFalse(_find_candidate(plan_rows, "windows 7 apps")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "driver for win98")["source_collection_target"])
        self.assertTrue(_find_candidate(plan_rows, "firefox")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "source evidence for article")["source_collection_duplicate"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 4)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 2)
        self.assertEqual({packet["artifact_title"] for packet in batch04_packets}, {"7-Zip 19.00 for Windows", "WinSCP 5.21.8"})
        self.assertTrue(all(packet["artifact_verified"] for packet in batch04_packets))
        self.assertTrue(all(packet["binary_verified"] is False for packet in batch04_packets))
        self.assertTrue(all(packet["download_safe"] is False for packet in batch04_packets))
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 6)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 5)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 5)
        self.assertEqual(json.loads(manual_report.stdout)["gate_status"], "blocked")
        self.assertEqual(json.loads(source_report.stdout)["artifact_verified_packet_count"], 2)
        self.assertEqual({record["title"] for record in records}, {"Firefox ESR 52.9.0", "Creative Labs Sound Blaster 16 manual", "Mike Miller's Many Hats", "7-Zip 19.00 for Windows", "WinSCP 5.21.8"})
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 5)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_duplicate_batch03_article_identity_cannot_increment_gate_count(self) -> None:
        with _SourceCollectionDemo() as demo:
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
            article_packet = read_jsonl(batch03_path / "manual_evidence_packets.jsonl")[0]
            duplicate = deepcopy(article_packet)
            duplicate["evidence_packet_id"] = "source-derived-evidence:duplicate-mike-millers-many-hats"
            cumulative = cumulative + [article_packet, duplicate]
            _write_jsonl(demo.root / "duplicate_article_packets.jsonl", cumulative)
            ingest = _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(demo.root / "duplicate_article_packets.jsonl"), "--json")
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_04",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )
            report = _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"), "--json")

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 5)
        self.assertEqual(review.code, 0, review.stderr)
        review_payload = json.loads(review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 3)
        self.assertEqual(review_payload["rejected_or_non_eligible_count"], 2)
        duplicate_results = [item for item in review_payload["rejected_or_non_eligible"] if item.get("status") == "duplicate"]
        self.assertEqual(len(duplicate_results), 1)
        self.assertEqual(duplicate_results[0]["gate_exclusion_reason"], "duplicate_artifact_identity")
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 3)


def _batch04_curated_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
    seven_zip_id = next(row["candidate_id"] for row in plan_rows if row.get("candidate_id") == "artifact-gate-curated:7zip-19-00-windows")
    winscp_id = next(row["candidate_id"] for row in plan_rows if row.get("candidate_id") == "artifact-gate-curated:winscp-5-21-8")
    base = {
        "access_method": "bounded_page_observation",
        "batch_id": "source-observation-batch-04",
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-04",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_04",
        "reviewer": "source_observation_batch_04",
        "schema_version": "eureka.artifact_source_observation.v0",
        "wayback_replay_used": False,
    }
    seven_zip_primary = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows desktop utility",
            "product": "7-Zip",
            "release_date": "2019-02-21",
            "title": "7-Zip 19.00 for Windows",
            "version": "19.00",
        },
        "artifact_title": "7-Zip 19.00 for Windows",
        "artifact_type": "software",
        "candidate_id": seven_zip_id,
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_firefox_sound_blaster_or_mike_millers_many_hats",
        "limitations": ["page observation only"],
        "observation_notes": "Official 7-Zip download metadata identifies 7-Zip 19.00 for Windows and release date 2019-02-21.",
        "observed_artifact_fields": ["product", "version", "release_date", "windows_platform"],
        "platform_or_context": "Windows desktop utility",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "7-Zip / Igor Pavlov",
        "review_rationale": "Official project metadata identifies a concrete 7-Zip 19.00 for Windows artifact.",
        "short_evidence_summary": "Official 7-Zip metadata identifies 7-Zip 19.00 for Windows.",
        "source_authority": "primary",
        "source_id": "7zip-official-download-19-00",
        "source_identifier": "7-Zip official download page",
        "source_observation_id": "source-observation-batch-04:7zip-19-00-download-page",
        "source_title": "Download - 7-Zip",
        "source_type": "official_support_page",
        "source_url": "https://www.7-zip.org/download.html",
    }
    seven_zip_context = {
        **seven_zip_primary,
        "confidence": "medium",
        "duplicate_check_result": "new_identity_platform_context_corroboration",
        "observation_notes": "Official 7-Zip product page corroborates product identity and Windows platform context.",
        "observed_artifact_fields": ["product", "supported_windows_versions", "software_description"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "review_rationale": "Official product page is platform context only.",
        "short_evidence_summary": "Official 7-Zip product page corroborates product and Windows platform context.",
        "source_id": "7zip-official-product-page",
        "source_identifier": "7-Zip official product page",
        "source_observation_id": "source-observation-batch-04:7zip-product-page",
        "source_title": "7-Zip",
        "source_type": "official_product_page",
        "source_url": "https://www.7-zip.org/",
    }
    winscp_primary = {
        **base,
        "artifact_identity_fields": {
            "artifact_type": "software",
            "platform_or_context": "Windows FTP/SFTP client",
            "product": "WinSCP",
            "release_date": "2023-04-11",
            "title": "WinSCP 5.21.8",
            "version": "5.21.8",
        },
        "artifact_title": "WinSCP 5.21.8",
        "artifact_type": "software",
        "candidate_id": winscp_id,
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_firefox_sound_blaster_or_mike_millers_many_hats",
        "limitations": ["page observation only"],
        "observation_notes": "Official WinSCP history identifies version 5.21.8 and release date 2023-04-11.",
        "observed_artifact_fields": ["product", "version", "release_date", "release_notes"],
        "platform_or_context": "Windows FTP/SFTP client",
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "WinSCP project",
        "review_rationale": "Official WinSCP version history identifies a concrete WinSCP 5.21.8 artifact.",
        "short_evidence_summary": "Official WinSCP history identifies WinSCP 5.21.8 and date.",
        "source_authority": "primary",
        "source_id": "winscp-official-history-5-21-8",
        "source_identifier": "WinSCP official version history",
        "source_observation_id": "source-observation-batch-04:winscp-5-21-8-history",
        "source_title": "Older Versions - WinSCP",
        "source_type": "official_release_notes",
        "source_url": "https://winscp.net/eng/docs/history_old",
    }
    winscp_catalog = {
        **winscp_primary,
        "artifact_identity_fields": {
            **winscp_primary["artifact_identity_fields"],
            "checksums_observed": ["MD5", "SHA-1", "SHA-256"],
        },
        "confidence": "medium",
        "duplicate_check_result": "new_identity_catalog_corroboration",
        "observation_notes": "SourceForge listing corroborates WinSCP 5.21.8 file-listing metadata, date, and Windows FTP/SFTP client context.",
        "observed_artifact_fields": ["product", "version", "release_date", "client_type", "file_listing_metadata", "checksums"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "publisher_or_source_name": "SourceForge",
        "review_rationale": "Stable catalog page corroborates identity but is not a standalone verification claim.",
        "short_evidence_summary": "SourceForge listing corroborates WinSCP 5.21.8 metadata.",
        "source_authority": "stable_catalog",
        "source_id": "sourceforge-winscp-5-21-8-listing",
        "source_identifier": "SourceForge WinSCP 5.21.8 file listing",
        "source_observation_id": "source-observation-batch-04:sourceforge-winscp-5-21-8",
        "source_title": "WinSCP - Browse /WinSCP/5.21.8 at SourceForge.net",
        "source_type": "stable_catalog_page",
        "source_url": "https://sourceforge.net/projects/winscp/files/WinSCP/5.21.8/",
    }
    return [seven_zip_primary, seven_zip_context, winscp_primary, winscp_catalog]


if __name__ == "__main__":
    unittest.main()
