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
from tests.e2e.test_source_observation_batch_08 import (
    _batch08_curated_observations,
    _seed_manual_gate_through_batch07,
)


class SourceObservationBatch09Tests(unittest.TestCase):
    def test_batch09_can_close_corpus_gate_without_launch_ready_claim(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch08(demo)

            batch09_path = demo.root / "source-observation-batch-09"
            demo.collection_path = batch09_path
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch09_path),
                "--target-records",
                "7",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch09_path),
                "--out",
                str(batch09_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch09_path / "source_candidate_plan.jsonl")
            _write_jsonl(batch09_path / "source_observations_input.jsonl", _batch09_curated_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch09_path),
                "--observations",
                str(batch09_path / "source_observations_input.jsonl"),
                "--json",
            )
            source_validate = _run_artifact_gate_main("source-validate", "--collection", str(batch09_path), "--json")
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch09_path),
                "--out",
                str(batch09_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch09_packets = read_jsonl(batch09_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch09_packets
            _write_jsonl(batch09_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch09_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_validate = _run_artifact_gate_main("manual-validate", "--batch", str(demo.batch_path), "--json")
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_09",
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
                str(batch09_path),
                "--out",
                str(batch09_path / "source_collection_report.json"),
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
        self.assertEqual(plan_payload["selected_candidate_count"], 7)
        self.assertEqual(plan_payload["selection_limit"], 7)
        self.assertEqual(plan_payload["curated_candidate_count"], 22)
        self.assertGreaterEqual(plan_payload["duplicate_candidate_count"], 18)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 7)
        targets = [row for row in plan_rows if row.get("source_collection_target") is True]
        self.assertEqual(
            {row["candidate_id"] for row in targets},
            {
                "artifact-gate-curated:qbittorrent-4-6-4-windows",
                "artifact-gate-curated:filezilla-pro-3-67-0-windows",
                "artifact-gate-curated:obs-studio-30-1-windows",
                "artifact-gate-curated:handbrake-1-7-3-windows",
                "artifact-gate-curated:winmerge-2-16-40-windows",
                "artifact-gate-curated:calibre-7-8-0-windows",
                "artifact-gate-curated:python-3-12-3-windows",
            },
        )
        self.assertTrue(_find_candidate(plan_rows, "wireshark 4.2.3")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "sumatrapdf 3.5.2")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "thunderbird 115.10.1")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "irfanview 4.67")["source_collection_duplicate"])
        self.assertTrue(_find_candidate(plan_rows, "paint.net 5.0.13")["source_collection_duplicate"])
        self.assertFalse(_find_candidate(plan_rows, "windows 7 apps")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "old blue ftp client")["source_collection_target"])
        self.assertFalse(_find_candidate(plan_rows, "driver for win98")["source_collection_target"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 12)
        self.assertEqual(source_validate.code, 0, source_validate.stderr)
        self.assertEqual(json.loads(source_validate.stdout)["proposed_artifact_verified_count"], 7)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 7)
        self.assertEqual(
            {packet["artifact_title"] for packet in batch09_packets},
            {
                "qBittorrent 4.6.4 for Windows",
                "FileZilla Pro 3.67.0 for Windows",
                "OBS Studio 30.1 for Windows",
                "HandBrake 1.7.3 for Windows",
                "WinMerge 2.16.40 for Windows",
                "calibre 7.8.0 for Windows",
                "Python 3.12.3 for Windows",
            },
        )
        self.assertTrue(all(packet["artifact_verified"] for packet in batch09_packets))
        self.assertTrue(all(packet["binary_verified"] is False for packet in batch09_packets))
        self.assertTrue(all(packet["download_safe"] is False for packet in batch09_packets))
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 26)
        self.assertEqual(manual_validate.code, 0, manual_validate.stderr)
        self.assertEqual(json.loads(manual_validate.stdout)["artifact_verified_packet_count"], 25)
        self.assertEqual(manual_review.code, 0, manual_review.stderr)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 25)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 25)
        self.assertEqual(json.loads(manual_report.stdout)["gate_status"], "pass")
        self.assertEqual(json.loads(source_report.stdout)["artifact_verified_packet_count"], 7)
        self.assertEqual(len(records), 25)
        self.assertIn("qBittorrent 4.6.4 for Windows", {record["title"] for record in records})
        self.assertIn("Python 3.12.3 for Windows", {record["title"] for record in records})
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 25)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "pass")
        blocker_ids = {item["id"] for item in launch_report["blockers"]}
        self.assertNotIn("official_reviewed_artifact_gate_not_passed", blocker_ids)
        self.assertIn("verified_artifact_evidence_not_promoted", blocker_ids)
        self.assertIn("external_staging_host_missing", blocker_ids)

    def test_duplicate_batch09_curated_identities_cannot_increment_past_gate_target(self) -> None:
        with _SourceCollectionDemo() as demo:
            cumulative = _seed_manual_gate_through_batch08(demo)
            batch09_path = demo.root / "source-observation-batch-09"
            demo.collection_path = batch09_path
            _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch09_path),
                "--target-records",
                "7",
            )
            _run_artifact_gate_main("source-template", "--collection", str(batch09_path), "--out", str(batch09_path / "source_observation_template.jsonl"))
            _write_jsonl(batch09_path / "source_observations_input.jsonl", _batch09_curated_observations(demo))
            _run_artifact_gate_main("source-ingest", "--collection", str(batch09_path), "--observations", str(batch09_path / "source_observations_input.jsonl"))
            _run_artifact_gate_main("source-to-evidence", "--collection", str(batch09_path), "--out", str(batch09_path / "manual_evidence_packets.jsonl"))
            batch09_packets = read_jsonl(batch09_path / "manual_evidence_packets.jsonl")
            duplicates = []
            for packet in batch09_packets:
                duplicate = deepcopy(packet)
                duplicate["evidence_packet_id"] = f"{packet['evidence_packet_id']}:duplicate"
                duplicates.append(duplicate)
            _write_jsonl(batch09_path / "duplicate_batch09_packets.jsonl", cumulative + batch09_packets + duplicates)
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch09_path / "duplicate_batch09_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_09",
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
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 33)
        self.assertEqual(review.code, 0, review.stderr)
        review_payload = json.loads(review.stdout)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 25)
        duplicate_results = [item for item in review_payload["rejected_or_non_eligible"] if item.get("status") == "duplicate"]
        self.assertEqual(len(duplicate_results), 7)
        self.assertTrue(all(item["gate_exclusion_reason"] == "duplicate_artifact_identity" for item in duplicate_results))
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 25)


