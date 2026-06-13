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


class ArtifactEvidenceSourceCollectionTests(unittest.TestCase):
    def test_source_plan_and_template_are_deterministic(self) -> None:
        with _SourceCollectionDemo() as demo:
            first = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(demo.collection_path),
                "--target-records",
                "5",
            )
            first_plan = (demo.collection_path / "source_candidate_plan.jsonl").read_text(encoding="utf-8")
            second = _run_artifact_gate_main(
                "source-plan",
                "--gate",
                str(demo.seed_gate_path),
                "--manual-batch",
                str(demo.batch_path),
                "--out",
                str(demo.collection_path),
                "--target-records",
                "5",
            )
            second_plan = (demo.collection_path / "source_candidate_plan.jsonl").read_text(encoding="utf-8")
            template = _run_artifact_gate_main(
                "source-template",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "source_observation_template.jsonl"),
            )
            rows = read_jsonl(demo.collection_path / "source_observation_template.jsonl")
            plan_rows = read_jsonl(demo.collection_path / "source_candidate_plan.jsonl")

        self.assertEqual(first.code, 0, first.stderr)
        self.assertEqual(second.code, 0, second.stderr)
        self.assertEqual(template.code, 0, template.stderr)
        self.assertEqual(first_plan, second_plan)
        self.assertGreater(len(rows), 0)
        for key in ("source_observation_id", "candidate_id", "artifact_title", "source_url", "observer"):
            self.assertIn(key, rows[0])
        driver = _find_candidate(plan_rows, "driver for win98")
        self.assertTrue(driver["artifact_gate_excluded"])
        self.assertEqual(driver["gate_exclusion_reason"], "hardware_details_missing")
        windows = _find_candidate(plan_rows, "windows 7 apps")
        self.assertTrue(windows["artifact_gate_excluded"])
        self.assertEqual(windows["gate_exclusion_reason"], "broad_collection_query")

    def test_source_validate_reports_missing_observations_without_fabricating_evidence(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.write_source_plan_and_template()
            validate = _run_artifact_gate_main("source-validate", "--collection", str(demo.collection_path), "--json")
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            report = _run_artifact_gate_main(
                "source-report",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "source_collection_report.json"),
                "--json",
            )
            packets = read_jsonl(demo.collection_path / "manual_evidence_packets.jsonl")
            validation_payload = json.loads(validate.stdout)
            evidence_payload = json.loads(to_evidence.stdout)
            report_payload = json.loads(report.stdout)

        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertEqual(report.code, 0, report.stderr)
        self.assertEqual(validation_payload["status"], "pass_with_warnings")
        self.assertEqual(evidence_payload["evidence_packet_count"], 0)
        self.assertEqual(packets, [])
        self.assertEqual(report_payload["artifact_verified_packet_count"], 0)
        self.assertEqual(report_payload["collection_status"], "blocked")

    def test_source_ingest_accepts_valid_non_verified_source_lead(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.write_source_plan_and_template()
            _write_jsonl(demo.root / "source_lead.jsonl", [_valid_source_lead_observation(demo)])
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.root / "source_lead.jsonl"),
                "--json",
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            manual_ingest = _run_artifact_gate_main(
                "manual-ingest",
                "--batch",
                str(demo.batch_path),
                "--evidence",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_collection_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )
            packet = read_jsonl(demo.collection_path / "manual_evidence_packets.jsonl")[0]

        self.assertEqual(ingest.code, 0, ingest.stderr)
        self.assertEqual(json.loads(ingest.stdout)["valid_observation_count"], 1)
        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertFalse(packet["artifact_verified"])
        self.assertFalse(packet["gate_eligible"])
        self.assertEqual(manual_ingest.code, 0, manual_ingest.stderr)
        self.assertEqual(json.loads(review.stdout)["reviewed_artifact_record_count"], 0)

    def test_source_ingest_rejects_missing_observer_source_identifier_and_observed_fields(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.write_source_plan_and_template()
            observation = _valid_source_lead_observation(demo)
            observation["observer"] = ""
            observation["source_url"] = ""
            observation["source_identifier"] = ""
            observation["observed_artifact_fields"] = []
            _write_jsonl(demo.root / "invalid_missing.jsonl", [observation])
            result = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.root / "invalid_missing.jsonl"),
                "--json",
            )
            payload = json.loads(result.stdout)

        self.assertEqual(result.code, 1)
        joined = "\n".join(payload["errors"])
        self.assertIn("observer is required", joined)
        self.assertIn("source_url or source_identifier is required", joined)
        self.assertIn("observed_artifact_fields are required", joined)

    def test_source_ingest_rejects_unsafe_fetch_flags(self) -> None:
        for field in ("downloaded_file", "fetched_binary", "file_fetch_performed", "wayback_replay_used"):
            with self.subTest(field=field):
                with _SourceCollectionDemo() as demo:
                    demo.write_source_plan_and_template()
                    observation = _valid_source_lead_observation(demo)
                    observation[field] = True
                    _write_jsonl(demo.root / f"invalid_{field}.jsonl", [observation])
                    result = _run_artifact_gate_main(
                        "source-ingest",
                        "--collection",
                        str(demo.collection_path),
                        "--observations",
                        str(demo.root / f"invalid_{field}.jsonl"),
                        "--json",
                    )
                    payload = json.loads(result.stdout)

                self.assertEqual(result.code, 1)
                self.assertTrue(payload["errors"])

    def test_source_ingest_rejects_fixture_and_ia_metadata_verified_claims(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.write_source_plan_and_template()
            fixture = _valid_eligible_observation(demo)
            fixture["source_observation_id"] = "source-observation:fixture"
            fixture["access_method"] = "local_fixture"
            fixture["source_type"] = "local_fixture"
            fixture["source_authority"] = "primary"
            ia_metadata = _valid_eligible_observation(demo)
            ia_metadata["source_observation_id"] = "source-observation:ia-metadata"
            ia_metadata["source_type"] = "archive_metadata_page"
            ia_metadata["source_authority"] = "archive_metadata"
            _write_jsonl(demo.root / "bad_verified.jsonl", [fixture, ia_metadata])
            result = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.root / "bad_verified.jsonl"),
                "--json",
            )
            payload = json.loads(result.stdout)

        self.assertEqual(result.code, 1)
        joined = "\n".join(payload["errors"])
        self.assertIn("local_fixture", joined)
        self.assertIn("archive metadata", joined)

    def test_source_to_evidence_materializes_only_valid_eligible_manual_records(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.write_source_plan_and_template()
            _write_jsonl(demo.root / "eligible_source.jsonl", [_valid_eligible_observation(demo)])
            _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.root / "eligible_source.jsonl"),
            )
            to_evidence = _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
                "--json",
            )
            _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(demo.collection_path / "manual_evidence_packets.jsonl"))
            review = _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_collection_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
                "--json",
            )
            _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
            packet = read_jsonl(demo.collection_path / "manual_evidence_packets.jsonl")[0]
            records = read_jsonl(demo.batch_path / "reviewed_artifact_records.jsonl")
            report = _load_json(demo.batch_path / "artifact_gate_report.json")

        self.assertEqual(to_evidence.code, 0, to_evidence.stderr)
        self.assertTrue(packet["artifact_verified"])
        self.assertTrue(packet["gate_eligible"])
        self.assertEqual(json.loads(review.stdout)["reviewed_artifact_record_count"], 1)
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0]["binary_verified"])
        self.assertFalse(records[0]["download_safe"])
        self.assertFalse(records[0]["execution_safe"])
        self.assertFalse(records[0]["rights_cleared"])
        self.assertEqual(report["reviewed_artifact_gate_count"], 1)
        self.assertEqual(report["gate_status"], "blocked")

    def test_source_report_counts_valid_invalid_and_launch_gate_consumes_manual_report(self) -> None:
        with _SourceCollectionDemo() as demo:
            demo.write_source_plan_and_template()
            valid = _valid_eligible_observation(demo)
            invalid = _valid_source_lead_observation(demo)
            invalid["source_observation_id"] = "source-observation:invalid"
            invalid["observer"] = ""
            _write_jsonl(demo.root / "mixed_observations.jsonl", [valid, invalid])
            ingest = _run_artifact_gate_main(
                "source-ingest",
                "--collection",
                str(demo.collection_path),
                "--observations",
                str(demo.root / "mixed_observations.jsonl"),
                "--json",
            )
            _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
            )
            source_report = _run_artifact_gate_main(
                "source-report",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "source_collection_report.json"),
                "--json",
            )
            _run_artifact_gate_main("manual-ingest", "--batch", str(demo.batch_path), "--evidence", str(demo.collection_path / "manual_evidence_packets.jsonl"))
            _run_artifact_gate_main(
                "manual-review",
                "--batch",
                str(demo.batch_path),
                "--reviewer",
                "source_collection_01",
                "--out",
                str(demo.batch_path / "reviewed_artifact_records.jsonl"),
            )
            _run_artifact_gate_main("manual-report", "--batch", str(demo.batch_path), "--out", str(demo.batch_path / "artifact_gate_report.json"))
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
            launch_report = _load_json(demo.launch_gate_path / "launch_gate_report.json")

        self.assertEqual(ingest.code, 1)
        source_payload = json.loads(source_report.stdout)
        self.assertEqual(source_payload["valid_observation_count"], 1)
        self.assertEqual(source_payload["invalid_observation_count"], 1)
        self.assertEqual(source_payload["evidence_packet_count"], 1)
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["official_reviewed_artifact_count"], 1)
        self.assertEqual(launch_report["official_reviewed_artifact_gate_status"], "fail")

    def test_source_collection_commands_do_not_mutate_inputs(self) -> None:
        with _SourceCollectionDemo() as demo:
            watched = [
                demo.seed_gate_path / "artifact_gate_report.json",
                demo.seed_gate_path / "candidates.jsonl",
                demo.batch_path / "candidate_plan.jsonl",
                demo.batch_path / "artifact_gate_report.json",
            ]
            before = {path: _sha256(path) for path in watched}
            demo.write_source_plan_and_template()
            _run_artifact_gate_main("source-validate", "--collection", str(demo.collection_path))
            _run_artifact_gate_main(
                "source-to-evidence",
                "--collection",
                str(demo.collection_path),
                "--out",
                str(demo.collection_path / "manual_evidence_packets.jsonl"),
            )
            _run_artifact_gate_main("source-report", "--collection", str(demo.collection_path), "--out", str(demo.collection_path / "source_collection_report.json"))
            after = {path: _sha256(path) for path in watched}

        self.assertEqual(before, after)


