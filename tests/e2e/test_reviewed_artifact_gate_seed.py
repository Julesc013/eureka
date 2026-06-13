from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.artifact_gate_seed import read_jsonl, validate_evidence_packet
from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, write_index
from scripts.eureka_artifact_gate import main as artifact_gate_main
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from scripts.eureka_staging import main as staging_main


QUERY = "manual for Sound Blaster CT1740"


class ReviewedArtifactGateSeedTests(unittest.TestCase):
    def test_candidates_command_writes_deterministic_seed_candidates(self) -> None:
        with _ArtifactGateDemo() as demo:
            first = demo.root / "candidates-first.jsonl"
            second = demo.root / "candidates-second.jsonl"
            first_result = _run_artifact_gate_main("candidates", "--index", str(demo.reviewed_index_path), "--out", str(first))
            second_result = _run_artifact_gate_main("candidates", "--index", str(demo.reviewed_index_path), "--out", str(second))
            rows = read_jsonl(first)
            first_text = first.read_text(encoding="utf-8")
            second_text = second.read_text(encoding="utf-8")

        self.assertEqual(first_result.code, 0, first_result.stderr)
        self.assertEqual(second_result.code, 0, second_result.stderr)
        self.assertEqual(first_text, second_text)
        self.assertGreater(len(rows), 0)
        manual = _find_candidate(rows, "manual for sound blaster")
        self.assertFalse(manual["artifact_gate_excluded"])
        self.assertFalse(manual["gate_eligible"])
        self.assertFalse(manual["artifact_verified"])
        driver = _find_candidate(rows, "driver for win98")
        self.assertTrue(driver["artifact_gate_excluded"])
        self.assertEqual(driver["gate_exclusion_reason"], "hardware_details_missing")
        windows = _find_candidate(rows, "windows 7 apps")
        self.assertTrue(windows["artifact_gate_excluded"])
        self.assertEqual(windows["gate_exclusion_reason"], "broad_collection_query")

    def test_evidence_template_writes_required_fields(self) -> None:
        with _ArtifactGateDemo() as demo:
            candidates = demo.root / "candidates.jsonl"
            templates = demo.root / "evidence_template.jsonl"
            _run_artifact_gate_main("candidates", "--index", str(demo.reviewed_index_path), "--out", str(candidates))
            result = _run_artifact_gate_main("evidence-template", "--candidates", str(candidates), "--out", str(templates))
            rows = read_jsonl(templates)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertGreater(len(rows), 0)
        first = rows[0]
        for key in (
            "evidence_packet_id",
            "candidate_id",
            "artifact_title",
            "artifact_identity_fields",
            "source_observations",
            "reviewer",
            "review_rationale",
            "artifact_verified",
            "gate_eligible",
        ):
            self.assertIn(key, first)
        self.assertFalse(first["artifact_verified"])
        self.assertFalse(first["gate_eligible"])

    def test_validate_evidence_rejects_missing_required_manual_review_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "invalid.json"
            _write_json(
                path,
                {
                    "evidence_packet_id": "packet:missing",
                    "candidate_id": "candidate:missing",
                    "artifact_title": "Missing fields",
                    "no_download_performed": True,
                },
            )
            result = _run_artifact_gate_main("validate-evidence", "--evidence", str(path), "--json")

        self.assertEqual(result.code, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any("reviewer is required" in error for error in payload["errors"]))
        self.assertTrue(any("review_rationale is required" in error for error in payload["errors"]))
        self.assertTrue(any("source identity" in error for error in payload["errors"]))

    def test_validate_evidence_rejects_fixture_only_verified_claim(self) -> None:
        packet = _valid_source_lead_packet()
        packet["artifact_verified"] = True
        packet["gate_eligible"] = True
        packet["verification_scope"] = "manual_external_artifact_identity_verified"
        errors = validate_evidence_packet(packet)

        self.assertTrue(any("fixture-only" in error for error in errors))

    def test_validate_evidence_rejects_verified_claim_without_verification_scope(self) -> None:
        packet = _valid_source_lead_packet()
        packet["source_authority"] = "independent_external_evidence"
        packet["provenance"] = {}
        packet["artifact_verified"] = True
        packet["gate_eligible"] = True
        packet["verification_scope"] = "source_lead_only"
        errors = validate_evidence_packet(packet)

        self.assertTrue(any("stronger verification_scope" in error for error in errors))

    def test_validate_evidence_allows_non_verified_source_lead_packet(self) -> None:
        packet = _valid_source_lead_packet()
        errors = validate_evidence_packet(packet)

        self.assertEqual(errors, [])

    def test_seed_creates_gate_reports_without_verified_truth(self) -> None:
        with _ArtifactGateDemo() as demo:
            result = _run_artifact_gate_main(
                "seed",
                "--index",
                str(demo.reviewed_index_path),
                "--out",
                str(demo.gate_path),
                "--max-records",
                "5",
            )
            validate = _run_artifact_gate_main("validate", "--gate", str(demo.gate_path), "--json")
            status = _run_artifact_gate_main("status", "--gate", str(demo.gate_path))
            report = _load_json(demo.gate_path / "artifact_gate_report.json")
            records = read_jsonl(demo.gate_path / "reviewed_artifact_records.jsonl")

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertIn("gate status: blocked", status.stdout)
        self.assertEqual(report["status"], "PASS_WITH_WARNINGS")
        self.assertEqual(report["gate_status"], "blocked")
        self.assertEqual(report["reviewed_artifact_gate_count"], 0)
        self.assertEqual(report["artifact_verified_count"], 0)
        self.assertGreater(len(records), 0)
        self.assertTrue(all(record["artifact_verified"] is False for record in records))
        self.assertTrue(all(record["binary_verified"] is False for record in records))
        self.assertTrue(all(record["download_safe"] is False for record in records))
        self.assertTrue(all(record["execution_safe"] is False for record in records))
        self.assertTrue(all(record["source_observations"] for record in records))
        self.assertTrue(all(record["provenance"] for record in records))

    def test_validate_catches_inconsistent_report_counts(self) -> None:
        with _ArtifactGateDemo() as demo:
            _run_artifact_gate_main("seed", "--index", str(demo.reviewed_index_path), "--out", str(demo.gate_path))
            report_path = demo.gate_path / "artifact_gate_report.json"
            report = _load_json(report_path)
            report["artifact_verified_count"] = 99
            _write_json(report_path, report)
            result = _run_artifact_gate_main("validate", "--gate", str(demo.gate_path), "--json")

        self.assertEqual(result.code, 1)
        payload = json.loads(result.stdout)
        self.assertTrue(any("artifact_verified_count" in error for error in payload["errors"]))

    def test_export_launch_report_writes_consumable_report(self) -> None:
        with _ArtifactGateDemo() as demo:
            _run_artifact_gate_main("seed", "--index", str(demo.reviewed_index_path), "--out", str(demo.gate_path))
            out = demo.root / "artifact_gate_report.exported.json"
            result = _run_artifact_gate_main("export-launch-report", "--gate", str(demo.gate_path), "--out", str(out))
            exported = _load_json(out)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(exported["task_id"], "REVIEWED-ARTIFACT-GATE-SEED-00")
        self.assertEqual(exported["gate_status"], "blocked")
        self.assertEqual(exported["reviewed_artifact_gate_count"], 0)

    def test_launch_gate_consumes_seed_report_without_marking_launch_ready(self) -> None:
        with _ArtifactGateDemo() as demo:
            _run_artifact_gate_main("seed", "--index", str(demo.reviewed_index_path), "--out", str(demo.gate_path))
            _write_staging_and_rehearsal(demo)
            result = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--artifact-gate-report",
                str(demo.gate_path / "artifact_gate_report.json"),
                "--out",
                str(demo.launch_gate_path),
            )
            report = _load_json(demo.launch_gate_path / "launch_gate_report.json")

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["launch_status"], "BLOCKED")
        self.assertEqual(report["official_reviewed_artifact_gate_status"], "fail")
        self.assertEqual(report["official_reviewed_artifact_count"], 0)
        self.assertNotIn("artifact_gate_authority_unknown", report["blocker_categories"]["unknown_authority_blockers"])
        self.assertIn("official_reviewed_artifact_gate_not_passed", report["blocker_categories"]["corpus_evidence_blockers"])

    def test_launch_gate_with_seed_report_does_not_mutate_inputs(self) -> None:
        with _ArtifactGateDemo() as demo:
            _run_artifact_gate_main("seed", "--index", str(demo.reviewed_index_path), "--out", str(demo.gate_path))
            _write_staging_and_rehearsal(demo)
            watched = [
                demo.reviewed_index_path,
                demo.gate_path / "artifact_gate_report.json",
                demo.gate_path / "reviewed_artifact_records.jsonl",
                demo.bundle_path / "manifest.json",
                demo.bundle_path / "public_search_index.json",
                demo.rehearsal_report_path,
            ]
            before = {path: _sha256(path) for path in watched}
            _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--artifact-gate-report",
                str(demo.gate_path / "artifact_gate_report.json"),
                "--out",
                str(demo.launch_gate_path),
            )
            after = {path: _sha256(path) for path in watched}

        self.assertEqual(before, after)


