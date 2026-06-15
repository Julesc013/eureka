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
from tests.e2e.test_source_observation_batch_07 import (
    _batch07_curated_observations,
    _seed_manual_gate_through_batch06,
)


class SourceObservationBatch08Tests(unittest.TestCase):
    def test_batch08_uses_very_high_throughput_targets_after_batch07_duplicates(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch07(demo)

            batch08_path = demo.root / "source-observation-batch-08"
            demo.collection_path = batch08_path
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch08_path),
                "--target-records",
                "5",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch08_path),
                "--out",
                str(batch08_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch08_path / "source_candidate_plan.jsonl")
            _write_jsonl(batch08_path / "source_observations_input.jsonl", _batch08_curated_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch08_path),
                "--observations",
                str(batch08_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch08_path),
                "--out",
                str(batch08_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch08_packets = read_jsonl(batch08_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch08_packets
            _write_jsonl(batch08_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch08_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_08",
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
                str(batch08_path),
                "--out",
                str(batch08_path / "source_collection_report.json"),
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
        self.assertEqual(plan_payload["selected_candidate_count"], 5)
        self.assertEqual(plan_payload["selection_limit"], 5)
        self.assertEqual(plan_payload["curated_candidate_count"], 22)
        self.assertGreaterEqual(plan_payload["duplicate_candidate_count"], 15)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 5)
        targets = [row for row in plan_rows if row.get("source_collection_target") is True]
        self.assertEqual(
            {row["candidate_id"] for row in targets},
            {
                "artifact-gate-curated:wireshark-4-2-3-windows",
                "artifact-gate-curated:sumatrapdf-3-5-2-windows",
                "artifact-gate-curated:thunderbird-115-10-1-windows",
                "artifact-gate-curated:irfanview-4-67-windows",
                "artifact-gate-curated:paint-net-5-0-13-windows",
            },
        )
        self.assertTrue(_find_candidate(plan_rows, "notepad++ v8.6")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "inkscape 1.3.2")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "libreoffice 7.6.7")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "apache openoffice 4.1.15")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "vlc 3.0.20")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "gimp 2.10.38")["source_collection_duplicate"])
        self.assertFalse(_find_candidate(plan_rows, "windows 7 apps")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "old blue ftp client")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "driver for win98")["source_collection_target"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 9)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 5)
        self.assertEqual(
            {packet["artifact_title"] for packet in batch08_packets},
            {
                "Wireshark 4.2.3 for Windows",
                "SumatraPDF 3.5.2 for Windows",
                "Thunderbird 115.10.1 for Windows",
                "IrfanView 4.67 for Windows",
                "Paint.NET 5.0.13 for Windows",
            },
        )
        self.assertTrue(all(packet["artifact_verified"] for packet in batch08_packets))
        self.assertTrue(all(packet["binary_verified"] is False for packet in batch08_packets))
        self.assertTrue(all(packet["download_safe"] is False for packet in batch08_packets))
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 19)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 18)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 18)
        self.assertEqual(json.loads(manual_report.stdout)["gate_status"], "blocked")
        self.assertEqual(json.loads(source_report.stdout)["artifact_verified_packet_count"], 5)
        self.assertEqual(len(records), 18)
        self.assertIn("Wireshark 4.2.3 for Windows", {record["title"] for record in records})
        self.assertIn("Paint.NET 5.0.13 for Windows", {record["title"] for record in records})
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 18)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_duplicate_batch07_curated_identities_cannot_increment_gate_count(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch07(demo)
            batch07_titles = {
                "Notepad++ v8.6 for Windows",
                "Inkscape 1.3.2 for Windows",
                "LibreOffice 7.6.7 Community for Windows",
                "Apache OpenOffice 4.1.15 for Windows",
            }
            batch07_packets = [packet for packet in cumulative if packet.get("artifact_title") in batch07_titles]
            duplicates = []
            for packet in batch07_packets:
                duplicate = deepcopy(packet)
                duplicate["evidence_packet_id"] = f"{packet['evidence_packet_id']}:duplicate"
                duplicates.append(duplicate)
            _write_jsonl(demo.root / "duplicate_batch07_packets.jsonl", cumulative + duplicates)
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "duplicate_batch07_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_08",
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
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 18)
        self.assertEqual(review.code, 0, review.stderr)
        review_payload = json.loads(review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 13)
        duplicate_results = [item for item in review_payload["rejected_or_non_eligible"] if item.get("status") == "duplicate"]
        self.assertEqual(len(duplicate_results), 4)
        self.assertTrue(all(item["gate_exclusion_reason"] == "duplicate_artifact_identity" for item in duplicate_results))
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 13)