def _seed_manual_gate_through_batch08(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    cumulative = _seed_manual_gate_through_batch07(demo)
    batch08_path = demo.root / "source-observation-batch-08"
    demo.collection_path = batch08_path
    _run_artifact_gate_main("source-plan", "--gate", str(demo.seed_gate_path), "--manual-batch", str(demo.batch_path), "--out", str(batch08_path), "--target-records", "5")
    _run_artifact_gate_main("source-template", "--collection", str(batch08_path), "--out", str(batch08_path / "source_observation_template.jsonl"))
    _write_jsonl(batch08_path / "source_observations_input.jsonl", _batch08_curated_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch08_path), "--observations", str(batch08_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch08_path), "--out", str(batch08_path / "manual_evidence_packets.jsonl"))
    cumulative = cumulative + read_jsonl(batch08_path / "manual_evidence_packets.jsonl")
    _write_jsonl(batch08_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
    _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(batch08_path / "manual_evidence_packets.cumulative.jsonl"))
    _run_artifact_gate_main(
        "manual-review",
        "--batch",
        str(demo.batch_path),
        "--reviewer",
        "source_observation_batch_08",
        "--out",
        str(demo.batch_path / "reviewed_artifact_records.jsonl"),
    )
    _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
    return cumulative


def _batch09_curated_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
    candidate_ids = {
        row["candidate_id"]: row["candidate_id"]
        for row in plan_rows
        if str(row.get("candidate_id") or "").startswith("artifact-gate-curated:")
    }
    base = {
        "access_method": "bounded_page_observation",
        "batch_id": "source-observation-batch-09",
        "collected_at": "2026-06-15T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-09",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-15T00:00:00Z",
        "observer": "source_observation_batch_09",
        "reviewer": "source_observation_batch_09",
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
        source_authority: str = "primary",
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
                else "Source metadata corroborates the same identity but is not a separate gate record."
            ),
            "short_evidence_summary": notes,
            "source_authority": source_authority,
            "source_id": source_id,
            "source_identifier": source_title,
            "source_observation_id": f"source-observation-batch-09:{source_id}",
            "source_title": source_title,
            "source_type": source_type,
            "source_url": source_url,
        }

    qbit_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows BitTorrent client",
        "product": "qBittorrent",
        "publisher_or_project": "qBittorrent project",
        "release_date": "2024-03-24",
        "title": "qBittorrent 4.6.4 for Windows",
        "version": "4.6.4",
    }
    filezilla_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows file-transfer client",
        "product": "FileZilla Pro",
        "publisher_or_project": "FileZilla Pro / FileZilla Project",
        "release_date": "2024-04-15",
        "title": "FileZilla Pro 3.67.0 for Windows",
        "version": "3.67.0",
    }
    obs_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows recording and streaming application",
        "product": "OBS Studio",
        "publisher_or_project": "OBS Project",
        "release_date": "2024-03-13",
        "title": "OBS Studio 30.1 for Windows",
        "version": "30.1",
    }
    handbrake_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows video transcoder",
        "product": "HandBrake",
        "publisher_or_project": "HandBrake Team",
        "release_date": "2024-02-11",
        "title": "HandBrake 1.7.3 for Windows",
        "version": "1.7.3",
    }
    winmerge_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows visual diff and merge utility",
        "product": "WinMerge",
        "publisher_or_project": "WinMerge project",
        "release_date": "2024-04-27",
        "title": "WinMerge 2.16.40 for Windows",
        "version": "2.16.40",
    }
    calibre_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows e-book manager",
        "product": "calibre",
        "publisher_or_project": "calibre project",
        "release_date": "2024-04-05",
        "title": "calibre 7.8.0 for Windows",
        "version": "7.8.0",
    }
    python_fields = {
        "artifact_type": "software",
        "platform_or_context": "Windows programming language runtime",
        "product": "Python",
        "publisher_or_project": "Python Software Foundation",
        "release_date": "2024-04-09",
        "title": "Python 3.12.3 for Windows",
        "version": "3.12.3",
    }

    return [
        observed(
            candidate_id="artifact-gate-curated:qbittorrent-4-6-4-windows",
            title="qBittorrent 4.6.4 for Windows",
            platform="Windows BitTorrent client",
            fields=qbit_fields,
            source_id="qbittorrent-4-6-4-github-release-tag",
            source_title="qBittorrent release-4.6.4",
            source_type="official_release_page",
            source_url="https://github.com/qbittorrent/qBittorrent/releases/tag/release-4.6.4",
            notes="Official qBittorrent GitHub release tag identifies release-4.6.4 and release tagging metadata.",
            observed_fields=["product", "version", "release_tag", "release_date"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:qbittorrent-4-6-4-windows",
            title="qBittorrent 4.6.4 for Windows",
            platform="Windows BitTorrent client",
            fields=qbit_fields,
            source_id="qbittorrent-4-6-4-sourceforge-win32",
            source_title="qBittorrent win32 4.6.4 project file page",
            source_type="archive_metadata_page",
            source_url="https://sourceforge.net/projects/qbittorrent/files/qbittorrent-win32/qbittorrent-4.6.4/",
            notes="Project file page corroborates qBittorrent 4.6.4 Windows package naming and date metadata.",
            observed_fields=["product", "version", "windows_package_context", "release_date"],
            verified=False,
            duplicate_check_result="new_identity_windows_package_corroboration",
            source_authority="archive_metadata",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:filezilla-pro-3-67-0-windows",
            title="FileZilla Pro 3.67.0 for Windows",
            platform="Windows file-transfer client",
            fields=filezilla_fields,
            source_id="filezilla-pro-3-67-0-version-history",
            source_title="FileZilla Pro Version History",
            source_type="official_release_notes",
            source_url="https://filezillapro.com/filezilla-pro-version-history/",
            notes="Official FileZilla Pro version history identifies 3.67.0 release date, fixed vulnerability context, and official binaries.",
            observed_fields=["product", "version", "release_date", "official_binary_context"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:filezilla-pro-3-67-0-windows",
            title="FileZilla Pro 3.67.0 for Windows",
            platform="Windows file-transfer client",
            fields=filezilla_fields,
            source_id="filezilla-pro-windows-product-page",
            source_title="FileZilla Pro Download",
            source_type="official_product_page",
            source_url="https://filezillapro.com/download/",
            notes="Official FileZilla Pro product page corroborates Windows availability and FTP/SFTP client context.",
            observed_fields=["product", "windows_context", "file_transfer_protocol_context"],
            verified=False,
            duplicate_check_result="new_identity_platform_corroboration",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:obs-studio-30-1-windows",
            title="OBS Studio 30.1 for Windows",
            platform="Windows recording and streaming application",
            fields=obs_fields,
            source_id="obs-studio-30-1-release-notes",
            source_title="OBS Studio 30.1 Release Notes",
            source_type="official_release_notes",
            source_url="https://obsproject.com/blog/obs-studio-30-1-release-notes",
            notes="Official OBS release notes identify OBS Studio 30.1, release date, and Windows-specific changes.",
            observed_fields=["product", "version", "release_date", "windows_change_context"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:obs-studio-30-1-windows",
            title="OBS Studio 30.1 for Windows",
            platform="Windows recording and streaming application",
            fields=obs_fields,
            source_id="obs-studio-windows-download-context",
            source_title="Download OBS Studio",
            source_type="official_product_page",
            source_url="https://obsproject.com/download",
            notes="Official OBS download page corroborates Windows release/support context.",
            observed_fields=["product", "windows_context", "supported_windows_versions"],
            verified=False,
            duplicate_check_result="new_identity_platform_corroboration",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:handbrake-1-7-3-windows",
            title="HandBrake 1.7.3 for Windows",
            platform="Windows video transcoder",
            fields=handbrake_fields,
            source_id="handbrake-1-7-3-release-news",
            source_title="HandBrake 1.7.3 Released",
            source_type="official_release_page",
            source_url="https://handbrake.fr/news.php?article=52",
            notes="Official HandBrake news identifies 1.7.3, release date, and Windows runtime context.",
            observed_fields=["product", "version", "release_date", "windows_runtime_context"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:winmerge-2-16-40-windows",
            title="WinMerge 2.16.40 for Windows",
            platform="Windows visual diff and merge utility",
            fields=winmerge_fields,
            source_id="winmerge-2-16-40-release-history",
            source_title="WinMerge Release History",
            source_type="official_release_page",
            source_url="https://github.com/WinMerge/winmerge/wiki/Release-History",
            notes="Official WinMerge release history identifies 2.16.40 and release date.",
            observed_fields=["product", "version", "release_date"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:winmerge-2-16-40-windows",
            title="WinMerge 2.16.40 for Windows",
            platform="Windows visual diff and merge utility",
            fields=winmerge_fields,
            source_id="winmerge-2-16-40-sourceforge-files",
            source_title="WinMerge stable 2.16.40 project file page",
            source_type="archive_metadata_page",
            source_url="https://sourceforge.net/projects/winmerge/files/stable/2.16.40/",
            notes="Project file page corroborates WinMerge 2.16.40 Windows files and release notes.",
            observed_fields=["product", "version", "windows_package_context", "release_notes"],
            verified=False,
            duplicate_check_result="new_identity_windows_package_corroboration",
            source_authority="archive_metadata",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:calibre-7-8-0-windows",
            title="calibre 7.8.0 for Windows",
            platform="Windows e-book manager",
            fields=calibre_fields,
            source_id="calibre-7-8-whats-new",
            source_title="calibre What's New - Release 7.8",
            source_type="official_release_notes",
            source_url="https://calibre-ebook.com/whats-new",
            notes="Official calibre What's New page identifies release 7.8 and release date.",
            observed_fields=["product", "version", "release_date", "change_summary"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
        observed(
            candidate_id="artifact-gate-curated:calibre-7-8-0-windows",
            title="calibre 7.8.0 for Windows",
            platform="Windows e-book manager",
            fields=calibre_fields,
            source_id="calibre-7-8-0-release-directory",
            source_title="calibre release 7.8.0",
            source_type="official_release_page",
            source_url="https://download.calibre-ebook.com/7.8.0/",
            notes="Official calibre release directory corroborates 7.8.0 and Windows package context.",
            observed_fields=["product", "version", "windows_package_context"],
            verified=False,
            duplicate_check_result="new_identity_windows_package_corroboration",
            confidence="medium",
        ),
        observed(
            candidate_id="artifact-gate-curated:python-3-12-3-windows",
            title="Python 3.12.3 for Windows",
            platform="Windows programming language runtime",
            fields=python_fields,
            source_id="python-3-12-3-release-page",
            source_title="Python 3.12.3",
            source_type="official_release_page",
            source_url="https://www.python.org/downloads/release/python-3123/",
            notes="Official Python.org release page identifies Python 3.12.3, release date, and Windows installer records.",
            observed_fields=["product", "version", "release_date", "windows_installer_records"],
            verified=True,
            duplicate_check_result="new_identity_not_prior_gate_artifacts",
        ),
    ]


if __name__ == "__main__":
    unittest.main()
