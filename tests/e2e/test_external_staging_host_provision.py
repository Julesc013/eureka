from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.external_staging_mvp import (
    PLAN_JSON,
    REPORT_JSON,
    package_leakage_errors,
    smoke_from_plan,
)
from scripts.eureka_external_staging import main as external_staging_main
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from tests.e2e.test_public_alpha_corpus_gate_closeout import (
    _CorpusCloseoutDemo,
    _package_with_closeout,
    _write_closeout,
)


class ExternalStagingHostProvisionTests(unittest.TestCase):
    def test_plan_validate_package_and_dry_run_missing_host(self) -> None:
        with _ExternalStagingDemo() as demo:
            plan = _run_external_main("plan", "--bundle", str(demo.bundle_path), "--out", str(demo.external_path))
            validate = _run_external_main("validate-plan", "--plan", str(demo.plan_path))
            package = _run_external_main("package", "--bundle", str(demo.bundle_path), "--plan", str(demo.plan_path), "--out", str(demo.package_path))
            dry_run = _run_external_main("deploy", "--plan", str(demo.plan_path), "--dry-run")
            smoke = _run_external_main("smoke", "--plan", str(demo.plan_path))
            validate_report = _run_external_main("validate-report", "--report", str(demo.report_path))
            status = _run_external_main("status", "--report", str(demo.report_path))
            plan_payload = _load_json(demo.plan_path)
            report = _load_json(demo.report_path)

        self.assertEqual(plan.code, 0, plan.stderr)
        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(package.code, 0, package.stderr)
        self.assertEqual(dry_run.code, 0, dry_run.stderr)
        self.assertEqual(smoke.code, 0, smoke.stderr)
        self.assertEqual(validate_report.code, 0, validate_report.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertFalse(plan_payload["host_configured"])
        self.assertEqual(report["deployment_status"], "dry_run_pass")
        self.assertEqual(report["smoke_status"], "blocked")
        self.assertIn("external staging host is not configured", report["blockers"])
        self.assertIn("staging base URL is not configured", report["blockers"])
        self.assertIn("EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG", status.stdout)

    def test_validate_plan_rejects_secret_marker(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_plan(demo)
            plan = _load_json(demo.plan_path)
            plan["host_redacted"] = "token=local-dev-token"
            _write_json(demo.plan_path, plan)
            result = _run_external_main("validate-plan", "--plan", str(demo.plan_path))

        self.assertEqual(result.code, 1)
        self.assertIn("forbidden secret marker", result.stderr)

    def test_package_excludes_private_paths_tokens_and_live_metadata_config(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_plan(demo)
            result = _run_external_main("package", "--bundle", str(demo.bundle_path), "--plan", str(demo.plan_path), "--out", str(demo.package_path))
            text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in demo.package_path.rglob("*") if path.is_file())
            errors = package_leakage_errors(demo.package_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertFalse(errors)
        self.assertNotIn("local_review_ledger", text)
        self.assertNotIn("local_reviewed_records", text)
        self.assertNotIn("local-dev-token", text)
        self.assertNotIn(".eureka", text)
        self.assertNotIn("live_metadata_enabled\": true", text)

    def test_deploy_apply_refuses_missing_host_configuration(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_plan(demo)
            result = _run_external_main("deploy", "--plan", str(demo.plan_path), "--apply")
            report = _load_json(demo.report_path)

        self.assertEqual(result.code, 1)
        self.assertEqual(report["deployment_status"], "not_configured")
        self.assertIn("host is not configured", report["blockers"])

    def test_smoke_with_mocked_routes_can_pass_without_network(self) -> None:
        with _ExternalStagingDemo(configured=True) as demo:
            _write_plan(demo, configured=True)
            _run_external_main("deploy", "--plan", str(demo.plan_path), "--apply")
            report = smoke_from_plan(plan=demo.plan_path, probe=_fake_probe)
            errors = _run_external_main("validate-report", "--report", str(demo.report_path))

        self.assertEqual(report["deployment_status"], "deployed")
        self.assertEqual(report["smoke_status"], "pass")
        self.assertEqual(errors.code, 0, errors.stderr)
        self.assertFalse(report["safety_checks"]["workbench_exposed"])
        self.assertFalse(report["safety_checks"]["live_metadata_enabled"])

    def test_validate_report_rejects_unsafe_claims(self) -> None:
        cases = (
            ("deployed_without_host", {"deployment_status": "deployed", "host_configured": False}, "deployed without host"),
            ("smoke_without_probes", {"smoke_status": "pass", "route_probe_results": []}, "smoke pass without route probes"),
            ("workbench", {"safety_checks": {"workbench_exposed": True}}, "workbench_exposed"),
            ("live", {"safety_checks": {"live_metadata_enabled": True}}, "live_metadata_enabled"),
            ("mutation", {"safety_checks": {"mutation_enabled": True}}, "mutation_enabled"),
            ("binary", {"binary_verified_count": 1}, "binary_verified_count"),
        )
        for label, patch, expected in cases:
            with self.subTest(label=label), _ExternalStagingDemo() as demo:
                _write_plan(demo)
                _run_external_main("deploy", "--plan", str(demo.plan_path), "--dry-run")
                report = _load_json(demo.report_path)
                _deep_update(report, patch)
                _write_json(demo.report_path, report)
                result = _run_external_main("validate-report", "--report", str(demo.report_path))

                self.assertEqual(result.code, 1)
                self.assertIn(expected, result.stderr)

    def test_launch_gate_consumes_dry_run_report_but_keeps_external_staging_blocker(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_plan(demo)
            _run_external_main("deploy", "--plan", str(demo.plan_path), "--dry-run")
            _run_external_main("smoke", "--plan", str(demo.plan_path))
            _write_rehearsal(demo)
            result = _run_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["external_staging_report_status"], "dry_run")
        self.assertIn("external_staging_host_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertEqual(report["launch_status"], "BLOCKED")

    def test_launch_gate_resolves_external_staging_blocker_only_for_deployed_and_smoked_report(self) -> None:
        with _ExternalStagingDemo(configured=True) as demo:
            _write_plan(demo, configured=True)
            _run_external_main("deploy", "--plan", str(demo.plan_path), "--apply")
            smoke_from_plan(plan=demo.plan_path, probe=_fake_probe)
            _write_rehearsal(demo)
            result = _run_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["external_staging_report_status"], "pass")
        self.assertNotIn("external_staging_host_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertIn("production_hosting_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertIn("release_promotion_not_passed", report["blocker_categories"]["release_process_blockers"])
        self.assertIn("public_launch_approval_missing", report["blocker_categories"]["approval_blockers"])
        self.assertEqual(report["launch_status"], "BLOCKED")

    def test_external_staging_does_not_mutate_inputs_or_tracked_generated_files(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_plan(demo)
            paths = [
                demo.bundle_path / "manifest.json",
                demo.bundle_path / "public_search_index.json",
                demo.bundle_path / "public_runtime_config.json",
                demo.bundle_path / "corpus_gate_closeout.json",
                demo.bundle_path / "public_artifact_identity_records.jsonl",
                demo.bundle_path / "public_artifact_evidence_summary.jsonl",
            ]
            before = {path: _sha256(path) for path in paths}
            _run_external_main("package", "--bundle", str(demo.bundle_path), "--plan", str(demo.plan_path), "--out", str(demo.package_path))
            _run_external_main("deploy", "--plan", str(demo.plan_path), "--dry-run")
            _run_external_main("smoke", "--plan", str(demo.plan_path))
            after = {path: _sha256(path) for path in paths}

        self.assertEqual(before, after)


class _ExternalStagingDemo:
    def __init__(self, *, configured: bool = False) -> None:
        self.configured = configured

    def __enter__(self) -> "_ExternalStagingDemo":
        self._corpus = _CorpusCloseoutDemo()
        self.demo = self._corpus.__enter__()
        _write_closeout(self.demo)
        _package_with_closeout(self.demo)
        self.root = self.demo.root
        self.bundle_path = self.demo.bundle_path
        self.external_path = self.root / "external-staging"
        self.plan_path = self.external_path / PLAN_JSON
        self.report_path = self.external_path / REPORT_JSON
        self.package_path = self.external_path / "package"
        self.launch_gate_path = self.root / "launch-gate-external"
        self.launch_gate_report_path = self.launch_gate_path / "launch_gate_report.json"
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._corpus.__exit__(exc_type, exc, traceback)


def _write_plan(demo: _ExternalStagingDemo, *, configured: bool = False) -> None:
    args = ["plan", "--bundle", str(demo.bundle_path), "--out", str(demo.external_path)]
    if configured:
        args.extend(
            [
                "--host",
                "staging.example.invalid",
                "--user",
                "deploy",
                "--remote-dir",
                "/srv/eureka-public-alpha",
                "--base-url",
                "http://staging.example.invalid:8765",
                "--service-port",
                "8765",
            ]
        )
    result = _run_external_main(*args)
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _write_rehearsal(demo: _ExternalStagingDemo) -> None:
    result = _run_main(
        rehearsal_main,
        "run",
        "--bundle",
        str(demo.bundle_path),
        "--host",
        "127.0.0.1",
        "--port",
        "0",
        "--out",
        str(demo.demo.rehearsal_path),
    )
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _run_launch_gate(demo: _ExternalStagingDemo) -> "_Result":
    return _run_main(
        launch_gate_main,
        "audit",
        "--bundle",
        str(demo.bundle_path),
        "--rehearsal-report",
        str(demo.demo.rehearsal_report_path),
        "--artifact-gate-report",
        str(demo.demo.artifact_gate_report_path),
        "--corpus-gate-closeout",
        str(demo.demo.closeout_path / "corpus_gate_closeout.json"),
        "--external-staging-report",
        str(demo.report_path),
        "--out",
        str(demo.launch_gate_path),
    )


def _fake_probe(method: str, url: str) -> dict[str, object]:
    if "/workbench" in url:
        return {"method": method, "url": url, "status_code": 404, "body": "disabled"}
    if url.rstrip("/").endswith("/api/status"):
        body = {
            "read_only": True,
            "public_alpha_mode": True,
            "corpus_gate_status": "pass",
            "artifact_verified_count": 25,
            "reviewed_artifact_gate_count": 25,
            "live_metadata_enabled": False,
            "public_live_fanout": False,
            "workbench_exposed": False,
            "mutation_enabled": False,
            "downloads_enabled": False,
            "binary_verified_count": 0,
            "download_safe_count": 0,
            "execution_safe_count": 0,
            "rights_cleared_count": 0,
        }
        return {"method": method, "url": url, "status_code": 200, "body": json.dumps(body)}
    return {"method": method, "url": url, "status_code": 200, "body": "ok"}


def _run_external_main(*args: str) -> "_Result":
    return _run_main(external_staging_main, *args)


def _run_main(main_func: object, *args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main_func(list(args), stdout=stdout, stderr=stderr)  # type: ignore[misc]
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _deep_update(target: dict[str, object], patch: dict[str, object]) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)  # type: ignore[arg-type,index]
        else:
            target[key] = value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
