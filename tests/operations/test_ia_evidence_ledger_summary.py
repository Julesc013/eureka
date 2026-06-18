from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime.local.candidate_index_refresh import (
    CANDIDATE_FILE_NAME,
    MANIFEST_FILE_NAME as CANDIDATE_MANIFEST_FILE_NAME,
)
from runtime.local.candidate_index_refresh import (
    build_delta as build_candidate_index_delta,
)
from runtime.local.evidence_ledger_summary import (
    EVIDENCE_SUMMARY_FILE_NAME,
    MANIFEST_FILE_NAME,
    EvidenceLedgerSummaryError,
    build_delta,
    load_candidates,
    load_source_observations,
    normalize_evidence_summaries,
    validate_delta_path,
)
from runtime.local.source_observation_cache import (
    MANIFEST_FILE_NAME as SOURCE_OBSERVATION_MANIFEST_FILE_NAME,
)
from runtime.local.source_observation_cache import (
    build_delta as build_source_observation_delta,
)


ROOT = Path(__file__).resolve().parents[2]
SMOKE_REPORT = ROOT / "control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json"


class IAEvidenceLedgerSummaryTests(unittest.TestCase):
    def test_builds_summary_delta_from_source_observation_and_candidate_deltas(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            result = build_delta(
                source="ia_metadata",
                source_observation_delta_path=source_delta,
                candidate_index_delta_path=candidate_delta,
                out_dir=Path(tmp) / "evidence-delta",
            )

        manifest = result["manifest"]
        self.assertEqual("PASS_WITH_WARNINGS", result["status"])
        self.assertEqual(56, manifest["source_observation_count"])
        self.assertEqual(56, manifest["candidate_count"])
        self.assertEqual(344, manifest["evidence_summary_count"])
        self.assertEqual(7, manifest["query_count"])
        self.assertEqual(["fixture", "live"], manifest["provider_modes"])
        self.assertEqual("REVIEW-IA-CANDIDATES-BATCH-00", manifest["recommended_next_task"])

    def test_validates_input_hashes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            candidate_manifest = json.loads(candidate_delta.read_text(encoding="utf-8"))
            candidate_manifest["input_source_observation_delta_hash"] = "sha256:bogus"
            candidate_delta.write_text(json.dumps(candidate_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            with self.assertRaises(EvidenceLedgerSummaryError):
                build_delta(
                    source="ia_metadata",
                    source_observation_delta_path=source_delta,
                    candidate_index_delta_path=candidate_delta,
                    out_dir=Path(tmp) / "evidence-delta",
                )

    def test_assigns_stable_evidence_summary_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            rows = _read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)

        ids = [row["evidence_summary_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.startswith("evidence-summary:ia_metadata:") for item in ids))

    def test_writes_evidence_summary_data_manifest_and_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)

            self.assertTrue((out / EVIDENCE_SUMMARY_FILE_NAME).is_file())
            self.assertTrue((out / MANIFEST_FILE_NAME).is_file())
            self.assertTrue((out / "EVIDENCE_LEDGER_SUMMARY_REPORT.md").is_file())
            self.assertEqual(344, len(_read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)))

    def test_strict_validation_passes_for_valid_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            validation = validate_delta_path(out / MANIFEST_FILE_NAME, strict=True)

        self.assertEqual("PASS", validation["status"], validation)
        self.assertEqual(0, validation["unsafe_record_count"])

    def test_status_command_reports_counts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_evidence_ledger_summary.py",
                    "status",
                    "--delta",
                    str(out / MANIFEST_FILE_NAME),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("evidence_summaries: 344", completed.stdout)
        self.assertIn("source_observations: 56", completed.stdout)
        self.assertIn("accepted_truth_created: false", completed.stdout)

    def test_repeated_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            first_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            first_rows = (out / EVIDENCE_SUMMARY_FILE_NAME).read_text(encoding="utf-8")
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            second_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            second_rows = (out / EVIDENCE_SUMMARY_FILE_NAME).read_text(encoding="utf-8")

        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(first_rows, second_rows)

    def test_source_and_candidate_refs_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            rows = _read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)

        self.assertTrue(all(row["source_observation_refs"] for row in rows))
        self.assertTrue(all(row["candidate_refs"] for row in rows))
        self.assertTrue(all(row["source_observation_refs"][0].startswith("source-observation:ia_metadata:") for row in rows))
        self.assertTrue(all(row["candidate_refs"][0].startswith("candidate:ia_metadata:") for row in rows))

    def test_all_entries_remain_provisional_and_unreviewed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            rows = _read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)

        self.assertTrue(all(row["evidence_status"] == "provisional" for row in rows))
        self.assertTrue(all(row["review_state"] == "unreviewed" for row in rows))
        self.assertTrue(all(row["authority"] == "evidence_summary_only" for row in rows))

    def test_only_source_supported_fields_produce_summaries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            source_manifest = json.loads(source_delta.read_text(encoding="utf-8"))
            candidate_manifest = json.loads(candidate_delta.read_text(encoding="utf-8"))
            source_observations = load_source_observations(source_delta, source_manifest)
            candidates = load_candidates(candidate_delta, candidate_manifest)
            candidate = dict(candidates[0])
            candidate["candidate_id"] = "candidate:ia_metadata:without-platform"
            candidate["platform_time_version_hints"] = []
            summaries = normalize_evidence_summaries(
                source_observations=source_observations,
                candidates=[candidate],
                source_manifest=source_manifest,
                candidate_manifest=candidate_manifest,
                source_delta_hash=_file_hash(source_delta),
                candidate_delta_hash=_file_hash(candidate_delta),
            )

        evidence_types = {row["evidence_type"] for row in summaries}
        self.assertNotIn("date/time clue", evidence_types)
        self.assertNotIn("platform clue", evidence_types)
        self.assertTrue(all(row["supporting_fields"] for row in summaries))

    def test_zero_result_unavailable_state_does_not_create_false_object_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            result = build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            rows = _read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)

        self.assertEqual("zero_results", result["manifest"]["live_probe_statuses_preserved"][0]["probe_status"])
        self.assertFalse(result["manifest"]["live_probe_statuses_preserved"][0]["source_observation_created"])
        self.assertFalse(any(row.get("accepted_truth") for row in rows))
        self.assertFalse(result["manifest"]["accepted_truth_created"])

    def test_conflicting_metadata_is_marked_not_resolved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            source_manifest = json.loads(source_delta.read_text(encoding="utf-8"))
            candidate_manifest = json.loads(candidate_delta.read_text(encoding="utf-8"))
            source_observations = load_source_observations(source_delta, source_manifest)
            candidates = load_candidates(candidate_delta, candidate_manifest)
            left = dict(candidates[0])
            right = dict(candidates[0])
            right["candidate_id"] = "candidate:ia_metadata:conflicting-title"
            right["normalized_title"] = f"{left['normalized_title']} alternate"
            summaries = normalize_evidence_summaries(
                source_observations=source_observations,
                candidates=[left, right],
                source_manifest=source_manifest,
                candidate_manifest=candidate_manifest,
                source_delta_hash=_file_hash(source_delta),
                candidate_delta_hash=_file_hash(candidate_delta),
            )

        title_summaries = [row for row in summaries if row["evidence_type"] == "title/name clue"]
        self.assertTrue(title_summaries)
        self.assertTrue(all(row["support_posture"] == "conflicting" for row in title_summaries))
        self.assertTrue(all(row["contradiction_flags"] for row in title_summaries))

    def test_insufficient_support_remains_insufficient(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
            rows = _read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)

        insufficient = [row for row in rows if row["support_posture"] == "insufficient"]
        self.assertTrue(insufficient)
        self.assertTrue(all(row["review_required"] for row in insufficient))

    def test_unsafe_authoritative_wording_fails_validation(self) -> None:
        validation = _mutated_validation(lambda rows, _manifest: rows[0].__setitem__("normalized_support_summary", "This is verified artifact truth."))
        self.assertEqual("FAIL", validation["status"], validation)
        self.assertTrue(any("unsafe authoritative claim" in error for error in validation["errors"]))

    def test_rights_safe_verified_claims_fail_validation(self) -> None:
        validation = _mutated_validation(
            lambda rows, _manifest: rows[0].__setitem__("proposition", "Rights are cleared and this is safe to download as a verified artifact.")
        )
        self.assertEqual("FAIL", validation["status"], validation)
        self.assertTrue(any("unsafe authoritative claim" in error for error in validation["errors"]))

    def test_orphan_refs_fail_validation(self) -> None:
        for field, value in (
            ("candidate_refs", ["candidate:ia_metadata:missing"]),
            ("source_observation_refs", ["source-observation:ia_metadata:missing"]),
        ):
            with self.subTest(field=field):
                validation = _mutated_validation(lambda rows, _manifest, field=field, value=value: rows[0].__setitem__(field, value))
                self.assertEqual("FAIL", validation["status"], validation)

    def test_mutation_flags_fail_closed(self) -> None:
        cases = (
            "reviewed_master_mutation",
            "public_index_mutation",
            "candidate_index_store_mutation",
            "evidence_ledger_store_mutation",
            "review_promotion_mutation",
            "accepted_truth_created",
            "no_public_fanout",
            "no_downloads",
            "no_file_fetch",
            "no_wayback_replay",
        )
        true_when_bad = {
            "reviewed_master_mutation",
            "public_index_mutation",
            "candidate_index_store_mutation",
            "evidence_ledger_store_mutation",
            "review_promotion_mutation",
            "accepted_truth_created",
        }
        for field in cases:
            with self.subTest(field=field):
                validation = _mutated_validation(lambda _rows, manifest, field=field: manifest.__setitem__(field, field in true_when_bad))
                self.assertEqual("FAIL", validation["status"], validation)

    def test_missing_input_delta_fails_cleanly(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_evidence_ledger_summary.py",
                "build-delta",
                "--source",
                "ia_metadata",
                "--source-observation-delta",
                "missing-source-observation-delta.json",
                "--candidate-index-delta",
                "missing-candidate-index-delta.json",
                "--out",
                ".eureka/source-wave/ia-metadata/evidence-ledger/test-missing",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("source-observation delta manifest not found", completed.stderr)

    def test_generated_delta_does_not_create_reviewed_or_review_ledger_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            result = build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)

            self.assertFalse((out / "reviewed_records.jsonl").exists())
            self.assertFalse((out / "review_ledger.jsonl").exists())
            self.assertFalse((out / "accepted_truth.json").exists())
            self.assertFalse(result["manifest"]["reviewed_master_mutation"])
            self.assertFalse(result["manifest"]["review_promotion_mutation"])
            self.assertFalse(result["manifest"]["evidence_ledger_store_mutation"])

    def test_build_delta_makes_no_network_or_provider_call(self) -> None:
        def fail_socket(*_args: object, **_kwargs: object) -> socket.socket:
            raise AssertionError("network socket should not be opened")

        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            with mock.patch("socket.socket", side_effect=fail_socket):
                result = build_delta(
                    source="ia_metadata",
                    source_observation_delta_path=source_delta,
                    candidate_index_delta_path=candidate_delta,
                    out_dir=Path(tmp) / "evidence-delta",
                )

        self.assertFalse(result["network_used"])
        self.assertFalse(result["provider_calls"])

    def test_cli_build_validate_status_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
            source_delta, candidate_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "evidence-delta"
            build = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_evidence_ledger_summary.py",
                    "build-delta",
                    "--source",
                    "ia_metadata",
                    "--source-observation-delta",
                    str(source_delta),
                    "--candidate-index-delta",
                    str(candidate_delta),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            validate = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_evidence_ledger_summary.py",
                    "validate",
                    "--delta",
                    str(out / MANIFEST_FILE_NAME),
                    "--strict",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("evidence_summaries_written: 344", build.stdout)
        self.assertIn("status: PASS", validate.stdout)


def _build_inputs(tmp: Path) -> tuple[Path, Path]:
    source_dir = tmp / "source-observation-delta"
    candidate_dir = tmp / "candidate-index-delta"
    build_source_observation_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=source_dir)
    source_manifest = source_dir / SOURCE_OBSERVATION_MANIFEST_FILE_NAME
    build_candidate_index_delta(source="ia_metadata", source_observation_delta_path=source_manifest, out_dir=candidate_dir)
    return source_manifest, candidate_dir / CANDIDATE_MANIFEST_FILE_NAME


def _mutated_validation(mutator: object) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="eureka-evidence-ledger-summary-") as tmp:
        source_delta, candidate_delta = _build_inputs(Path(tmp))
        out = Path(tmp) / "evidence-delta"
        build_delta(source="ia_metadata", source_observation_delta_path=source_delta, candidate_index_delta_path=candidate_delta, out_dir=out)
        rows = _read_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME)
        manifest = json.loads((out / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
        mutator(rows, manifest)  # type: ignore[misc]
        _write_jsonl(out / EVIDENCE_SUMMARY_FILE_NAME, rows)
        (out / MANIFEST_FILE_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return validate_delta_path(out / MANIFEST_FILE_NAME, strict=True)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _file_hash(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
