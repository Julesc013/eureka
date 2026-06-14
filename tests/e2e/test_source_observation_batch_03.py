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
from tests.e2e.test_source_observation_batch_01 import (
    _ct1740_source_lead_observation,
    _firefox_release_notes_observation,
    _firefox_system_requirements_observation,
)
from tests.e2e.test_source_observation_batch_02 import _batch02_observations


class SourceObservationBatch03Tests(unittest.TestCase):
    def test_batch03_targets_new_article_identity_and_preserves_existing_gate_records(self) -> None:
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
            plan = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(batch03_path),
                "--target-records",
                "5",
                "--json",
            )
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(batch03_path),
                "--out",
                str(batch03_path / "source_observation_template.jsonl"),
                "--json",
            )
            plan_rows = read_jsonl(batch03_path / "source_candidate_plan.jsonl")
            article = next(row for row in plan_rows if row.get("artifact_type") == "article" and row.get("source_collection_target") is True)
            firefox = _find_candidate(plan_rows, "firefox")
            sound_blaster_rows = [row for row in plan_rows if "ct1740" in json.dumps(row, sort_keys=True).casefold()]

            _write_jsonl(batch03_path / "source_observations_input.jsonl", _batch03_article_observations(demo))
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(batch03_path),
                "--observations",
                str(batch03_path / "source_observations_input.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(batch03_path),
                "--out",
                str(batch03_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            batch03_packets = read_jsonl(batch03_path / "manual_evidence_packets.jsonl")
            cumulative = cumulative + batch03_packets
            _write_jsonl(batch03_path / "manual_evidence_packets.cumulative.jsonl", cumulative)
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(batch03_path / "manual_evidence_packets.cumulative.jsonl"),
                "--json",
            )
            manual_review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_03",
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
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")
            launch_report = _load_json(demo.launch_gate_path / "launch_gate_report.json")

        self.assertEqual(plan.code, 0, plan.stderr)
        self.assertEqual(json.loads(plan.stdout)["selected_candidate_count"], 1)
        self.assertGreaterEqual(json.loads(plan.stdout)["duplicate_candidate_count"], 4)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["template_count"], 1)
        self.assertTrue(article["source_collection_target"])
        self.assertTrue(article["source_collection_curation_target"])
        self.assertFalse(firefox["source_collection_target"])
        self.assertTrue(firefox["source_collection_duplicate"])
        self.assertTrue(all(row["source_collection_duplicate"] for row in sound_blaster_rows if row.get("artifact_gate_excluded") is not True))
        driver = _find_candidate(plan_rows, "driver for win98")
        windows = _find_candidate(plan_rows, "windows 7 apps")
        self.assertFalse(driver["source_collection_target"])
        self.assertFalse(windows["source_collection_target"])
        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 3)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(json.loads(to_evidence.stdout)["artifact_verified_packet_count"], 1)
        self.assertEqual(batch03_packets[0]["artifact_title"], "Mike Miller's Many Hats")
        self.assertTrue(batch03_packets[0]["artifact_verified"])
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(manual_ingest.stdout)["evidence_packet_count"], 4)
        self.assertEqual(json.loads(manual_review.stdout)["reviewed_artifact_record_count"], 3)
        self.assertEqual(json.loads(manual_report.stdout)["reviewed_artifact_gate_count"], 3)
        self.assertEqual({record["title"] for record in records}, {"Firefox ESR 52.9.0", "Creative Labs Sound Blaster 16 manual", "Mike Miller's Many Hats"})
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 3)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_duplicate_sound_blaster_identity_is_rejected_by_manual_review(self) -> None:
        with _SourceCollectionDemo() as demo:
            batch02_path = _write_batch02_source_evidence(demo)
            packet = read_jsonl(batch02_path / "manual_evidence_packets.jsonl")[0]
            duplicate = deepcopy(packet)
            duplicate["evidence_packet_id"] = "source-derived-evidence:duplicate-sound-blaster-manual"
            _write_jsonl(demo.root / "duplicate_sound_blaster_packets.jsonl", [packet, duplicate])
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "duplicate_sound_blaster_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_observation_batch_03",
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
            review_payload = json.loads(review.stdout)

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 2)
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 1)
        self.assertEqual(review_payload["rejected_or_non_eligible_count"], 1)
        duplicate_result = review_payload["rejected_or_non_eligible"][0]
        self.assertEqual(duplicate_result["status"], "duplicate")
        self.assertEqual(duplicate_result["gate_exclusion_reason"], "duplicate_artifact_identity")
        self.assertEqual(json.loads(report.stdout)["reviewed_artifact_gate_count"], 1)


def _write_batch01_source_evidence(demo: _SourceCollectionDemo):
    batch_path = demo.root / "source-observation-batch-01"
    demo.collection_path = batch_path
    demo.write_source_plan_and_template()
    observations = [
        _firefox_system_requirements_observation(demo),
        _firefox_release_notes_observation(demo),
        _ct1740_source_lead_observation(demo),
    ]
    _write_jsonl(batch_path / "source_observations_input.jsonl", observations)
    _run_artifact_gate_main("source-ingest", "--collection", str(batch_path), "--observations", str(batch_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch_path), "--out", str(batch_path / "manual_evidence_packets.jsonl"))
    return batch_path


