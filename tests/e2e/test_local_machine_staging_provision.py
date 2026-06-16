from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import unittest

from runtime.local.public_alpha_release_checks import run_release_checks
from runtime.local.local_machine_staging_mvp import build_plan, validate_report
from scripts.eureka_local_machine_staging import main as local_machine_main
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from tests.e2e.test_public_alpha_corpus_gate_closeout import _CorpusCloseoutDemo, _package_with_closeout, _write_closeout


class LocalMachineStagingProvisionTests(unittest.TestCase):
    def test_plan_validate_smoke_validate_and_status(self) -> None:
        with _LocalMachineDemo() as demo:
            plan = _run_local_machine_main("plan", "--bundle", str(demo.bundle_path), "--out", str(demo.local_machine_path))
            validate_plan = _run_local_machine_main("validate-plan", "--plan", str(demo.plan_path))
            smoke = _write_local_machine_report(demo)
            validate_smoke = _run_local_machine_main("validate-report", "--report", str(demo.report_path))
            status = _run_local_machine_main("status", "--report", str(demo.report_path))
            report = _load_json(demo.report_path)

        self.assertEqual(plan.code, 0, plan.stderr)
        self.assertEqual(validate_plan.code, 0, validate_plan.stderr)
        self.assertEqual(smoke.code, 0, smoke.stderr)
        self.assertEqual(validate_smoke.code, 0, validate_smoke.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertEqual(report["local_machine_staging_status"], "pass")
        self.assertEqual(report["corpus_gate_status"], "pass")
        self.assertEqual(report["reviewed_artifact_gate_count"], 25)
        self.assertEqual(report["artifact_verified_count"], 25)
        self.assertFalse(report["public_exposure"])
        self.assertFalse(report["live_metadata_enabled"])
        self.assertFalse(report["workbench_exposed"])
        self.assertFalse(report["mutation_enabled"])
        self.assertIn("local_machine_staging_status: pass", status.stdout)

    def test_validate_plan_rejects_non_loopback_host(self) -> None:
        with _LocalMachineDemo() as demo:
            bad_plan = build_plan(demo.bundle_path, out_dir=demo.local_machine_path, host="0.0.0.0", port=8765)
            _write_json(demo.plan_path, bad_plan)
            result = _run_local_machine_main("validate-plan", "--plan", str(demo.plan_path))

        self.assertEqual(result.code, 1)
        self.assertIn("host must be loopback", result.stderr)

    def test_validate_report_rejects_unsafe_claims(self) -> None:
        cases = (
            ("workbench", {"workbench_exposed": True}, "workbench_exposed must be false"),
            ("live", {"live_metadata_enabled": True}, "live_metadata_enabled must be false"),
            ("mutation", {"mutation_enabled": True}, "mutation_enabled must be false"),
            ("download", {"downloads_enabled": True}, "downloads_enabled must be false"),
            ("binary", {"binary_verified_count": 1}, "binary_verified_count must remain 0"),
            ("execution", {"execution_safe_count": 1}, "execution_safe_count must remain 0"),
            ("rights", {"rights_cleared_count": 1}, "rights_cleared_count must remain 0"),
        )
        for label, patch, expected in cases:
            with self.subTest(label=label), _LocalMachineDemo() as demo:
                _write_local_machine_report(demo)
                report = _load_json(demo.report_path)
                bad = copy.deepcopy(report)
                bad.update(patch)
                bad_path = demo.local_machine_path / f"bad_{label}.json"
                _write_json(bad_path, bad)
                errors = validate_report(bad_path)

            self.assertTrue(any(expected in error for error in errors), errors)

    def test_release_checks_consume_local_machine_staging_report(self) -> None:
        with _LocalMachineDemo() as demo:
            _write_local_machine_report(demo)
            _write_rehearsal(demo)
            _write_external_missing_config_report(demo)
            _write_launch_gate(demo)
            release = run_release_checks(
                bundle=demo.bundle_path,
                corpus_gate_closeout=demo.closeout_report_path,
                rehearsal_report=demo.rehearsal_report_path,
                external_staging_report=demo.external_report_path,
                local_machine_staging_report=demo.report_path,
                launch_gate_report=demo.launch_gate_report_path,
                out_dir=demo.release_path,
                command_runner=_passing_runner,
            )

        self.assertEqual(release["local_machine_staging_status"], "pass")
        self.assertEqual(release["local_machine_staging_report_status"], "PASS_WITH_WARNINGS")
        self.assertIn("external_staging_not_smoked", release["blocker_categories"]["external_staging_blockers"])
        self.assertEqual(release["next_recommended_task"], "LOCAL-MACHINE-PUBLIC-EXPOSURE-PLAN-00")

    def test_launch_gate_consumes_local_machine_report_and_remains_blocked(self) -> None:
        with _LocalMachineDemo() as demo:
            _write_local_machine_report(demo)
            _write_rehearsal(demo)
            _write_external_missing_config_report(demo)
            result = _write_launch_gate(demo)
            report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["local_machine_staging_status"], "pass")
        self.assertFalse(report["local_machine_public_exposure"])
        self.assertEqual(report["launch_status"], "BLOCKED")
        self.assertIn("external_staging_host_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertIn("production_hosting_missing", report["blocker_categories"]["deployment_blockers"])
        self.assertEqual(report["next_recommended_task"], "LOCAL-MACHINE-PUBLIC-EXPOSURE-PLAN-00")

    def test_smoke_does_not_mutate_bundle(self) -> None:
        with _LocalMachineDemo() as demo:
            before = _bundle_hashes(demo.bundle_path)
            _write_local_machine_report(demo)
            after = _bundle_hashes(demo.bundle_path)
            report = _load_json(demo.report_path)

        self.assertEqual(before, after)
        self.assertFalse(report["mutation_checks"]["any_mutated"])


class _LocalMachineDemo:
    def __enter__(self) -> "_LocalMachineDemo":
        self._corpus = _CorpusCloseoutDemo()
        self.demo = self._corpus.__enter__()
        _write_closeout(self.demo)
        _package_with_closeout(self.demo)
        self.root = self.demo.root
        self.bundle_path = self.demo.bundle_path
        self.closeout_report_path = self.demo.closeout_path / "corpus_gate_closeout.json"
        self.artifact_gate_report_path = self.demo.artifact_gate_report_path
        self.local_machine_path = self.root / "local-machine-staging"
        self.plan_path = self.local_machine_path / "local_machine_staging_plan.json"
        self.report_path = self.local_machine_path / "local_machine_staging_report.json"
        self.rehearsal_path = self.root / "rehearsal"
        self.rehearsal_report_path = self.rehearsal_path / "rehearsal_report.json"
        self.external_path = self.root / "external-staging"
        self.external_report_path = self.external_path / "external_staging_report.json"
        self.launch_gate_path = self.root / "launch-gate"
        self.launch_gate_report_path = self.launch_gate_path / "launch_gate_report.json"
        self.release_path = self.root / "release-checks"
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._corpus.__exit__(exc_type, exc, traceback)


def _write_local_machine_report(demo: _LocalMachineDemo) -> "_Result":
    return _run_local_machine_main(
        "smoke",
        "--bundle",
        str(demo.bundle_path),
        "--host",
        "127.0.0.1",
        "--port",
        "0",
        "--out",
        str(demo.local_machine_path),
    )


def _write_rehearsal(demo: _LocalMachineDemo) -> None:
    result = _run_rehearsal_main(
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
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _write_external_missing_config_report(demo: _LocalMachineDemo) -> None:
    _write_json(
        demo.external_report_path,
        {
            "schema_version": "eureka.external_staging_report.v0",
            "task_id": "EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG",
            "status": "PASS_WITH_WARNINGS",
            "deployment_status": "missing_config",
            "smoke_status": "blocked",
            "warnings": ["external staging config missing"],
            "blockers": ["external staging host/base_url missing"],
        },
    )


def _write_launch_gate(demo: _LocalMachineDemo) -> "_Result":
    return _run_launch_gate_main(
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
        str(demo.report_path),
        "--out",
        str(demo.launch_gate_path),
    )


def _passing_runner(command: object) -> dict[str, object]:
    text = " ".join(str(item) for item in command)
    stdout = "ok\n"
    if text.startswith("git status"):
        stdout = "## dev...origin/dev\n"
    elif text.startswith("git rev-parse HEAD") or text.startswith("git rev-parse origin/dev"):
        stdout = "abc123\n"
    elif "check_generated_artifact_cleanliness.py" in text:
        stdout = json.dumps({"status": "pass"}) + "\n"
    return {"command": list(command), "returncode": 0, "stdout": stdout, "stderr": ""}


def _run_local_machine_main(*args: str) -> "_Result":
    return _run_main(local_machine_main, *args)


def _run_rehearsal_main(*args: str) -> "_Result":
    return _run_main(rehearsal_main, *args)


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
