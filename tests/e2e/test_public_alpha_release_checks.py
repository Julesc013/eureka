from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import unittest

from runtime.local.public_alpha_release_checks import run_release_checks, validate_release_check_report
from scripts.eureka_public_alpha_launch_gate import main as launch_gate_main
from scripts.eureka_public_alpha_release_checks import main as release_checks_main
from tests.e2e.test_external_staging_host_provision import (
    _ExternalStagingDemo,
    _run_external_main,
    _run_launch_gate,
    _write_plan,
    _write_rehearsal,
)


class PublicAlphaReleaseChecksTests(unittest.TestCase):
    def test_release_check_run_writes_json_and_markdown_reports(self) -> None:
        with _ReleaseChecksDemo() as demo:
            report = _write_release_checks(demo)
            report_exists = demo.report_path.is_file()
            markdown_exists = demo.markdown_path.is_file()

        self.assertEqual(report["task_id"], "PUBLIC-ALPHA-RELEASE-CHECKS-00")
        self.assertEqual(report["status"], "PASS_WITH_WARNINGS")
        self.assertEqual(report["release_status"], "local_release_checks_green")
        self.assertTrue(report_exists)
        self.assertTrue(markdown_exists)

    def test_cli_validate_report_and_status(self) -> None:
        with _ReleaseChecksDemo() as demo:
            _write_release_checks(demo)
            validate = _run_release_main("validate-report", "--report", str(demo.report_path))
            status = _run_release_main("status", "--report", str(demo.report_path))

        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertIn("release_status: local_release_checks_green", status.stdout)

    def test_cli_run_skip_tests_writes_report(self) -> None:
        with _ReleaseChecksDemo() as demo:
            result = _run_release_main(
                "run",
                "--bundle",
                str(demo.bundle_path),
                "--corpus-gate-closeout",
                str(demo.closeout_report_path),
                "--rehearsal-report",
                str(demo.rehearsal_report_path),
                "--external-staging-report",
                str(demo.external_report_path),
                "--launch-gate-report",
                str(demo.launch_gate_report_path),
                "--out",
                str(demo.release_path),
                "--skip-tests",
                "--allow-dirty",
                "--no-require-origin-sync",
            )
            report = _load_json(demo.report_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["focused_test_status"], "skipped")
        self.assertIn("full_discovery_not_passed", report["blocker_categories"]["release_process_blockers"])

    def test_validate_report_rejects_missing_required_fields(self) -> None:
        with _ReleaseChecksDemo() as demo:
            report = _write_release_checks(demo)
            bad = copy.deepcopy(report)
            bad.pop("blocker_categories")
            bad_path = demo.release_path / "bad_release_report.json"
            _write_json(bad_path, bad)
            errors = validate_release_check_report(bad_path)

        self.assertIn("missing required field: blocker_categories", errors)

    def test_validate_report_rejects_unproven_pass_claims(self) -> None:
        cases = (
            ("full_discovery", {"full_discovery_status": "pass", "full_discovery_report_digest": ""}, "full discovery passed without report evidence"),
            ("release_promotion", {"release_promotion_status": "pass", "release_promotion_report_digest": ""}, "release promotion passed without report evidence"),
            ("external_dry_run", {"external_staging_status": "pass", "external_staging_deployment_status": "dry_run_pass"}, "external staging pass while external report is dry-run only"),
            ("secret", {"warnings": ["token=local-dev-token"]}, "forbidden secret marker"),
            ("binary", {"binary_verified_count": 1}, "binary_verified_count must remain 0"),
        )
        for label, patch, expected in cases:
            with self.subTest(label=label), _ReleaseChecksDemo() as demo:
                report = _write_release_checks(demo)
                bad = copy.deepcopy(report)
                bad.update(patch)
                bad_path = demo.release_path / f"bad_{label}.json"
                _write_json(bad_path, bad)

                errors = validate_release_check_report(bad_path)

            self.assertTrue(any(expected in error for error in errors), errors)

    def test_dirty_git_and_generated_cleanliness_failures_are_blockers(self) -> None:
        cases = (
            ("dirty", _runner_with_dirty_git, "git_worktree_dirty"),
            ("generated", _runner_with_generated_failure, "generated_artifact_cleanliness_failed"),
        )
        for label, runner, expected in cases:
            with self.subTest(label=label), _ReleaseChecksDemo() as demo:
                report = _write_release_checks(demo, runner=runner)

            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(item["id"] == expected for item in report["blockers"]))

    def test_invalid_inputs_or_not_green_rehearsal_fail_cleanly(self) -> None:
        cases = (
            ("corpus", "corpus_gate_validate", "corpus_gate_validate_failed"),
            ("staging", "staging_validate", "staging_validate_failed"),
            ("rehearsal_validate", "rehearsal_validate", "rehearsal_validate_failed"),
        )
        for label, failing_id, expected in cases:
            with self.subTest(label=label), _ReleaseChecksDemo() as demo:
                report = _write_release_checks(demo, runner=_runner_failing(failing_id))

            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(item["id"] == expected for item in report["blockers"]))

        with _ReleaseChecksDemo() as demo:
            rehearsal = _load_json(demo.rehearsal_report_path)
            rehearsal["status"] = "FAIL"
            _write_json(demo.rehearsal_report_path, rehearsal)
            report = _write_release_checks(demo)

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(item["id"] == "local_rehearsal_not_green" for item in report["blockers"]))

    def test_missing_full_discovery_and_release_promotion_remain_blockers(self) -> None:
        with _ReleaseChecksDemo() as demo:
            report = _write_release_checks(demo)

        categories = report["blocker_categories"]
        self.assertEqual(report["full_discovery_status"], "not_run")
        self.assertEqual(report["release_promotion_status"], "not_run")
        self.assertIn("full_discovery_not_passed", categories["release_process_blockers"])
        self.assertIn("release_promotion_not_passed", categories["release_process_blockers"])
        self.assertEqual(report["next_recommended_task"], "EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG")

    def test_launch_gate_consumes_release_check_report(self) -> None:
        with _ReleaseChecksDemo() as demo:
            _write_release_checks(demo)
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
                "--release-check-report",
                str(demo.report_path),
                "--out",
                str(demo.launch_gate_path),
            )
            launch_report = _load_json(demo.launch_gate_report_path)

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(launch_report["release_check_report_status"], "pass_with_warnings")
        self.assertEqual(launch_report["release_check_release_status"], "local_release_checks_green")
        self.assertIn("external_staging_host_missing", launch_report["blocker_categories"]["deployment_blockers"])
        self.assertIn("full_discovery_not_passed", launch_report["blocker_categories"]["release_process_blockers"])
        self.assertEqual(launch_report["launch_status"], "BLOCKED")

    def test_release_checks_do_not_mutate_inputs(self) -> None:
        with _ReleaseChecksDemo() as demo:
            paths = [
                demo.bundle_path / "manifest.json",
                demo.bundle_path / "public_search_index.json",
                demo.bundle_path / "public_runtime_config.json",
                demo.closeout_report_path,
                demo.rehearsal_report_path,
                demo.external_report_path,
                demo.launch_gate_report_path,
            ]
            before = {path: _sha256(path) for path in paths}
            _write_release_checks(demo)
            after = {path: _sha256(path) for path in paths}

        self.assertEqual(before, after)