def _seed_manual_gate_through_batch07(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    cumulative = _seed_manual_gate_through_batch06(demo)
    batch07_path = demo.root / "source-observation-batch-07"
    demo.collection_path = batch07_path
    _run_artifact_gate_main("source-plan", "--gate", str(demo.seed_gate_path), "--manual-batch", str(demo.batch_path), "--out", str(batch07_path), "--target-records", "5")
    _run_artifact_gate_main("source-template", "--collection", str(batch07_path), "--out", str(batch07_path / "source_observation_template.jsonl"))
    _write_jsonl(batch07_path / "source_observations_input.jsonl", _batch07_curated_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch07_path), "--observations", str(batch07_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch07_path), "--out", str(batch07_path / "manual_evidence_packets.jsonl"))
    cumulative = cumulative + read_jsonl(batch07_path / "manual_evidence_packets.jsonl")
    _write_jsonl(batch07_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(batch07_path / "manual_evidence_packets.cumulative.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_07",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
    return cumulative


def _batch08_curated_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
    candidate_ids = {
        row["candidate_id"]: row["candidate_id"]
        for row in plan_rows
        if str(row.get("candidate_id") or "").startswith("artifact-gate-curated:")
    }
    base = {
        "access_method": "bounded_page_observation",
        "batch_id": "source-observation-batch-08",
        "collected_at": "2026-06-15T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-08",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-15T00:00:00Z",
        "observer": "source_observation_batch_08",
        "reviewer": "source_observation_batch_08",
        "schema_version": "eureka.artifact_source_observation.v0",
        "source_authority": "primary",
        "wayback_replay_used": False,
    }

    def observed(
        *,
        candidate_id: str,
        title: str,
        platform: str,
        fields: dict[str, object],
        source_id: str,
        source_title: str,
        source_type: str,
        source_url: str,
        notes: str,
        observed_fields: list[str],
        verified: bool,
        duplicate_check_result: str,
        confidence: str = "high",
    ) -> dict[str, object]:
        return {
            **base,
            "artifact_identity_fields": fields,
            "artifact_title": title,
            "artifact_type": "software",
            "candidate_id": candidate_ids[candidate_id],
            "confidence": confidence,
            "duplicate_check_result": duplicate_check_result,
            "limitations": ["page observation only", "does not verify binary/download/execution/rights safety"],
            "observation_notes": notes,
            "observed_artifact_fields": observed_fields,
            "platform_or_context": platform,
            "proposed_artifact_verified": verified,
            "proposed_gate_eligible": verified,
            "proposed_verification_scope": "artifact_identity_metadata" if verified else "artifact_identity_candidate",
            "publisher_or_source_name": str(fields.get("publisher_or_project") or fields.get("publisher_or_source_name") or ""),
            "review_rationale": (
                f"Official source metadata identifies a concrete {title} artifact identity."
                if verified
                else "Official source metadata corroborates the same identity but is not a separate gate record."
            ),
            "short_evidence_summary": notes,
            "source_id": source_id,
            "source_identifier": source_title,
            "source_observation_id": f"source-observation-batch-08:{source_id}",
            "source_title": source_title,
            "source_type": source_type,
            "source_url": source_url,
        }

    wireshark_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows network protocol analyzer",
        "product": "Wireshark",
        "publisher_or_project": "Wireshark Foundation / Wireshark project",
        "release_date": "2024-02-14",
        "title": "Wireshark 4.2.3 for Windows",
        "version": "4.2.3",
    }
    sumatra_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows document viewer",
        "product": "SumatraPDF",
        "publisher_or_project": "SumatraPDF project",
        "release_date": "2023-10-25",
        "title": "SumatraPDF 3.5.2 for Windows",
        "version": "3.5.2",
    }
    thunderbird_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows desktop mail client",
        "product": "Thunderbird Desktop",
        "publisher_or_project": "Thunderbird project",
        "release_date": "2024-04-18",
        "title": "Thunderbird 115.10.1 for Windows",
        "version": "115.10.1",
    }
    irfanview_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows image viewer",
        "product": "IrfanView",
        "publisher_or_project": "Irfan Skiljan / IrfanView",
        "release_date": "2024-04-05",
        "title": "IrfanView 4.67 for Windows",
        "version": "4.67",
    }
    paint_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows image editor",
        "product": "Paint.NET",
        "publisher_or_project": "Paint.NET / Rick Brewster",
        "release_date": "2024-03-05",
        "title": "Paint.NET 5.0.13 for Windows",
        "version": "5.0.13",
    }

    return [
        observed(
            candidate_id="artifact-gate-curated:wireshark-4-2-3-windows",
            title="Wireshark 4.2.3 for Windows",
            platform="Windows network protocol analyzer",
            fields=wireshark_fields,
            source_id="wireshark-4-2-3-release-news",
            source_title="Wireshark 4.2.3, 4.0.13 and 3.6.21 Released",
            source_type="official_release_page",
            source_url="https://www.wireshark.org/news/20240214.html",
            notes="Official Wireshark news identifies 4.2.3, release date, and Windows installer availability.",
            observed_fields=["product", "version", "release_date", "windows_installer_availability"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:wireshark-4-2-3-windows",
            title="Wireshark 4.2.3 for Windows",
            platform="Windows network protocol analyzer",
            fields=wireshark_fields,
            source_id="wireshark-4-2-3-release-notes",
            source_title="Wireshark 4.2.3 Release Notes",
            source_type="official_release_notes",
            source_url="https://www.wireshark.org/docs/relnotes/wireshark-4.2.3.html",
            notes="Official Wireshark release notes corroborate 4.2.3 and Windows upgrade context.",
            observed_fields=["product", "version", "windows_upgrade_context"],
            verified=False,
            duplicate_check_result="new_identity_release_note_corroboration",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:sumatrapdf-3-5-2-windows",
            title="SumatraPDF 3.5.2 for Windows",
            platform="Windows document viewer",
            fields=sumatra_fields,
            source_id="sumatrapdf-3-5-2-version-history",
            source_title="SumatraPDF Version history",
            source_type="official_release_notes",
            source_url="https://www.sumatrapdfreader.org/docs/Version-history",
            notes="Official SumatraPDF version history identifies 3.5.2 and release date.",
            observed_fields=["product", "version", "release_date"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:sumatrapdf-3-5-2-windows",
            title="SumatraPDF 3.5.2 for Windows",
            platform="Windows document viewer",
            fields=sumatra_fields,
            source_id="sumatrapdf-product-page",
            source_title="Free PDF Reader - Sumatra PDF",
            source_type="official_product_page",
            source_url="https://www.sumatrapdfreader.org/free-pdf-reader",
            notes="Official SumatraPDF product page identifies SumatraPDF as a Windows document viewer.",
            observed_fields=["product", "windows_context", "artifact_type"],
            verified=False,
            duplicate_check_result="new_identity_product_page_corroboration",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:thunderbird-115-10-1-windows",
            title="Thunderbird 115.10.1 for Windows",
            platform="Windows desktop mail client",
            fields=thunderbird_fields,
            source_id="thunderbird-115-10-1-release-notes",
            source_title="Release Notes - Thunderbird 115.10.1",
            source_type="official_release_notes",
            source_url="https://www.thunderbird.net/en-US/thunderbird/115.10.1/releasenotes/",
            notes="Official Thunderbird release notes identify 115.10.1, release date, and Windows support.",
            observed_fields=["product", "version", "release_date", "windows_system_requirements"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:irfanview-4-67-windows",
            title="IrfanView 4.67 for Windows",
            platform="Windows image viewer",
            fields=irfanview_fields,
            source_id="irfanview-4-67-history",
            source_title="History of IrfanView changes/versions",
            source_type="official_release_notes",
            source_url="https://www.irfanview.com/history_old.htm",
            notes="Official IrfanView history identifies version 4.67 and release date.",
            observed_fields=["product", "version", "release_date"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:irfanview-4-67-windows",
            title="IrfanView 4.67 for Windows",
            platform="Windows image viewer",
            fields=irfanview_fields,
            source_id="irfanview-64bit-platform-context",
            source_title="IrfanView 64-bit version",
            source_type="official_support_page",
            source_url="https://www.irfanview.com/64bit.htm",
            notes="Official IrfanView 64-bit page corroborates Windows platform context.",
            observed_fields=["product", "windows_context", "32_bit_64_bit_context"],
            verified=False,
            duplicate_check_result="new_identity_platform_corroboration",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:paint-net-5-0-13-windows",
            title="Paint.NET 5.0.13 for Windows",
            platform="Windows image editor",
            fields=paint_fields,
            source_id="paint-net-5-0-13-roadmap",
            source_title="Paint.NET Roadmap and Change Log",
            source_type="official_release_notes",
            source_url="https://paint.net/roadmap.html",
            notes="Official Paint.NET roadmap identifies 5.0.13 and release date.",
            observed_fields=["product", "version", "release_date", "change_summary"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:paint-net-5-0-13-windows",
            title="Paint.NET 5.0.13 for Windows",
            platform="Windows image editor",
            fields=paint_fields,
            source_id="paint-net-5-0-13-release-post",
            source_title="paint.net 5.0.13 is now available!",
            source_type="official_release_post",
            source_url="https://forums.getpaint.net/topic/125401-paintnet-5013-is-now-available/",
            notes="Official Paint.NET forum post corroborates 5.0.13 availability and desktop release context.",
            observed_fields=["product", "version", "release_date", "desktop_release_context"],
            verified=False,
            duplicate_check_result="new_identity_release_post_corroboration",
            confidence="medium",
        ),
    ]


if __name__ == "__main__":
    unittest.main()
