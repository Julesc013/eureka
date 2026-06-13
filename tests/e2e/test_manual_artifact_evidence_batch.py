from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.artifact_gate_seed import read_jsonl
from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, write_index
from scripts.eureka_artifact_gate import main as artifact_gate_main
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from scripts.eureka_staging import main as staging_main


QUERY = "manual for Sound Blaster CT1740"


class ManualArtifactEvidenceBatchTests(unittest.TestCase):
    def test_manual_plan_and_template_are_deterministic(self) -> None:
        with _ManualBatchDemo() as demo:
            first = _run_artifact_gate_main(
                "manual-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--out",
                str(demo.batch_path),
                "--target-records",
                "5",
            )
            first_plan = (demo.batch_path / "candidate_plan.jsonl").read_text(encoding="utf-8")
            second = _run_artifact_gate_main(
                "manual-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--out",
                str(demo.batch_path),
                "--target-records",
                "5",
            )
            second_plan = (demo.batch_path / "candidate_plan.jsonl").read_text(encoding="utf-8")
            template = _run_artifact_gate_main(
                "manual-template",
                "--batch",
                str(demo.batch_path),
                "--out",
                str(demo.batch_path / "manual_evidence_template.jsonl"),
            )
            rows = read_jsonl(demo.batch_path / "manual_evidence_template.jsonl")
            plan_rows = read_jsonl(demo.batch_path / "candidate_plan.jsonl")

        self.assertEqual(first.code, 0, first.stderr)
        self.assertEqual(second.code, 0, second.stderr)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(first_plan, second_plan)
        self.assertGreater(len(rows), 0)
        self.assertTrue(all("batch_id" in row for row in rows))
        self.assertTrue(any(row["manual_batch_selected"] for row in plan_rows))
        driver = _find_candidate(plan_rows, "driver for win98")
        self.assertTrue(driver["artifact_gate_excluded"])
        self.assertEqual(driver["gate_exclusion_reason"], "hardware_details_missing")
        windows = _find_candidate(plan_rows, "windows 7 apps")
        self.assertTrue(windows["artifact_gate_excluded"])
        self.assertEqual(windows["gate_exclusion_reason"], "broad_collection_query")

    def test_manual_validate_reports_missing_evidence_without_fabricating_records(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            validate = _run_artifact_gate_main("manual-validate", "--batch", str(demo.batch_path), "--json")
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "manual_batch_01",
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
            validation_payload = json.loads(validate.stdout)
            review_payload = json.loads(review.stdout)
            report_payload = json.loads(report.stdout)

        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(review.code, 0, review.stderr)
        self.assertEqual(report.code, 0, report.stderr)
        self.assertEqual(validation_payload["status"], "pass_with_warnings")
        self.assertIn("missing evidence packets", " ".join(validation_payload["warnings"]))
        self.assertEqual(review_payload["reviewed_artifact_record_count"], 0)
        self.assertEqual(report_payload["artifact_verified_count"], 0)
        self.assertEqual(report_payload["reviewed_artifact_gate_count"], 0)
        self.assertEqual(report_payload["gate_status"], "blocked")

    def test_manual_ingest_accepts_valid_non_verified_source_lead_packet(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            packet = _valid_source_lead_packet(demo)
            _write_jsonl(demo.root / "source_lead.jsonl", [packet])
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "source_lead.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "manual_batch_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_evidence_packet_count"], 1)
        self.assertEqual(review.code, 0, review.stderr)
        self.assertEqual(json.loads(review.stdout)["reviewed_artifact_record_count"], 0)

    def test_manual_ingest_rejects_missing_reviewer_rationale_and_source_identity(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            packet = _valid_source_lead_packet(demo)
            packet["reviewer"] = ""
            packet["review_rationale"] = ""
            packet["artifact_identity_fields"] = {}
            packet["source_observations"] = []
            packet["evidence_urls"] = []
            packet["source_identifiers"] = []
            _write_jsonl(demo.root / "invalid.jsonl", [packet])
            result = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "invalid.jsonl"),
                "--json",
            )
            payload = json.loads(result.stdout)

        self.assertEqual(result.code, 1)
        joined = "\n".join(payload["errors"])
        self.assertIn("reviewer is required", joined)
        self.assertIn("review_rationale is required", joined)
        self.assertIn("source identity", joined)

    def test_manual_ingest_rejects_insufficient_and_fixture_only_verified_claims(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            insufficient = _valid_eligible_packet(demo)
            insufficient["verification_scope"] = "source_lead_only"
            fixture_only = _valid_eligible_packet(demo)
            fixture_only["evidence_packet_id"] = "manual-fixture-only"
            fixture_only["source_authority"] = "archive_metadata_fixture"
            _write_jsonl(demo.root / "bad_verified.jsonl", [insufficient, fixture_only])
            result = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "bad_verified.jsonl"),
                "--json",
            )
            payload = json.loads(result.stdout)

        self.assertEqual(result.code, 1)
        joined = "\n".join(payload["errors"])
        self.assertIn("stronger verification_scope", joined)
        self.assertIn("fixture-only", joined)

    def test_manual_review_materializes_only_valid_eligible_packets(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            eligible = _valid_eligible_packet(demo)
            source_lead = _valid_source_lead_packet(demo)
            _write_jsonl(demo.root / "mixed.jsonl", [eligible, source_lead])
            ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.root / "mixed.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "manual_batch_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(review.code, 0, review.stderr)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertTrue(record["artifact_verified"])
        self.assertTrue(record["gate_eligible"])
        self.assertFalse(record["binary_verified"])
        self.assertFalse(record["download_safe"])
        self.assertFalse(record["execution_safe"])
        self.assertFalse(record["rights_cleared"])

    def test_manual_report_counts_packets_and_stays_blocked_below_target(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            _write_jsonl(demo.root / "eligible.jsonl", [_valid_eligible_packet(demo)])
            _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(demo.root / "eligible.jsonl"))
            _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "manual_batch_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
            )
            report = _run_artifact_gate_main(
                "manual-report",
                "--batch",
                str(demo.batch_path),
                "--out",
                str(demo.batch_path / "artifact_gate_report.json"),
                "--json",
            )
            status = _run_artifact_gate_main("manual-status", "--batch", str(demo.batch_path))
            payload = json.loads(report.stdout)

        self.assertEqual(report.code, 0, report.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertEqual(payload["artifact_verified_count"], 1)
        self.assertEqual(payload["reviewed_artifact_gate_count"], 1)
        self.assertEqual(payload["gate_status"], "blocked")
        self.assertIn("reviewed artifact gate count: 1/25", status.stdout)

    def test_launch_gate_consumes_manual_batch_report_and_remains_blocked(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            _write_jsonl(demo.root / "eligible.jsonl", [_valid_eligible_packet(demo)])
            _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(demo.root / "eligible.jsonl"))
            _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "manual_batch_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
            )
            _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
            _write_staging_and_rehearsal(demo)
            result = _run_launch_gate_main(
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
            report = _load_json(demo.launch_gate_path / "launch_gate_report.json")

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["launch_status"], "BLOCKED")
        self.assertEqual(report["official_reviewed_artifact_count"], 1)
        self.assertEqual(report["official_reviewed_artifact_gate_status"], "fail")
        self.assertNotIn("artifact_gate_authority_unknown", report["blocker_categories"]["unknown_authority_blockers"])

    def test_launch_gate_with_manual_report_does_not_mutate_inputs(self) -> None:
        with _ManualBatchDemo() as demo:
            demo.write_plan_and_template()
            _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
            _write_staging_and_rehearsal(demo)
            watched = [
                demo.seed_gate_path / "artifact_gate_report.json",
                demo.batch_path / "artifact_gate_report.json",
                demo.batch_path / "candidate_plan.jsonl",
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
                str(demo.batch_path / "artifact_gate_report.json"),
                "--out",
                str(demo.launch_gate_path),
            )
            after = {path: _sha256(path) for path in watched}

        self.assertEqual(before, after)