class _SourceCollectionDemo:
    def __enter__(self) -> "_SourceCollectionDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self._temp_dir.name)
        self.index_path = self.root / "local_search_index.json"
        self.ledger_path = self.root / "local_review_ledger.jsonl"
        self.records_path = self.root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = self.root / "local_search_index.reviewed.json"
        self.seed_gate_path = self.root / "public-alpha-seed"
        self.batch_path = self.root / "manual-batch-01"
        self.collection_path = self.root / "source-collection-01"
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
            reason="Source collection test reviewed source lead",
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
        plan = _run_artifact_gate_main("manual-plan", "--gate", str(self.seed_gate_path), "--out", str(self.batch_path), "--target-records", "5")
        if plan.code != 0:
            raise AssertionError(plan.stderr or plan.stdout)
        template = _run_artifact_gate_main("manual-template", "--batch", str(self.batch_path), "--out", str(self.batch_path / "manual_evidence_template.jsonl"))
        if template.code != 0:
            raise AssertionError(template.stderr or template.stdout)
        report = _run_artifact_gate_main("manual-report", "--batch", str(self.batch_path), "--out", str(self.batch_path / "artifact_gate_report.json"))
        if report.code != 0:
            raise AssertionError(report.stderr or report.stdout)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()

    def write_source_plan_and_template(self) -> None:
        plan = _run_artifact_gate_main(
            "source-plan",
            "--gate",
            str(self.seed_gate_path),
            "--manual-batch",
            str(self.batch_path),
            "--out",
            str(self.collection_path),
            "--target-records",
            "5",
        )
        if plan.code != 0:
            raise AssertionError(plan.stderr or plan.stdout)
        template = _run_artifact_gate_main(
            "source-template",
            "--collection",
            str(self.collection_path),
            "--out",
            str(self.collection_path / "source_observation_template.jsonl"),
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


def _write_staging_and_rehearsal(demo: _SourceCollectionDemo) -> None:
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


def _valid_source_lead_observation(demo: _SourceCollectionDemo) -> dict[str, object]:
    candidate = _selected_candidate(demo)
    source_url = "https://catalog.example.invalid/creative/sound-blaster-ct1740-manual"
    return {
        "schema_version": "eureka.artifact_source_observation.v0",
        "source_observation_id": "source-observation:ct1740-catalog",
        "collection_id": "source-collection:source-collection-01",
        "candidate_id": candidate["candidate_id"],
        "artifact_title": "Sound Blaster CT1740 User Manual",
        "artifact_type": "manual",
        "artifact_identity_fields": {
            "title": "Sound Blaster CT1740 User Manual",
            "identifier": "CT1740",
            "platform_or_context": "Sound Blaster CT1740",
        },
        "platform_or_context": "Sound Blaster CT1740",
        "source_id": "ct1740-catalog",
        "source_url": source_url,
        "source_identifier": "CT1740 manual catalog entry",
        "source_title": "Sound Blaster CT1740 manual catalog page",
        "publisher_or_source_name": "Example catalog",
        "source_type": "stable_catalog_page",
        "source_authority": "reputable_secondary",
        "observed_artifact_fields": ["title", "model", "manual"],
        "observation_notes": "Catalog metadata identifies a CT1740 manual candidate.",
        "short_evidence_summary": "Stable catalog metadata identifies the CT1740 manual as a source lead.",
        "access_method": "manual_page_observation",
        "observed_at": "2026-06-14T00:00:00Z",
        "collected_at": "2026-06-14T00:00:00Z",
        "observer": "source_collection_01",
        "reviewer": "",
        "review_rationale": "",
        "live_network_used": False,
        "no_download_performed": True,
        "downloaded_file": False,
        "fetched_binary": False,
        "wayback_replay_used": False,
        "file_fetch_performed": False,
        "proposed_verification_scope": "artifact_identity_candidate",
        "proposed_artifact_verified": False,
        "proposed_gate_eligible": False,
        "confidence": "medium",
        "limitations": ["secondary metadata only"],
    }


def _valid_eligible_observation(demo: _SourceCollectionDemo) -> dict[str, object]:
    observation = _valid_source_lead_observation(demo)
    observation.update(
        {
            "source_observation_id": "source-observation:ct1740-official",
            "source_id": "creative-support-ct1740-manual",
            "source_url": "https://support.example.invalid/creative/sound-blaster-ct1740-manual",
            "source_identifier": "Creative support CT1740 manual page",
            "source_title": "Sound Blaster CT1740 manual support page",
            "publisher_or_source_name": "Creative support",
            "source_type": "official_support_page",
            "source_authority": "primary",
            "short_evidence_summary": "Primary support-page metadata identifies the CT1740 manual artifact.",
            "reviewer": "source_collection_01",
            "review_rationale": "Primary support-page metadata identifies a concrete CT1740 manual artifact by model and title.",
            "proposed_verification_scope": "artifact_identity_metadata",
            "proposed_artifact_verified": True,
            "proposed_gate_eligible": True,
            "confidence": "high",
            "limitations": ["does not verify binary safety, downloads, execution, or rights"],
        }
    )
    return observation


def _selected_candidate(demo: _SourceCollectionDemo) -> dict[str, object]:
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
