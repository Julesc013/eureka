from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.corpus_gate_closeout import (
    CLOSEOUT_JSON,
    PUBLIC_ARTIFACT_RECORDS_JSONL,
    PUBLIC_EVIDENCE_SUMMARY_JSONL,
)
from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, write_index
from scripts.eureka_public_alpha_corpus_gate import main as corpus_gate_main
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from scripts.eureka_staging import main as staging_main
from scripts.run_eureka_local import main as run_local_main


QUERY = "manual for Sound Blaster CT1740"


class PublicAlphaCorpusGateCloseoutTests(unittest.TestCase):
    def test_closeout_writes_public_safe_reports_and_exports_25_records(self) -> None:
        with _CorpusCloseoutDemo() as demo:
            result = _run_corpus_main(
                "closeout",
                "--artifact-gate-report",
                str(demo.artifact_gate_report_path),
                "--manual-batch",
                str(demo.manual_batch_path),
                "--out",
                str(demo.closeout_path),
            )
            validate = _run_corpus_main("validate", "--closeout", str(demo.closeout_path))
            status = _run_corpus_main("status", "--closeout", str(demo.closeout_path), "--json")

            closeout = _load_json(demo.closeout_path / CLOSEOUT_JSON)
            public_records = _read_jsonl(demo.closeout_path / PUBLIC_ARTIFACT_RECORDS_JSONL)
            summaries = _read_jsonl(demo.closeout_path / PUBLIC_EVIDENCE_SUMMARY_JSONL)
            text = (demo.closeout_path / PUBLIC_ARTIFACT_RECORDS_JSONL).read_text(encoding="utf-8")
            markdown_exists = (demo.closeout_path / "CORPUS_GATE_CLOSEOUT.md").is_file()

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(json.loads(status.stdout)["status"], "pass")
        self.assertTrue(markdown_exists)
        self.assertEqual(closeout["corpus_gate_status"], "pass")
        self.assertEqual(closeout["reviewed_artifact_gate_count"], 25)
        self.assertEqual(closeout["artifact_verified_count"], 25)
        self.assertEqual(closeout["verification_scope_counts"], {"artifact_identity_metadata": 25})
        self.assertEqual(closeout["binary_verified_count"], 0)
        self.assertEqual(closeout["download_safe_count"], 0)
        self.assertEqual(closeout["execution_safe_count"], 0)
        self.assertEqual(closeout["rights_cleared_count"], 0)
        self.assertEqual(len(public_records), 25)
        self.assertEqual(len(summaries), 25)
        self.assertNotIn(".eureka", text)
        self.assertNotIn("local_review", text)
        self.assertNotIn("local-dev-token", text)

    def test_closeout_validate_rejects_under_count_duplicates_leakage_secrets_and_safety_claims(self) -> None:
        cases = (
            ("under_count", {"count": 24}, "reviewed_artifact_gate_count"),
            ("duplicate", {"duplicate": True}, "duplicate artifact identity"),
            ("local_path", {"local_path": True}, "forbidden marker"),
            ("secret", {"secret": True}, "forbidden secret marker"),
            ("binary_claim", {"unsafe_field": "binary_verified"}, "binary_verified cannot be true"),
            ("download_claim", {"unsafe_field": "download_safe"}, "download_safe cannot be true"),
            ("execution_claim", {"unsafe_field": "execution_safe"}, "execution_safe cannot be true"),
            ("rights_claim", {"unsafe_field": "rights_cleared"}, "rights_cleared cannot be true"),
        )
        for label, options, expected in cases:
            with self.subTest(label=label), _CorpusCloseoutDemo(**options) as demo:
                result = _run_corpus_main(
                    "closeout",
                    "--artifact-gate-report",
                    str(demo.artifact_gate_report_path),
                    "--manual-batch",
                    str(demo.manual_batch_path),
                    "--out",
                    str(demo.closeout_path),
                )

                self.assertNotEqual(result.code, 0, result.stdout)
                self.assertIn(expected, result.stderr)

    def test_staging_package_with_corpus_closeout_updates_manifest_and_public_status(self) -> None:
        with _CorpusCloseoutDemo() as demo:
            _write_closeout(demo)
            package = _run_staging_main(
                "package",
                "--index",
                str(demo.reviewed_index_path),
                "--corpus-gate-closeout",
                str(demo.closeout_path),
                "--out",
                str(demo.bundle_path),
            )
            validate = _run_staging_main("validate", "--bundle", str(demo.bundle_path))
            status = _run_staging_main("status", "--bundle", str(demo.bundle_path), "--json")
            smoke = _run_local_main("--smoke", "--staging-bundle", str(demo.bundle_path))
            manifest = _load_json(demo.bundle_path / "manifest.json")

        self.assertEqual(package.code, 0, package.stderr)
        self.assertEqual(validate.code, 0, validate.stderr)
        status_payload = json.loads(status.stdout)
        smoke_payload = json.loads(smoke.stdout)
        self.assertEqual(manifest["artifact_verified_count"], 25)
        self.assertEqual(manifest["public_search_index_artifact_verified_count"], 0)
        self.assertEqual(manifest["reviewed_artifact_gate_count"], 25)
        self.assertEqual(status_payload["corpus_gate_status"], "pass")
        self.assertEqual(smoke_payload["status_payload"]["artifact_verified_count"], 25)
        self.assertEqual(smoke_payload["status_payload"]["corpus_gate_status"], "pass")
        self.assertTrue(smoke_payload["status_payload"]["artifact_identity_metadata_only"])
        self.assertEqual(smoke_payload["status_payload"]["binary_verified_count"], 0)
        self.assertFalse(smoke_payload["status_payload"]["live_metadata_enabled"])
        self.assertFalse(smoke_payload["status_payload"]["workbench_exposed"])

    def test_staging_validate_rejects_inconsistent_corpus_counts(self) -> None:
        with _CorpusCloseoutDemo() as demo:
            _write_closeout(demo)
            _package_with_closeout(demo)
            manifest_path = demo.bundle_path / "manifest.json"
            manifest = _load_json(manifest_path)
            manifest["artifact_verified_count"] = 24
            _write_json(manifest_path, manifest)
            validate = _run_staging_main("validate", "--bundle", str(demo.bundle_path))

        self.assertEqual(validate.code, 1)
        self.assertIn("manifest.artifact_verified_count", validate.stderr)

    def test_rehearsal_and_launch_gate_resolve_corpus_blockers_but_remain_blocked(self) -> None:
        with _CorpusCloseoutDemo() as demo:
            _write_closeout(demo)
            _package_with_closeout(demo)
            before = _bundle_hashes(demo.bundle_path)
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
            rehearsal_validate = _run_rehearsal_main("validate-report", "--report", str(demo.rehearsal_report_path))
            launch = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--artifact-gate-report",
                str(demo.artifact_gate_report_path),
                "--corpus-gate-closeout",
                str(demo.closeout_path / CLOSEOUT_JSON),
                "--out",
                str(demo.launch_gate_path),
            )
            launch_validate = _run_launch_gate_main("validate-report", "--report", str(demo.launch_gate_report_path))
            after = _bundle_hashes(demo.bundle_path)
            rehearsal_report = _load_json(demo.rehearsal_report_path)
            launch_report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(rehearsal.code, 0, rehearsal.stderr)
        self.assertEqual(rehearsal_validate.code, 0, rehearsal_validate.stderr)
        self.assertEqual(launch.code, 0, launch.stderr)
        self.assertEqual(launch_validate.code, 0, launch_validate.stderr)
        self.assertEqual(before, after)
        self.assertEqual(rehearsal_report["corpus_gate_status"], "pass")
        self.assertEqual(rehearsal_report["artifact_verified_count"], 25)
        self.assertNotIn("official reviewed-artifact gate is not completed", rehearsal_report["launch_blockers"])
        self.assertEqual(launch_report["launch_status"], "BLOCKED")
        self.assertEqual(launch_report["corpus_gate_closeout_status"], "pass")
        self.assertEqual(launch_report["artifact_verified_count"], 25)
        self.assertEqual(launch_report["blocker_categories"]["corpus_evidence_blockers"], [])
        self.assertEqual(launch_report["blocker_categories"]["unknown_authority_blockers"], [])
        self.assertIn("external_staging_host_missing", launch_report["blocker_categories"]["deployment_blockers"])
        self.assertIn("full_discovery_not_passed", launch_report["blocker_categories"]["release_process_blockers"])
        self.assertIn("public_launch_approval_missing", launch_report["blocker_categories"]["approval_blockers"])