class _ManualBatchDemo:
    def __enter__(self) -> "_ManualBatchDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self._temp_dir.name)
        self.index_path = self.root / "local_search_index.json"
        self.ledger_path = self.root / "local_review_ledger.jsonl"
        self.records_path = self.root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = self.root / "local_search_index.reviewed.json"
        self.seed_gate_path = self.root / "public-alpha-seed"
        self.batch_path = self.root / "manual-batch-01"
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
            reason="Manual evidence batch test reviewed source lead",
            reviewed_at="2026-06-13T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=self.records_path))
        seed = _run_artifact_gate_main(
            "seed",
            "--index",
            str(self.reviewed_index_path),
            "--out",
            str(self.seed_gate_path),
            "--max-records",
            "5",
        )
        if seed.code != 0:
            raise AssertionError(seed.stderr or seed.stdout)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()

    def write_plan_and_template(self) -> None:
        plan = _run_artifact_gate_main("manual-plan", "--gate", str(self.seed_gate_path), "--out", str(self.batch_path), "--target-records", "5")
        if plan.code != 0:
            raise AssertionError(plan.stderr or plan.stdout)
        template = _run_artifact_gate_main(
            "manual-template",
            "--batch",
            str(self.batch_path),
            "--out",
            str(self.batch_path / "manual_evidence_template.jsonl"),
        )
        if template.code != 0:
            raise AssertionError(template.stderr or template.stdout)


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