class _ArtifactGateDemo:
    def __enter__(self) -> "_ArtifactGateDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self._temp_dir.name)
        self.index_path = self.root / "local_search_index.json"
        self.ledger_path = self.root / "local_review_ledger.jsonl"
        self.records_path = self.root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = self.root / "local_search_index.reviewed.json"
        self.gate_path = self.root / "artifact-gate"
        self.bundle_path = self.root / "public-alpha-bundle"
        self.rehearsal_path = self.root / "rehearsal"
        self.rehearsal_report_path = self.rehearsal_path / "rehearsal_report.json"
        self.launch_gate_path = self.root / "launch-gate"
        write_index(self.index_path, build_local_demo_index())
        accept_candidate(
            index_path=self.index_path,
            query=QUERY,
            ledger_path=self.ledger_path,
            records_path=self.records_path,
            reviewer="local_demo",
            reason="Artifact gate seed test reviewed source lead",
            reviewed_at="2026-06-13T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=self.records_path))
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


class _RunResult:
    def __init__(self, code: int, stdout: str, stderr: str):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


def _run_artifact_gate_main(*args: str) -> _RunResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = artifact_gate_main(args, stdout=stdout, stderr=stderr)
    return _RunResult(code, stdout.getvalue(), stderr.getvalue())


def _run_launch_gate_main(*args: str) -> _RunResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = launch_gate_main(args, stdout=stdout, stderr=stderr)
    return _RunResult(code, stdout.getvalue(), stderr.getvalue())


def _run_staging_main(*args: str) -> _RunResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = staging_main(args, stdout=stdout, stderr=stderr)
    return _RunResult(code, stdout.getvalue(), stderr.getvalue())


def _run_rehearsal_main(*args: str) -> _RunResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = rehearsal_main(args, stdout=stdout, stderr=stderr)
    return _RunResult(code, stdout.getvalue(), stderr.getvalue())


def _write_staging_and_rehearsal(demo: _ArtifactGateDemo) -> None:
    package = _run_staging_main("package", "--index", str(demo.reviewed_index_path), "--out", str(demo.bundle_path))
    if package.code != 0:
        raise AssertionError(package.stderr or package.stdout)
    rehearsal = _run_rehearsal_main(
        "run",
        "--bundle",
        str(demo.bundle_path),
        "--host",
        "127.0.0.1",
        "--port",
        "0",
        "--out",
        str(demo.rehearsal_path),
    )
    if rehearsal.code != 0:
        raise AssertionError(rehearsal.stderr or rehearsal.stdout)


def _find_candidate(rows: list[dict[str, object]], needle: str) -> dict[str, object]:
    needle = needle.casefold()
    for row in rows:
        text = json.dumps(row, sort_keys=True, ensure_ascii=True).casefold()
        if needle in text:
            return row
    raise AssertionError(f"candidate not found: {needle}")


def _valid_source_lead_packet() -> dict[str, object]:
    return {
        "schema_version": "eureka.artifact_gate_evidence_packet.v0",
        "evidence_packet_id": "packet:valid",
        "candidate_id": "candidate:valid",
        "source_index_document_id": "local-demo:fixture",
        "artifact_title": "Manual for Sound Blaster CT1740",
        "artifact_type": "manual",
        "platform_or_context": "Sound Blaster CT1740",
        "artifact_identity_fields": {
            "title": "Manual for Sound Blaster CT1740",
            "source_index_document_id": "local-demo:fixture",
        },
        "source_observations": [{"kind": "source_hint", "value": "fixture source"}],
        "source_hints": ["internet_archive_metadata"],
        "evidence_hints": ["metadata title observation"],
        "evidence_type": "source_metadata_lead",
        "source_authority": "archive_metadata_fixture",
        "observed_fields": ["title", "source_hints"],
        "reviewer": "local_reviewer",
        "review_rationale": "Non-verified source lead only.",
        "no_download_performed": True,
        "file_fetch_performed": False,
        "binary_verified": False,
        "download_safe": False,
        "execution_safe": False,
        "rights_cleared": False,
        "verification_scope": "source_lead_only",
        "artifact_verified": False,
        "gate_eligible": False,
        "gate_exclusion_reason": "manual_external_evidence_required",
        "provenance": {"source_kind": "ia_metadata_fixture"},
    }


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
