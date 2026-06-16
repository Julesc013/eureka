from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import unittest

from runtime.local.local_machine_public_exposure import build_report, validate_plan, validate_report
from runtime.local.public_alpha_release_checks import run_release_checks
from scripts.eureka_local_machine_public_exposure import main as exposure_main
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from tests.e2e.test_local_machine_staging_provision import (
    _LocalMachineDemo,
    _passing_runner,
    _write_external_missing_config_report,
    _write_launch_gate,
    _write_local_machine_report,
    _write_rehearsal,
)


class LocalMachinePublicExposurePlanTests(unittest.TestCase):
    def test_plan_validate_status_report_and_validate_report(self) -> None:
        with _ExposureDemo() as demo:
            plan = _write_exposure_plan(demo)
            validate_plan_result = _run_exposure_main("validate-plan", "--plan", str(demo.plan_path))
            status = _run_exposure_main("status", "--plan", str(demo.plan_path))
            report = _write_exposure_report(demo)
            validate_report_result = _run_exposure_main("validate-report", "--report", str(demo.report_path))
            payload = _load_json(demo.report_path)

        self.assertEqual(plan.code, 0, plan.stderr)
        self.assertEqual(validate_plan_result.code, 0, validate_plan_result.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertEqual(report.code, 0, report.stderr)
        self.assertEqual(validate_report_result.code, 0, validate_report_result.stderr)
        self.assertEqual(payload["selected_hosting_path"], "local_machine")
        self.assertEqual(payload["exposure_mode"], "loopback_only")
        self.assertFalse(payload["public_exposure_enabled"])
        self.assertTrue(payload["external_staging_deferred"])
        self.assertEqual(payload["public_readiness_status"], "blocked")
        self.assertIn("remaining_blockers: 7", status.stdout)

    def test_validate_plan_rejects_unsafe_claims(self) -> None:
        cases = (
            ("public", {"public_exposure_enabled": True}, "public_exposure_enabled must remain false"),
            ("workbench", {"public_workbench_exposed": True}, "public_workbench_exposed must be false"),
            ("mutation", {"public_mutation_enabled": True}, "public_mutation_enabled must be false"),
            ("live", {"live_metadata_enabled": True}, "live_metadata_enabled must be false"),
            ("downloads", {"downloads_enabled": True}, "downloads_enabled must be false"),
            ("binary", {"binary_verified_count": 1}, "binary_verified_count must remain 0"),
            ("corpus", {"corpus_gate_status": "blocked"}, "corpus_gate_status must be pass"),
            ("tls", {"tls_status": "validated"}, "TLS validated without evidence"),
            ("domain", {"domain_status": "configured"}, "domain configured without evidence"),
            ("auth", {"production_auth_or_noauth_posture": "readonly_noauth_approved"}, "no-auth approved without evidence"),
        )
        for label, patch, expected in cases:
            with self.subTest(label=label), _ExposureDemo() as demo:
                _write_exposure_plan(demo)
                plan = _load_json(demo.plan_path)
                bad = copy.deepcopy(plan)
                bad.update(patch)
                bad_path = demo.exposure_path / f"bad_{label}.json"
                _write_json(bad_path, bad)
                errors = validate_plan(bad_path)

            self.assertTrue(any(expected in error for error in errors), errors)

    def test_validate_report_rejects_launch_ready_and_unsafe_posture(self) -> None:
        cases = (
            ("ready", {"public_readiness_status": "launch_ready"}, "must not claim launch readiness"),
            ("public", {"public_exposure_enabled": True}, "public_exposure_enabled must remain false"),
            ("tls", {"tls_status": "validated"}, "TLS validated without evidence"),
            ("auth", {"production_auth_or_noauth_posture": "readonly_noauth_approved"}, "no-auth approved without evidence"),
            ("download", {"download_safe_count": 1}, "download_safe_count must remain 0"),
        )
        for label, patch, expected in cases:
            with self.subTest(label=label), _ExposureDemo() as demo:
                _write_exposure_plan(demo)
                _write_exposure_report(demo)
                report = _load_json(demo.report_path)
                bad = copy.deepcopy(report)
                bad.update(patch)
                bad_path = demo.exposure_path / f"bad_report_{label}.json"
                _write_json(bad_path, bad)
                errors = validate_report(bad_path)

            self.assertTrue(any(expected in error for error in errors), errors)

    def test_release_checks_consume_public_exposure_report(self) -> None:
        with _ExposureDemo() as demo:
            _write_exposure_plan(demo)
            _write_exposure_report(demo)
            release = run_release_checks(
                bundle=demo.bundle_path,
                corpus_gate_closeout=demo.closeout_report_path,
                rehearsal_report=demo.rehearsal_report_path,
                external_staging_report=demo.external_report_path,
                local_machine_staging_report=demo.local_machine_report_path,
                local_machine_public_exposure_report=demo.report_path,
                launch_gate_report=demo.launch_gate_report_path,
                out_dir=demo.release_path,
                command_runner=_passing_runner,
            )

        self.assertEqual(release["local_machine_public_exposure_status"], "pass")
        self.assertEqual(release["selected_hosting_path"], "local_machine")
        self.assertEqual(release["exposure_mode"], "loopback_only")
        self.assertFalse(release["public_exposure_enabled"])
        self.assertTrue(release["external_staging_deferred"])
        self.assertNotIn("external_staging_not_smoked", release["blocker_categories"]["external_staging_blockers"])
        self.assertIn("public_exposure_not_configured", release["blocker_categories"]["deployment_blockers"])
        self.assertEqual(release["next_recommended_task"], "PUBLIC-ALPHA-OPS-POSTURE-00")

    def test_launch_gate_consumes_public_exposure_report_and_defers_external_ssh(self) -> None:
        with _ExposureDemo() as demo:
            _write_exposure_plan(demo)
            _write_exposure_report(demo)
            result = _run_launch_gate_main(
                "audit",
                "--bundle",
                str(demo.bundle_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--artifact-gate-report",
                str(demo.artifact_gate_report_path),
                "--corpus-gate-closeout",
                str(demo.closeout_report_path),
                "--external-staging-report",
                str(demo.external_report_path),
                "--local-machine-staging-report",
                str(demo.local_machine_report_path),
                "--local-machine-public-exposure-report",
                str(demo.report_path),
                "--release-check-report",
                str(demo.release_report_path),
                "--out",
                str(demo.launch_gate_path),
            )
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["external_staging_host_status"], "deferred")
        self.assertTrue(report["external_staging_deferred"])
        self.assertEqual(report["local_machine_public_exposure_status"], "pass")
        self.assertNotIn("external_staging_host_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertIn("public_exposure_not_configured", report["blocker_categories"]["deployment_blockers"])
        self.assertIn("ops_posture_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertIn("full_discovery_not_passed", report["blocker_categories"]["release_process_blockers"])
        self.assertIn("public_launch_approval_missing", report["blocker_categories"]["approval_blockers"])
        self.assertEqual(report["launch_status"], "BLOCKED")
        self.assertEqual(report["next_recommended_task"], "PUBLIC-ALPHA-OPS-POSTURE-00")

    def test_plan_and_report_do_not_mutate_inputs(self) -> None:
        with _ExposureDemo() as demo:
            paths = [
                demo.bundle_path / "manifest.json",
                demo.bundle_path / "public_search_index.json",
                demo.bundle_path / "public_runtime_config.json",
                demo.local_machine_report_path,
                demo.rehearsal_report_path,
                demo.external_report_path,
                demo.launch_gate_report_path,
                demo.release_report_path,
            ]
            before = {path: _sha256(path) for path in paths}
            _write_exposure_plan(demo)
            _write_exposure_report(demo)
            after = {path: _sha256(path) for path in paths}

        self.assertEqual(before, after)


class _ExposureDemo:
    def __enter__(self) -> "_ExposureDemo":
        self._local = _LocalMachineDemo()
        self.demo = self._local.__enter__()
        _write_local_machine_report(self.demo)
        _write_rehearsal(self.demo)
        _write_external_missing_config_report(self.demo)
        _write_launch_gate(self.demo)
        self.root = self.demo.root
        self.bundle_path = self.demo.bundle_path
        self.closeout_report_path = self.demo.closeout_report_path
        self.artifact_gate_report_path = self.demo.artifact_gate_report_path
        self.local_machine_report_path = self.demo.report_path
        self.rehearsal_report_path = self.demo.rehearsal_report_path
        self.external_report_path = self.demo.external_report_path
        self.launch_gate_path = self.demo.launch_gate_path
        self.launch_gate_report_path = self.demo.launch_gate_report_path
        self.release_path = self.demo.release_path
        self.release_report_path = self.release_path / "release_check_report.json"
        self.exposure_path = self.root / "local-machine-public-exposure"
        self.plan_path = self.exposure_path / "local_machine_public_exposure_plan.json"
        self.report_path = self.exposure_path / "local_machine_public_exposure_report.json"
        release = run_release_checks(
            bundle=self.bundle_path,
            corpus_gate_closeout=self.closeout_report_path,
            rehearsal_report=self.rehearsal_report_path,
            external_staging_report=self.external_report_path,
            local_machine_staging_report=self.local_machine_report_path,
            launch_gate_report=self.launch_gate_report_path,
            out_dir=self.release_path,
            command_runner=_passing_runner,
        )
        if release["status"] == "FAIL":
            raise AssertionError(release)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._local.__exit__(exc_type, exc, traceback)


def _write_exposure_plan(demo: _ExposureDemo) -> "_Result":
    return _run_exposure_main(
        "plan",
        "--local-machine-staging-report",
        str(demo.local_machine_report_path),
        "--release-check-report",
        str(demo.release_report_path),
        "--launch-gate-report",
        str(demo.launch_gate_report_path),
        "--out",
        str(demo.exposure_path),
    )


def _write_exposure_report(demo: _ExposureDemo) -> "_Result":
    return _run_exposure_main("report", "--plan", str(demo.plan_path), "--out", str(demo.exposure_path))


def _run_exposure_main(*args: str) -> "_Result":
    return _run_main(exposure_main, *args)


def _run_launch_gate_main(*args: str) -> "_Result":
    return _run_main(launch_gate_main, *args)


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