def _write_batch02_source_evidence(demo: _SourceCollectionDemo):
    batch_path = demo.root / "source-observation-batch-02"
    demo.collection_path = batch_path
    demo.write_source_plan_and_template()
    _write_jsonl(batch_path / "source_observations_input.jsonl", _batch02_observations(demo))
    _run_artifact_gate_main("source-ingest", "--collection", str(batch_path), "--observations", str(batch_path / "source_observations_input.jsonl"))
    _run_artifact_gate_main("source-to-evidence", "--collection", str(batch_path), "--out", str(batch_path / "manual_evidence_packets.jsonl"))
    return batch_path


def _batch03_article_observations(demo: _SourceCollectionDemo) -> list[dict[str, object]]:
    candidate = next(
        row
        for row in read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")
        if row.get("artifact_type") == "article" and row.get("source_collection_target") is True
    )
    candidate_id = candidate["candidate_id"]
    base = {
        "access_method": "bounded_page_observation",
        "artifact_title": "Mike Miller's Many Hats",
        "artifact_type": "article",
        "candidate_id": candidate_id,
        "collected_at": "2026-06-14T00:00:00Z",
        "collection_id": "source-collection:source-observation-batch-03",
        "downloaded_file": False,
        "fetched_binary": False,
        "file_fetch_performed": False,
        "live_network_used": False,
        "no_download_performed": True,
        "observed_at": "2026-06-14T00:00:00Z",
        "observer": "source_observation_batch_03",
        "platform_or_context": "IEEE Computer Graphics and Applications Vol. 14 No. 1, January 1994",
        "reviewer": "source_observation_batch_03",
        "schema_version": "eureka.artifact_source_observation.v0",
        "wayback_replay_used": False,
    }
    primary = {
        **base,
        "artifact_identity_fields": {
            "doi": "10.1109/MCG.1994.10003",
            "issue": "1",
            "issue_date": "1994-01",
            "page_range": "4-6",
            "publication_title": "IEEE Computer Graphics and Applications",
            "title": "Mike Miller's Many Hats",
            "volume": "14",
        },
        "confidence": "high",
        "duplicate_check_result": "new_identity_not_firefox_or_sound_blaster",
        "limitations": ["publication-record metadata only"],
        "observation_notes": "Publication metadata identifies the article title, January 1994 issue, volume 14, pages 4-6, and DOI.",
        "observed_artifact_fields": ["article_title", "publication_title", "issue_date", "volume", "issue", "page_range", "doi"],
        "proposed_artifact_verified": True,
        "proposed_gate_eligible": True,
        "proposed_verification_scope": "artifact_identity_metadata",
        "publisher_or_source_name": "IEEE Computer Society",
        "review_rationale": "Official publication-record metadata identifies a concrete article artifact distinct from existing gate records.",
        "short_evidence_summary": "IEEE metadata identifies Mike Miller's Many Hats in IEEE CG&A, January 1994, pages 4-6.",
        "source_authority": "primary",
        "source_id": "ieee-cg-1994-01-mike-millers-many-hats",
        "source_identifier": "DOI 10.1109/MCG.1994.10003",
        "source_observation_id": "source-observation-batch-03:ieee-mike-millers-many-hats",
        "source_title": "Mike Miller's Many Hats - IEEE Computer Society",
        "source_type": "publication_record",
        "source_url": "https://store.example.invalid/csdl/magazine/cg/1994/01/mcg1994010004",
    }
    secondary = {
        **base,
        "artifact_identity_fields": {
            "issue": "1",
            "issue_date": "1994-01",
            "page_range": "4-6",
            "publication_title": "IEEE Computer Graphics and Applications",
            "ray_tracing_context": "Ray Tracing News Vol. 7 No. 1",
            "title": "Mike Miller's Many Hats",
            "volume": "14",
        },
        "confidence": "medium",
        "duplicate_check_result": "new_identity_ray_tracing_context_corroboration",
        "limitations": ["secondary ray-tracing newsletter context"],
        "observation_notes": "Ray Tracing News identifies the article in IEEE CG&A, volume 14 number 1, January 1994, pages 4-6.",
        "observed_artifact_fields": ["article_title", "publication_title", "issue_date", "volume", "issue", "page_range", "ray_tracing_context"],
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "publisher_or_source_name": "Ray Tracing News",
        "review_rationale": "Secondary ray-tracing source corroborates article identity and context only.",
        "short_evidence_summary": "Ray Tracing News corroborates the article identity and ray-tracing context.",
        "source_authority": "reputable_secondary",
        "source_id": "rtnews-v7n1-pov-in-ieee-cga",
        "source_identifier": "Ray Tracing News Volume 7 Number 1",
        "source_observation_id": "source-observation-batch-03:rtnews-mike-millers-many-hats",
        "source_title": "Ray Tracing News, Volume 7, Number 1",
        "source_type": "reputable_secondary_reference",
        "source_url": "https://graphics.example.invalid/RTNews/rtnv7n1.html",
    }
    faq = {
        **secondary,
        "source_id": "faqs-raytrace-faq-part2-mike-millers-many-hats",
        "source_identifier": "comp.graphics.rendering.raytracing FAQ part 2",
        "source_observation_id": "source-observation-batch-03:faqs-raytrace-mike-millers-many-hats",
        "source_title": "comp.graphics.rendering.raytracing FAQ (part 2/2)",
        "source_url": "https://faqs.example.invalid/graphics/raytrace-faq/part2/",
        "duplicate_check_result": "new_identity_secondary_corroboration",
        "short_evidence_summary": "Ray-tracing FAQ metadata corroborates the January 1994 IEEE CG&A cover-story context.",
    }
    return [primary, secondary, faq]


if __name__ == "__main__":
    unittest.main()