def _write_staging_and_rehearsal(demo: _ManualBatchDemo) -> None:
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


def _valid_eligible_packet(demo: _ManualBatchDemo) -> dict[str, object]:
    candidate = _selected_candidate(demo)
    source_url = "https://support.example.invalid/creative/sound-blaster-ct1740-manual"
    return {
        "schema_version": "eureka.artifact_gate_evidence_packet.v0",
        "evidence_packet_id": "manual-evidence:eligible-ct1740",
        "batch_id": "manual-batch:manual-batch-01",
        "candidate_id": candidate["candidate_id"],
        "source_index_document_id": candidate["source_index_document_id"],
        "artifact_title": "Sound Blaster CT1740 User Manual",
        "artifact_type": "manual",
        "artifact_identity_fields": {
            "title": "Sound Blaster CT1740 User Manual",
            "identifier": "CT1740",
            "platform_or_context": "Sound Blaster CT1740",
        },
        "platform_or_context": "Sound Blaster CT1740",
        "source_observations": [
            {
                "source_id": "creative-support-ct1740-manual",
                "source_url": source_url,
                "source_title": "Sound Blaster CT1740 manual support page",
                "publisher_or_source_name": "Creative support",
                "observed_artifact_fields": ["title", "model", "manual"],
                "authority_classification": "primary_official_source",
                "observation_notes": "Identifies the CT1740 manual by model and title.",
                "access_method": "manual_page_observation",
                "live_network_used": False,
                "downloaded_file": False,
                "fetched_binary": False,
            }
        ],
        "evidence_urls": [source_url],
        "source_identifiers": ["CT1740"],
        "evidence_type": "manual_page_observation",
        "source_authority": "primary_official_source",
        "observed_fields": ["title", "model", "manual"],
        "reviewer": "manual_batch_01",
        "review_rationale": "Primary support-page metadata identifies a concrete CT1740 manual artifact.",
        "collected_at": "2026-06-14T00:00:00Z",
        "no_download_performed": True,
        "file_fetch_performed": False,
        "binary_verified": False,
        "download_safe": False,
        "execution_safe": False,
        "rights_cleared": False,
        "verification_scope": "artifact_identity_metadata",
        "artifact_verified": True,
        "gate_eligible": True,
        "gate_exclusion_reason": "",
        "source_hints": [source_url],
        "evidence_hints": ["manual page observation"],
        "provenance": {"source": "manual_evidence_test"},
    }


def _valid_source_lead_packet(demo: _ManualBatchDemo) -> dict[str, object]:
    packet = _valid_eligible_packet(demo)
    packet["evidence_packet_id"] = "manual-evidence:source-lead-ct1740"
    packet["source_authority"] = "stable_catalog_metadata"
    packet["verification_scope"] = "artifact_identity_candidate"
    packet["artifact_verified"] = False
    packet["gate_eligible"] = False
    packet["gate_exclusion_reason"] = "manual_external_evidence_required"
    return packet


def _selected_candidate(demo: _ManualBatchDemo) -> dict[str, object]:
    rows = read_jsonl(demo.batch_path / "candidate_plan.jsonl")
    for row in rows:
        if row.get("manual_batch_selected") is True and row.get("artifact_gate_excluded") is not True:
            return row
    raise AssertionError("no selected candidate")


def _find_candidate(rows: list[dict[str, object]], needle: str) -> dict[str, object]:
    needle = needle.casefold()
    for row in rows:
        if needle in json.dumps(row, sort_keys=True, ensure_ascii=True).casefold():
            return row
    raise AssertionError(f"candidate not found: {needle}")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True, ensure_ascii=True) for row in rows) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