class _CorpusCloseoutDemo:
    def __init__(
        self,
        *,
        count: int = 25,
        duplicate: bool = False,
        local_path: bool = False,
        secret: bool = False,
        unsafe_field: str = "",
    ) -> None:
        self.count = count
        self.duplicate = duplicate
        self.local_path = local_path
        self.secret = secret
        self.unsafe_field = unsafe_field

    def __enter__(self) -> "_CorpusCloseoutDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.root = root
        self.manual_batch_path = root / "manual-batch"
        self.closeout_path = root / "corpus-closeout"
        self.bundle_path = root / "staging-bundle"
        self.rehearsal_path = root / "rehearsal"
        self.rehearsal_report_path = self.rehearsal_path / "rehearsal_report.json"
        self.launch_gate_path = root / "launch-gate"
        self.launch_gate_report_path = self.launch_gate_path / "launch_gate_report.json"
        self.artifact_gate_report_path = self.manual_batch_path / "artifact_gate_report.json"
        self.reviewed_index_path = root / "local_search_index.reviewed.json"
        self._write_manual_batch()
        self._write_reviewed_index(root)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()

    def _write_manual_batch(self) -> None:
        self.manual_batch_path.mkdir(parents=True)
        records = [self._record(index) for index in range(self.count)]
        packets = [self._packet(index, records[index]) for index in range(self.count)]
        _write_jsonl(self.manual_batch_path / "reviewed_artifact_records.jsonl", records)
        _write_jsonl(self.manual_batch_path / "manual_evidence_packets.jsonl", packets)
        verified_count = sum(1 for item in records if item.get("artifact_verified") is True and item.get("gate_eligible") is True)
        report = {
            "schema_version": "eureka.manual_artifact_evidence_batch.v0",
            "task_id": "MANUAL-ARTIFACT-EVIDENCE-BATCH-01",
            "status": "PASS" if verified_count >= 25 else "PASS_WITH_WARNINGS",
            "gate_status": "pass" if verified_count >= 25 else "blocked",
            "batch_id": "manual-batch:test",
            "gate_target_reviewed_artifacts": 25,
            "official_reviewed_artifact_gate_target": 25,
            "reviewed_artifact_gate_count": verified_count,
            "official_reviewed_artifact_count": verified_count,
            "reviewed_artifact_record_count": verified_count,
            "artifact_verified_count": verified_count,
            "evidence_packet_count": self.count,
            "valid_evidence_packet_count": self.count,
            "invalid_evidence_packet_count": 0,
            "source_authority_counts": {"primary_official_source": verified_count},
            "verification_scope_counts": {"artifact_identity_metadata": verified_count},
            "blockers": [] if verified_count >= 25 else [{"id": "reviewed_artifact_gate_count_below_target"}],
            "warnings": ["test generated artifact evidence only"],
            "next_recommended_task": "PUBLIC-ALPHA-CORPUS-GATE-CLOSEOUT-00",
        }
        _write_json(self.artifact_gate_report_path, report)

    def _record(self, index: int) -> dict[str, object]:
        identity_index = 0 if self.duplicate and index == self.count - 1 else index
        title = f"Test Artifact {identity_index:02d}"
        if self.local_path and index == 0:
            title = r"C:\Users\Jules\.eureka\local_reviewed_records.jsonl"
        source_identifier = f"Official release page {identity_index:02d}"
        if self.secret and index == 0:
            source_identifier = "token=local-dev-token"
        record: dict[str, object] = {
            "schema_version": "eureka.reviewed_artifact_gate_record.v0",
            "reviewed_artifact_record_id": f"reviewed-artifact-gate-record:test-{index:02d}",
            "source_candidate_id": f"candidate:test-{identity_index:02d}",
            "source_evidence_packet_id": f"evidence:test-{identity_index:02d}",
            "dedupe_identity_key": f"test artifact {identity_index:02d}|software|windows|{identity_index}|artifact_identity_metadata",
            "batch_id": "manual-batch:test",
            "title": title,
            "artifact_type": "software",
            "platform_or_context": "Windows",
            "artifact_identity_fields": {
                "title": title,
                "artifact_type": "software",
                "platform_or_context": "Windows",
                "product": f"Test Artifact {identity_index:02d}",
                "version": f"{identity_index}.0",
                "release_date": "2026-01-01",
            },
            "status": "verified",
            "review_state": "accepted_artifact_identity",
            "artifact_verified": True,
            "accepted_truth": False,
            "gate_eligible": True,
            "verification_scope": "artifact_identity_metadata",
            "source_authority": "primary_official_source",
            "evidence_type": "source_collection_observation",
            "source_observations": [
                {
                    "source_title": f"Test Artifact {identity_index:02d} Release Notes",
                    "source_type": "official_release_page",
                    "source_authority": "primary",
                    "source_identifier": source_identifier,
                    "source_url": f"https://example.org/artifacts/{identity_index:02d}",
                    "observed_artifact_fields": ["title", "version", "release_date"],
                    "short_evidence_summary": f"Official metadata identifies Test Artifact {identity_index:02d}.",
                }
            ],
            "source_identifiers": [source_identifier],
            "observed_fields": ["title", "version", "release_date"],
            "binary_verified": False,
            "download_safe": False,
            "execution_safe": False,
            "rights_cleared": False,
            "no_download_performed": True,
            "file_fetch_performed": False,
            "live_network_used": True,
        }
        if self.unsafe_field and index == 0:
            record[self.unsafe_field] = True
        return record

    def _packet(self, index: int, record: dict[str, object]) -> dict[str, object]:
        return {
            "schema_version": "eureka.artifact_gate_evidence_packet.v0",
            "evidence_packet_id": record["source_evidence_packet_id"],
            "candidate_id": record["source_candidate_id"],
            "artifact_title": record["title"],
            "artifact_type": "software",
            "platform_or_context": "Windows",
            "artifact_verified": True,
            "gate_eligible": True,
            "verification_scope": "artifact_identity_metadata",
            "source_authority": "primary_official_source",
            "evidence_type": "source_collection_observation",
            "source_observations": record["source_observations"],
            "observed_fields": record["observed_fields"],
            "binary_verified": False,
            "download_safe": False,
            "execution_safe": False,
            "rights_cleared": False,
            "no_download_performed": True,
            "file_fetch_performed": False,
            "live_network_used": True,
            "artifact_identity_fields": record["artifact_identity_fields"],
            "collected_at": "2026-06-15T00:00:00Z",
        }

    def _write_reviewed_index(self, root: Path) -> None:
        index_path = root / "local_search_index.json"
        ledger_path = root / "local_review_ledger.jsonl"
        records_path = root / "local_reviewed_records.jsonl"
        write_index(index_path, build_local_demo_index())
        accept_candidate(
            index_path=index_path,
            query=QUERY,
            ledger_path=ledger_path,
            records_path=records_path,
            reviewer="local_demo",
            reason="Corpus closeout staging seed",
            reviewed_at="2026-06-15T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=records_path))


def _write_closeout(demo: _CorpusCloseoutDemo) -> None:
    result = _run_corpus_main(
        "closeout",
        "--artifact-gate-report",
        str(demo.artifact_gate_report_path),
        "--manual-batch",
        str(demo.manual_batch_path),
        "--out",
        str(demo.closeout_path),
    )
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _package_with_closeout(demo: _CorpusCloseoutDemo) -> None:
    result = _run_staging_main(
        "package",
        "--index",
        str(demo.reviewed_index_path),
        "--corpus-gate-closeout",
        str(demo.closeout_path),
        "--out",
        str(demo.bundle_path),
    )
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _run_corpus_main(*args: str) -> "_Result":
    return _run_main(corpus_gate_main, *args)


def _run_staging_main(*args: str) -> "_Result":
    return _run_main(staging_main, *args)


def _run_rehearsal_main(*args: str) -> "_Result":
    return _run_main(rehearsal_main, *args)


def _run_launch_gate_main(*args: str) -> "_Result":
    return _run_main(launch_gate_main, *args)


def _run_local_main(*args: str) -> "_Result":
    return _run_main(run_local_main, *args)


def _run_main(main_func: object, *args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main_func(list(args), stdout=stdout, stderr=stderr)  # type: ignore[misc]
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _bundle_hashes(bundle_path: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(bundle_path.iterdir())
        if path.is_file()
    }


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
