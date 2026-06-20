from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.index.preview import (
    build_preview_index,
    compare_preview_generations,
    load_preview_manifest,
    search_preview_index,
    validate_preview_index,
)


class E2EPreviewIndexModelTests(unittest.TestCase):
    def test_builds_status_and_authority_separated_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inputs = _write_delta_inputs(root)
            out_root = root / "preview"

            result = build_preview_index(
                out_root=out_root,
                candidate_delta=inputs["candidate_manifest"],
                evidence_delta=inputs["evidence_manifest"],
                source_observation_delta=inputs["source_manifest"],
                reviewed_records=inputs["reviewed_records"],
            )
            validation = validate_preview_index(result["current_path"], strict=True)
            records = _read_jsonl(Path(result["record_file"]))

        self.assertEqual("pass", validation["status"], validation["errors"])
        self.assertEqual(result["record_count"], len(records))
        self.assertIn("reviewed", result["status_counts"])
        self.assertIn("candidate", result["status_counts"])
        self.assertIn("absence", result["status_counts"])
        self.assertIn("mention_only", result["status_counts"])
        self.assertEqual(1, result["authority_counts"]["reviewed_record"])
        self.assertGreaterEqual(result["authority_counts"]["candidate_only"], 1)
        self.assertTrue(any(record["accepted_truth"] is True and record["authority"] == "reviewed_record" for record in records))
        self.assertTrue(all(record["accepted_truth"] is False for record in records if record["authority"] != "reviewed_record"))

    def test_search_returns_ranked_lanes_and_preserves_non_truth_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inputs = _write_delta_inputs(root)
            result = build_preview_index(
                out_root=root / "preview",
                candidate_delta=inputs["candidate_manifest"],
                evidence_delta=inputs["evidence_manifest"],
                source_observation_delta=inputs["source_manifest"],
                reviewed_records=inputs["reviewed_records"],
            )
            search = search_preview_index(result["current_path"], "WinFTP XP client", limit=10)

        self.assertGreaterEqual(search["result_count"], 1)
        self.assertIn("candidates", search["lanes"])
        self.assertTrue(any(item["status"] == "candidate" for item in search["results"]))
        for item in search["results"]:
            if item["status"] == "candidate":
                self.assertEqual("candidate_only", item["authority"])
                self.assertFalse(item["accepted_truth"])
                self.assertIn("human review before promotion", item["missing_information"])

    def test_generation_id_is_deterministic_for_same_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inputs = _write_delta_inputs(root)
            first = build_preview_index(
                out_root=root / "preview-a",
                candidate_delta=inputs["candidate_manifest"],
                evidence_delta=inputs["evidence_manifest"],
                source_observation_delta=inputs["source_manifest"],
                reviewed_records=inputs["reviewed_records"],
            )
            second = build_preview_index(
                out_root=root / "preview-b",
                candidate_delta=inputs["candidate_manifest"],
                evidence_delta=inputs["evidence_manifest"],
                source_observation_delta=inputs["source_manifest"],
                reviewed_records=inputs["reviewed_records"],
            )
            first_records = Path(first["record_file"]).read_text(encoding="utf-8")
            second_records = Path(second["record_file"]).read_text(encoding="utf-8")

        self.assertEqual(first["preview_index_id"], second["preview_index_id"])
        self.assertEqual(first_records, second_records)

    def test_validation_rejects_provisional_record_marked_as_accepted_truth(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inputs = _write_delta_inputs(root)
            result = build_preview_index(
                out_root=root / "preview",
                candidate_delta=inputs["candidate_manifest"],
                evidence_delta=inputs["evidence_manifest"],
                source_observation_delta=inputs["source_manifest"],
            )
            records_path = Path(result["record_file"])
            records = _read_jsonl(records_path)
            candidate = next(record for record in records if record["authority"] == "candidate_only")
            candidate["accepted_truth"] = True
            _write_jsonl(records_path, records)
            validation = validate_preview_index(result["current_path"], strict=True)

        self.assertEqual("fail", validation["status"])
        self.assertTrue(any("accepted_truth requires reviewed_record authority" in error for error in validation["errors"]))

    def test_compare_generations_reports_added_and_removed_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inputs = _write_delta_inputs(root)
            first = build_preview_index(out_root=root / "preview", candidate_delta=inputs["candidate_manifest"])
            second = build_preview_index(
                out_root=root / "preview",
                candidate_delta=inputs["candidate_manifest"],
                evidence_delta=inputs["evidence_manifest"],
            )
            comparison = compare_preview_generations(root / "preview", first["preview_index_id"], second["preview_index_id"])

        self.assertGreaterEqual(len(comparison["added"]), 1)
        self.assertGreaterEqual(len(comparison["added"]) + len(comparison["removed"]), 1)


def _write_delta_inputs(root: Path) -> dict[str, str]:
    source_dir = root / "source"
    candidate_dir = root / "candidate"
    evidence_dir = root / "evidence"
    reviewed_dir = root / "reviewed"
    for directory in (source_dir, candidate_dir, evidence_dir, reviewed_dir):
        directory.mkdir(parents=True, exist_ok=True)

    source_manifest = source_dir / "source_observation_delta_manifest.json"
    source_records = source_dir / "source_observations.jsonl"
    source_manifest.write_text(json.dumps({"observation_file": source_records.name}, sort_keys=True), encoding="utf-8")
    _write_jsonl(
        source_records,
        [
            {
                "observation_id": "source-observation:ia_metadata:test-001",
                "query_seed": "WinFTP XP client",
                "source_family": "ia_metadata",
                "source_id": "internet_archive_metadata",
                "provider_mode": "live",
                "normalized_metadata": {"title": "WinFTP candidate metadata"},
                "transport_status": "ok",
                "limitations": ["metadata support only"],
            }
        ],
    )

    candidate_manifest = candidate_dir / "candidate_index_delta_manifest.json"
    candidate_records = candidate_dir / "candidate_index_delta.jsonl"
    candidate_manifest.write_text(json.dumps({"candidate_file": candidate_records.name}, sort_keys=True), encoding="utf-8")
    _write_jsonl(
        candidate_records,
        [
            {
                "candidate_id": "candidate:ia_metadata:test-winftp",
                "source_family": "ia_metadata",
                "source_observation_refs": ["source-observation:ia_metadata:test-001"],
                "query_seed_refs": ["WinFTP XP client"],
                "provider_mode_refs": ["live"],
                "normalized_title": "WinFTP XP candidate",
                "normalized_type_hints": ["ftp_client"],
                "review_state": "unreviewed",
            }
        ],
    )

    evidence_manifest = evidence_dir / "evidence_summary_delta_manifest.json"
    evidence_records = evidence_dir / "evidence_summaries.jsonl"
    evidence_manifest.write_text(json.dumps({"evidence_summary_file": evidence_records.name}, sort_keys=True), encoding="utf-8")
    _write_jsonl(
        evidence_records,
        [
            {
                "evidence_summary_id": "evidence:ia_metadata:test-support",
                "candidate_refs": ["candidate:ia_metadata:test-winftp"],
                "source_observation_refs": ["source-observation:ia_metadata:test-001"],
                "source_family": "ia_metadata",
                "query_seed_refs": ["WinFTP XP client"],
                "evidence_type": "object-type clue",
                "support_posture": "candidate_support",
                "proposition": "Metadata mentions an FTP client candidate for Windows XP.",
                "normalized_support_summary": "Metadata supports a provisional FTP client candidate.",
            },
            {
                "evidence_summary_id": "evidence:ia_metadata:test-absence",
                "candidate_refs": [],
                "source_observation_refs": ["source-observation:ia_metadata:test-001"],
                "source_family": "ia_metadata",
                "query_seed_refs": ["WinFTP XP client"],
                "evidence_type": "absence clue",
                "support_posture": "insufficient",
                "proposition": "No reviewed archive representation has been confirmed.",
                "normalized_support_summary": "Independent archive representation remains missing.",
                "absence_or_near_miss_flags": ["representation_missing"],
                "uncertainty": ["independent source evidence missing"],
            },
        ],
    )

    reviewed_records = reviewed_dir / "reviewed_records.jsonl"
    _write_jsonl(
        reviewed_records,
        [
            {
                "reviewed_record_id": "reviewed:local:test-sound-driver",
                "title": "Reviewed local Sound Driver record",
                "summary": "Synthetic-free reviewed local fixture used to prove preview authority separation.",
                "accepted_truth": True,
                "artifact_verified": False,
                "review_refs": ["review:event:test-001"],
                "source_refs": ["source:local:test-001"],
                "evidence_refs": ["evidence:local:test-001"],
                "source_family": "local_review",
            }
        ],
    )

    return {
        "source_manifest": str(source_manifest),
        "candidate_manifest": str(candidate_manifest),
        "evidence_manifest": str(evidence_manifest),
        "reviewed_records": str(reviewed_records),
    }


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