class _ReleaseChecksDemo:
    def __enter__(self) -> "_ReleaseChecksDemo":
        self._external = _ExternalStagingDemo()
        self.demo = self._external.__enter__()
        _write_plan(self.demo)
        _run_external_main("deploy", "--plan", str(self.demo.plan_path), "--dry-run")
        _run_external_main("smoke", "--plan", str(self.demo.plan_path))
        _write_rehearsal(self.demo)
        _run_launch_gate(self.demo)
        self.root = self.demo.root
        self.bundle_path = self.demo.bundle_path
        self.closeout_report_path = self.demo.demo.closeout_path / "corpus_gate_closeout.json"
        self.rehearsal_report_path = self.demo.demo.rehearsal_report_path
        self.external_report_path = self.demo.report_path
        self.launch_gate_path = self.demo.launch_gate_path
        self.launch_gate_report_path = self.demo.launch_gate_report_path
        self.artifact_gate_report_path = self.demo.demo.artifact_gate_report_path
        self.release_path = self.root / "release-checks"
        self.report_path = self.release_path / "release_check_report.json"
        self.markdown_path = self.release_path / "RELEASE_CHECK_REPORT.md"
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._external.__exit__(exc_type, exc, traceback)


def _write_release_checks(demo: _ReleaseChecksDemo, *, runner: object = None) -> dict[str, object]:
    return run_release_checks(
        bundle=demo.bundle_path,
        corpus_gate_closeout=demo.closeout_report_path,
        rehearsal_report=demo.rehearsal_report_path,
        external_staging_report=demo.external_report_path,
        launch_gate_report=demo.launch_gate_report_path,
        out_dir=demo.release_path,
        command_runner=runner or _passing_runner,
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


def _runner_with_dirty_git(command: object) -> dict[str, object]:
    result = _passing_runner(command)
    if result["command"][:3] == ["git", "status", "--short"]:
        result["stdout"] = "## dev...origin/dev\n M runtime/local/public_alpha_release_checks.py\n"
    return result


def _runner_with_generated_failure(command: object) -> dict[str, object]:
    result = _passing_runner(command)
    if "check_generated_artifact_cleanliness.py" in " ".join(str(item) for item in command):
        result["returncode"] = 1
        result["stderr"] = "generated artifact is tracked\n"
    return result


def _runner_failing(command_id: str) -> object:
    def run(command: object) -> dict[str, object]:
        result = _passing_runner(command)
        text = " ".join(str(item) for item in command)
        should_fail = (
            (command_id == "corpus_gate_validate" and "eureka_public_alpha_corpus_gate.py" in text)
            or (command_id == "staging_validate" and "eureka_staging.py" in text)
            or (command_id == "rehearsal_validate" and "eureka_public_alpha_rehearsal.py" in text)
        )
        if should_fail:
            result["returncode"] = 1
            result["stderr"] = f"{command_id} failed\n"
        return result

    return run


def _run_release_main(*args: str) -> "_Result":
    return _run_main(release_checks_main, *args)


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
