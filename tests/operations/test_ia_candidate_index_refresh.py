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
    MANIFEST_FILE_NAME,
    build_delta,
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


class IACandidateIndexRefreshTests(unittest.TestCase):
    def test_builds_candidate_index_delta_from_source_observation_cache_delta(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            result = build_delta(
                source="ia_metadata",
                source_observation_delta_path=source_delta,
                out_dir=Path(tmp) / "candidate-delta",
            )

        manifest = result["manifest"]
        self.assertEqual("PASS_WITH_WARNINGS", result["status"])
        self.assertEqual(56, manifest["source_observation_count"])
        self.assertEqual(56, manifest["candidate_count"])
        self.assertEqual(7, manifest["query_count"])
        self.assertEqual(["fixture", "live"], manifest["provider_modes"])
        self.assertEqual("IA-EVIDENCE-LEDGER-SUMMARY-00", manifest["recommended_next_task"])
        self.assertFalse(manifest["reviewed_master_mutation"])
        self.assertFalse(manifest["public_index_mutation"])
        self.assertFalse(manifest["candidate_index_store_mutation"])
        self.assertFalse(manifest["evidence_ledger_mutation"])
        self.assertFalse(manifest["review_promotion_mutation"])

    def test_assigns_stable_source_family_scoped_candidate_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            rows = _read_jsonl(out / CANDIDATE_FILE_NAME)

        ids = [row["candidate_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.startswith("candidate:ia_metadata:") for item in ids))

    def test_writes_jsonl_manifest_and_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)

            self.assertTrue((out / CANDIDATE_FILE_NAME).is_file())
            self.assertTrue((out / MANIFEST_FILE_NAME).is_file())
            self.assertTrue((out / "CANDIDATE_INDEX_REFRESH_REPORT.md").is_file())
            self.assertEqual(56, len(_read_jsonl(out / CANDIDATE_FILE_NAME)))

    def test_validates_manifest_strict(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            validation = validate_delta_path(out / MANIFEST_FILE_NAME, strict=True)

        self.assertEqual("PASS", validation["status"], validation)
        self.assertEqual(0, validation["unsafe_record_count"])

    def test_status_command_reports_counts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_candidate_index_refresh.py",
                    "status",
                    "--delta",
                    str(out / MANIFEST_FILE_NAME),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("candidates: 56", completed.stdout)
        self.assertIn("queries: 7", completed.stdout)
        self.assertIn("candidate_index_store_mutation: false", completed.stdout)

    def test_rerun_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            first_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            first_rows = (out / CANDIDATE_FILE_NAME).read_text(encoding="utf-8")
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            second_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            second_rows = (out / CANDIDATE_FILE_NAME).read_text(encoding="utf-8")

        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(first_rows, second_rows)

    def test_candidates_preserve_source_observation_refs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            rows = _read_jsonl(out / CANDIDATE_FILE_NAME)

        self.assertTrue(all(row["source_observation_refs"] for row in rows))
        self.assertTrue(all(row["source_observation_refs"][0].startswith("source-observation:ia_metadata:") for row in rows))

    def test_candidates_are_all_provisional_and_unreviewed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            rows = _read_jsonl(out / CANDIDATE_FILE_NAME)

        self.assertTrue(all(row["candidate_status"] == "provisional" for row in rows))
        self.assertTrue(all(row["candidate_authority"] == "candidate_only" for row in rows))
        self.assertTrue(all(row["review_state"] == "unreviewed" for row in rows))

    def test_unsafe_downloaded_or_payload_fields_fail_validation(self) -> None:
        for field in ("downloaded_files", "payload_bytes", "secret_tokens"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
                    source_delta = _build_source_delta(Path(tmp))
                    out = Path(tmp) / "candidate-delta"
                    build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
                    rows = _read_jsonl(out / CANDIDATE_FILE_NAME)
                    rows[0][field] = ["forbidden"]
                    _write_jsonl(out / CANDIDATE_FILE_NAME, rows)

                    validation = validate_delta_path(out / MANIFEST_FILE_NAME, strict=True)

                self.assertEqual("FAIL", validation["status"], validation)

    def test_mutation_flags_fail_closed(self) -> None:
        cases = (
            "reviewed_master_mutation",
            "public_index_mutation",
            "candidate_index_store_mutation",
            "evidence_ledger_mutation",
            "review_promotion_mutation",
            "no_public_fanout",
            "no_downloads",
            "no_file_fetch",
            "no_wayback_replay",
        )
        for field in cases:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
                    source_delta = _build_source_delta(Path(tmp))
                    out = Path(tmp) / "candidate-delta"
                    build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
                    manifest = json.loads((out / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
                    manifest[field] = field not in {
                        "no_public_fanout",
                        "no_downloads",
                        "no_file_fetch",
                        "no_wayback_replay",
                    }
                    (out / MANIFEST_FILE_NAME).write_text(
                        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )

                    validation = validate_delta_path(out / MANIFEST_FILE_NAME, strict=True)

                self.assertEqual("FAIL", validation["status"], validation)

    def test_missing_source_observation_delta_fails_cleanly(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_candidate_index_refresh.py",
                "build-delta",
                "--source",
                "ia_metadata",
                "--source-observation-delta",
                "missing-source-observation-delta.json",
                "--out",
                ".eureka/source-wave/ia-metadata/candidate-index/test-missing",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("source-observation delta manifest not found", completed.stderr)

    def test_redacted_live_zero_result_state_does_not_create_false_truth(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)
            rows = _read_jsonl(out / CANDIDATE_FILE_NAME)

        self.assertEqual(56, len(rows))
        self.assertFalse(any(row.get("accepted_truth") for row in rows))
        self.assertTrue(all(row["review_state"] == "unreviewed" for row in rows))

    def test_generated_delta_does_not_create_reviewed_public_or_evidence_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            result = build_delta(source="ia_metadata", source_observation_delta_path=source_delta, out_dir=out)

            self.assertFalse((out / "reviewed_records.jsonl").exists())
            self.assertFalse((out / "public_snapshot_index.json").exists())
            self.assertFalse((out / "evidence_ledger.json").exists())
            self.assertFalse(result["manifest"]["reviewed_master_mutation"])
            self.assertFalse(result["manifest"]["public_index_mutation"])
            self.assertFalse(result["manifest"]["evidence_ledger_mutation"])

    def test_build_delta_makes_no_network_or_provider_call(self) -> None:
        def fail_socket(*_args: object, **_kwargs: object) -> socket.socket:
            raise AssertionError("network socket should not be opened")

        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            with mock.patch("socket.socket", side_effect=fail_socket):
                result = build_delta(
                    source="ia_metadata",
                    source_observation_delta_path=source_delta,
                    out_dir=Path(tmp) / "candidate-delta",
                )

        self.assertFalse(result["network_used"])
        self.assertFalse(result["provider_calls"])

    def test_cli_build_validate_status_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-candidate-index-refresh-") as tmp:
            source_delta = _build_source_delta(Path(tmp))
            out = Path(tmp) / "candidate-delta"
            build = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_candidate_index_refresh.py",
                    "build-delta",
                    "--source",
                    "ia_metadata",
                    "--source-observation-delta",
                    str(source_delta),
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
                    "scripts/eureka_candidate_index_refresh.py",
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

        self.assertIn("candidates_written: 56", build.stdout)
        self.assertIn("status: PASS", validate.stdout)


def _build_source_delta(tmp: Path) -> Path:
    source_dir = tmp / "source-observation-delta"
    build_source_observation_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=source_dir)
    return source_dir / SOURCE_OBSERVATION_MANIFEST_FILE_NAME


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
