from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, write_index
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from scripts.eureka_staging import main as staging_main


QUERY = "manual for Sound Blaster CT1740"
SECRET_MARKERS = (
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "sk-",
)


class PublicAlphaLaunchBlockerCloseoutTests(unittest.TestCase):
    def test_audit_writes_json_and_markdown_reports(self) -> None:
        with _LaunchGateDemo() as demo:
            result = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--out",
                str(demo.launch_gate_path),
            )
            report = _load_json(demo.launch_gate_report_path)
            markdown_exists = demo.launch_gate_markdown_path.is_file()

        self.assertEqual(result.code, 0, result.stderr)
        self.assertTrue(markdown_exists)
        self.assertEqual(report["task_id"], "PUBLIC-ALPHA-LAUNCH-BLOCKER-CLOSEOUT-00")
        self.assertEqual(report["status"], "PASS_WITH_WARNINGS")
        self.assertEqual(report["launch_status"], "BLOCKED")
        self.assertEqual(report["local_rehearsal_status"], "GREEN")

    def test_validate_report_passes_for_valid_report(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            result = _run_launch_gate_main("validate-report", "--report", str(demo.launch_gate_report_path))

        self.assertEqual(result.code, 0, result.stderr)
        self.assertIn("validation passed", result.stdout)

    def test_validate_report_fails_for_missing_required_fields(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)
            bad_report = copy.deepcopy(report)
            bad_report.pop("blocker_categories")
            bad_report["mutation_checks"]["bundle_mutated"] = True
            bad_path = demo.launch_gate_path / "bad_launch_gate_report.json"
            _write_json(bad_path, bad_report)
            result = _run_launch_gate_main("validate-report", "--report", str(bad_path))

        self.assertEqual(result.code, 1)
        self.assertIn("missing required field: blocker_categories", result.stderr)

    def test_status_prints_launch_status_and_categories(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            result = _run_launch_gate_main("status", "--report", str(demo.launch_gate_report_path))

        self.assertEqual(result.code, 0, result.stderr)
        self.assertIn("local rehearsal: GREEN", result.stdout)
        self.assertIn("launch status: BLOCKED", result.stdout)
        self.assertIn("corpus_evidence_blockers", result.stdout)
        self.assertIn("deployment_blockers", result.stdout)

    def test_current_expected_report_is_local_green_but_launch_blocked(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(report["local_rehearsal_status"], "GREEN")
        self.assertEqual(report["launch_status"], "BLOCKED")
        self.assertEqual(report["local_safety_status"], "pass")
        self.assertEqual(report["mutation_safety_status"], "pass")
        self.assertEqual(report["public_readonly_status"], "pass")
        self.assertEqual(report["workbench_exposure_status"], "not_exposed")
        self.assertEqual(report["live_metadata_exposure_status"], "not_exposed")

    def test_fail_on_blocked_exits_nonzero_when_blockers_remain(self) -> None:
        with _LaunchGateDemo() as demo:
            result = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--out",
                str(demo.launch_gate_path),
                "--fail-on-blocked",
            )

        self.assertEqual(result.code, 1)
        self.assertIn("launch remains blocked", result.stderr)

    def test_invalid_staging_bundle_causes_fail_report(self) -> None:
        with _LaunchGateDemo() as demo:
            (demo.bundle_path / "manifest.json").unlink()
            result = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--out",
                str(demo.launch_gate_path),
            )
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("bundle validation" in item for item in report["local_audit_failures"]))

    def test_invalid_rehearsal_report_causes_fail_report(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_json(demo.rehearsal_report_path, {"task_id": "PUBLIC-ALPHA-REHEARSAL-00"})
            result = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--out",
                str(demo.launch_gate_path),
            )
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["local_rehearsal_status"], "RED")
        self.assertTrue(any("rehearsal report validation" in item for item in report["local_audit_failures"]))

    def test_missing_gate_sources_are_unknown_or_blocked_not_pass(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(report["official_reviewed_artifact_gate_status"], "unknown")
        self.assertEqual(report["verified_artifact_evidence_status"], "unknown")
        self.assertIn("artifact_gate_authority_unknown", report["blocker_categories"]["unknown_authority_blockers"])
        self.assertIn("verified_evidence_authority_unknown", report["blocker_categories"]["unknown_authority_blockers"])

    def test_artifact_verified_zero_and_local_demo_reviews_remain_blocking(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(report["artifact_verified_count"], 0)
        self.assertGreater(report["local_reviewed_record_count"], 0)
        ids = {blocker["id"] for blocker in report["blockers"]}
        self.assertIn("artifact_verified_count_zero", ids)
        self.assertIn("local_demo_reviewed_records_not_official_gate", ids)

    def test_missing_deployment_release_and_approval_gates_remain_blocking(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        categories = report["blocker_categories"]
        self.assertIn("external_staging_host_missing", categories["deployment_blockers"])
        self.assertIn("production_hosting_missing", categories["deployment_blockers"])
        self.assertIn("tls_domain_missing", categories["deployment_blockers"])
        self.assertIn("full_discovery_not_passed", categories["release_process_blockers"])
        self.assertIn("release_promotion_not_passed", categories["release_process_blockers"])
        self.assertIn("public_launch_approval_missing", categories["approval_blockers"])

    def test_report_does_not_expose_tokens_or_secrets(self) -> None:
        with _LaunchGateDemo() as demo:
            _write_launch_gate(demo)
            text = demo.launch_gate_report_path.read_text(encoding="utf-8") + demo.launch_gate_markdown_path.read_text(encoding="utf-8")

        for marker in SECRET_MARKERS:
            self.assertNotIn(marker, text)

    def test_audit_does_not_mutate_inputs(self) -> None:
        with _LaunchGateDemo() as demo:
            paths = [
                demo.bundle_path / "manifest.json",
                demo.bundle_path / "public_search_index.json",
                demo.bundle_path / "public_runtime_config.json",
                demo.rehearsal_report_path,
                demo.index_path,
                demo.ledger_path,
                demo.records_path,
                demo.reviewed_index_path,
            ]
            before = {path: _sha256(path) for path in paths}
            _write_launch_gate(demo)
            after = {path: _sha256(path) for path in paths}
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(before, after)
        self.assertFalse(report["mutation_checks"]["bundle_mutated"])
        self.assertFalse(report["mutation_checks"]["rehearsal_report_mutated"])
        self.assertFalse(report["mutation_checks"]["any_input_mutated"])


class _LaunchGateDemo:
    def __enter__(self) -> "_LaunchGateDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.index_path = root / "local_search_index.json"
        self.ledger_path = root / "local_review_ledger.jsonl"
        self.records_path = root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = root / "local_search_index.reviewed.json"
        self.bundle_path = root / "public-alpha-bundle"
        self.rehearsal_path = root / "rehearsal"
        self.rehearsal_report_path = self.rehearsal_path / "rehearsal_report.json"
        self.launch_gate_path = root / "launch-gate"
        self.launch_gate_report_path = self.launch_gate_path / "launch_gate_report.json"
        self.launch_gate_markdown_path = self.launch_gate_path / "LAUNCH_GATE_REPORT.md"
        write_index(self.index_path, build_local_demo_index())
        accept_candidate(
            index_path=self.index_path,
            query=QUERY,
            ledger_path=self.ledger_path,
            records_path=self.records_path,
            reviewer="local_demo",
            reason="Public alpha launch gate test seed",
            reviewed_at="2026-06-13T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=self.records_path))
        package = _run_staging_main("package", "--index", str(self.reviewed_index_path), "--out", str(self.bundle_path))
        if package.code != 0:
            raise AssertionError(package.stderr or package.stdout)
        rehearsal = _run_rehearsal_main(
            "run",
            "--bundle",
            str(self.bundle_path),
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--out",
            str(self.rehearsal_path),
        )
        if rehearsal.code != 0:
            raise AssertionError(rehearsal.stderr or rehearsal.stdout)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


def _write_launch_gate(demo: _LaunchGateDemo) -> None:
    result = _run_launch_gate_main(
        "audit",
        "--bundle",
        str(demo.bundle_path),
        "--rehearsal-report",
        str(demo.rehearsal_report_path),
        "--out",
        str(demo.launch_gate_path),
    )
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _run_staging_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = staging_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _run_rehearsal_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = rehearsal_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _run_launch_gate_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = launch_gate_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_bytes(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
