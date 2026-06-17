from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime.local.source_observation_cache import (
    MANIFEST_FILE_NAME,
    OBSERVATION_FILE_NAME,
    SourceObservationCacheError,
    build_delta,
    validate_delta_path,
)


ROOT = Path(__file__).resolve().parents[2]
SMOKE_REPORT = ROOT / "control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json"


class IASourceObservationCacheDeltaTests(unittest.TestCase):
    def test_builds_delta_from_ia_smoke_report_fixture(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            result = build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=Path(tmp) / "delta")

            manifest = result["manifest"]
            self.assertEqual("PASS_WITH_WARNINGS", result["status"])
            self.assertEqual(56, manifest["observation_count"])
            self.assertEqual(7, manifest["query_count"])
            self.assertEqual(["fixture", "live"], manifest["provider_modes_represented"])
            self.assertEqual("IA-CANDIDATE-INDEX-REFRESH-00", manifest["recommended_next_task"])
            self.assertFalse(manifest["reviewed_master_mutation"])
            self.assertFalse(manifest["public_index_mutation"])
            self.assertFalse(manifest["candidate_index_mutation"])
            self.assertFalse(manifest["evidence_ledger_mutation"])

    def test_assigns_stable_source_family_scoped_observation_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)
            rows = _read_jsonl(out / OBSERVATION_FILE_NAME)

        ids = [row["observation_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.startswith("source-observation:ia_metadata:") for item in ids))

    def test_writes_jsonl_manifest_and_report(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)

            self.assertTrue((out / OBSERVATION_FILE_NAME).is_file())
            self.assertTrue((out / MANIFEST_FILE_NAME).is_file())
            self.assertTrue((out / "SOURCE_OBSERVATION_CACHE_DELTA_REPORT.md").is_file())
            self.assertEqual(56, len(_read_jsonl(out / OBSERVATION_FILE_NAME)))

    def test_validates_manifest_strict(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)
            validation = validate_delta_path(out / MANIFEST_FILE_NAME, strict=True)

        self.assertEqual("PASS", validation["status"], validation)
        self.assertEqual(0, validation["unsafe_record_count"])

    def test_status_command_reports_counts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_source_observation_cache.py",
                    "status",
                    "--delta",
                    str(out / MANIFEST_FILE_NAME),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("observations: 56", completed.stdout)
        self.assertIn("queries: 7", completed.stdout)
        self.assertIn("candidate_index_mutation: false", completed.stdout)

    def test_rerun_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)
            first_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            first_rows = (out / OBSERVATION_FILE_NAME).read_text(encoding="utf-8")
            build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)
            second_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            second_rows = (out / OBSERVATION_FILE_NAME).read_text(encoding="utf-8")

        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(first_rows, second_rows)

    def test_unsafe_downloaded_or_payload_fields_fail_validation(self) -> None:
        for field in ("downloaded_files", "payload_bytes", "secret_tokens"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
                    smoke = _mutated_smoke(tmp, **{field: ["forbidden"]})
                    with self.assertRaises(SourceObservationCacheError):
                        build_delta(source="ia_metadata", smoke_report_path=smoke, out_dir=Path(tmp) / "delta")

    def test_mutation_flags_fail_closed(self) -> None:
        cases = (
            ("reviewed/master", lambda payload: payload["safety"].__setitem__("reviewed_master_index_mutation", True)),
            ("public-index", lambda payload: payload.__setitem__("public_index_mutation", True)),
            ("candidate-index", lambda payload: payload["candidate_index_delta"].__setitem__("candidate_index_mutated", True)),
            ("evidence-ledger", lambda payload: payload.__setitem__("evidence_ledger_mutation", True)),
            ("public-fanout", lambda payload: payload["safety"].__setitem__("public_fanout", True)),
        )
        for label, mutate in cases:
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
                    smoke = _mutated_smoke(tmp, mutator=mutate)
                    with self.assertRaises(SourceObservationCacheError):
                        build_delta(source="ia_metadata", smoke_report_path=smoke, out_dir=Path(tmp) / "delta")

    def test_no_download_no_file_fetch_no_wayback_flags_are_enforced(self) -> None:
        cases = (
            ("downloads", lambda payload: payload["safety"].__setitem__("downloads", True)),
            ("file_fetching", lambda payload: payload["safety"].__setitem__("file_fetching", True)),
            ("wayback_replay", lambda payload: payload["safety"].__setitem__("wayback_replay", True)),
        )
        for label, mutate in cases:
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
                    smoke = _mutated_smoke(tmp, mutator=mutate)
                    with self.assertRaises(SourceObservationCacheError):
                        build_delta(source="ia_metadata", smoke_report_path=smoke, out_dir=Path(tmp) / "delta")

    def test_missing_smoke_report_fails_cleanly(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_source_observation_cache.py",
                "build-delta",
                "--source",
                "ia_metadata",
                "--smoke-report",
                "missing-smoke-report.json",
                "--out",
                ".eureka/source-wave/ia-metadata/source-observation-cache/test-missing",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("smoke report not found", completed.stderr)

    def test_redacted_live_zero_result_state_is_preserved_as_status_not_truth(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            result = build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=Path(tmp) / "delta")
            statuses = result["manifest"]["live_probe_statuses"]

        self.assertEqual("zero_results", statuses[0]["probe_status"])
        self.assertFalse(statuses[0]["source_observation_created"])
        self.assertEqual("not_truth", statuses[0]["truth_status"])

    def test_generated_delta_does_not_create_reviewed_records_or_indexes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            result = build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=out)
            rows = _read_jsonl(out / OBSERVATION_FILE_NAME)

            self.assertFalse((out / "candidate_index.json").exists())
            self.assertFalse((out / "evidence_ledger.json").exists())
            self.assertFalse((out / "reviewed_records.jsonl").exists())
            self.assertFalse(result["manifest"]["candidate_index_mutation"])
            self.assertFalse(result["manifest"]["evidence_ledger_mutation"])
            self.assertTrue(all(row["review_state"] == "unreviewed" for row in rows))
            self.assertTrue(all(row["authority"] == "source_observation_only" for row in rows))

    def test_build_delta_makes_no_network_or_provider_call(self) -> None:
        def fail_socket(*_args: object, **_kwargs: object) -> socket.socket:
            raise AssertionError("network socket should not be opened")

        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            with mock.patch("socket.socket", side_effect=fail_socket):
                result = build_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=Path(tmp) / "delta")

        self.assertFalse(result["network_used"])
        self.assertFalse(result["provider_calls"])

    def test_cli_build_validate_status_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-source-observation-cache-") as tmp:
            out = Path(tmp) / "delta"
            build = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_source_observation_cache.py",
                    "build-delta",
                    "--source",
                    "ia_metadata",
                    "--smoke-report",
                    str(SMOKE_REPORT),
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
                    "scripts/eureka_source_observation_cache.py",
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

        self.assertIn("observations_written: 56", build.stdout)
        self.assertIn("status: PASS", validate.stdout)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _mutated_smoke(
    tmp: str,
    mutator: object | None = None,
    **updates: object,
) -> Path:
    payload = json.loads(SMOKE_REPORT.read_text(encoding="utf-8"))
    if callable(mutator):
        mutator(payload)
    payload.update(updates)
    path = Path(tmp) / "smoke.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


if __name__ == "__main__":
    unittest.main()
