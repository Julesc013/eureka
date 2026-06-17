from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.public_alpha_ops_posture import build_default_plan
from runtime.local.public_alpha_ops_posture import validate_ops_posture
from runtime.local.public_alpha_ops_posture import write_plan
from scripts.eureka_public_alpha_ops_posture import main as ops_main
from tests.e2e.test_local_machine_public_exposure_plan import _ExposureDemo, _run_exposure_main


class PublicAlphaOpsPostureTests(unittest.TestCase):
    def test_default_plan_is_read_only_and_not_publicly_exposed(self) -> None:
        plan = _plan()

        self.assertTrue(plan["public_alpha_mode"])
        self.assertTrue(plan["public_read_only"])
        self.assertFalse(plan["public_exposure_enabled"])
        self.assertFalse(plan["public_workbench_exposed"])
        self.assertFalse(plan["public_mutation_enabled"])
        self.assertFalse(plan["live_metadata_enabled"])
        self.assertFalse(plan["public_live_fanout"])
        self.assertFalse(plan["downloads_enabled"])
        self.assertFalse(plan["uploads_enabled"])
        self.assertFalse(plan["extraction_enabled"])
        self.assertFalse(plan["model_provider_calls_enabled"])
        self.assertEqual(plan["status"], "READY_FOR_EXPOSURE_PLAN")
        self.assertEqual(plan["next_recommended_task"], "LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00")

    def test_validate_rejects_unsafe_public_posture(self) -> None:
        cases = (
            ("workbench", {"public_workbench_exposed": True}, "public_workbench_exposed must be false"),
            ("mutation", {"public_mutation_enabled": True}, "public_mutation_enabled must be false"),
            ("live_metadata", {"live_metadata_enabled": True}, "live_metadata_enabled must be false"),
            ("downloads", {"downloads_enabled": True}, "downloads_enabled must be false"),
            ("uploads", {"uploads_enabled": True}, "uploads_enabled must be false"),
            ("production", {"production_readiness_claimed": True}, "production_readiness_claimed must be false"),
        )
        for label, patch, expected in cases:
            with self.subTest(label=label):
                bad = copy.deepcopy(_plan())
                bad.update(patch)
                validation = validate_ops_posture(bad)

            self.assertEqual(validation["status"], "fail")
            self.assertTrue(any(expected in error for error in validation["errors"]), validation)

    def test_missing_rollback_posture_blocks_readiness(self) -> None:
        bad = copy.deepcopy(_plan())
        bad["rollback_posture"]["stop_server_command"] = ""

        validation = validate_ops_posture(bad)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["plan_status"], "BLOCKED")
        self.assertTrue(any(item["id"] == "rollback_posture_missing" for item in validation["ops_blockers"]))

    def test_missing_auth_or_noauth_choice_blocks_readiness(self) -> None:
        blocked = _plan(auth_posture="operator_decision_required")

        validation = validate_ops_posture(blocked)

        self.assertEqual(validation["plan_status"], "BLOCKED")
        self.assertTrue(any(item["id"] == "auth_or_noauth_posture_missing" for item in validation["ops_blockers"]))

    def test_cli_plan_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_ops_main("plan", "--out", tmp)
            plan_path = Path(tmp) / "ops_posture.json"
            report_path = Path(tmp) / "OPS_POSTURE_REPORT.md"
            plan_exists = plan_path.is_file()
            report_exists = report_path.is_file()
            payload = json.loads(plan_path.read_text(encoding="utf-8"))

        self.assertEqual(result.code, 0, result.stderr)
        self.assertTrue(plan_exists)
        self.assertTrue(report_exists)
        self.assertEqual(payload["status"], "READY_FOR_EXPOSURE_PLAN")
        self.assertIn("OPS_POSTURE_REPORT.md", result.stdout)

    def test_cli_validate_status_and_unsafe_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = write_plan(_plan(), tmp)
            validate = _run_ops_main("validate", "--plan", str(plan_path), "--strict")
            status = _run_ops_main("status", "--plan", str(plan_path))
            bad = copy.deepcopy(json.loads(plan_path.read_text(encoding="utf-8")))
            bad["public_mutation_enabled"] = True
            bad_path = Path(tmp) / "unsafe_ops_posture.json"
            bad_path.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            bad_validate = _run_ops_main("validate", "--plan", str(bad_path))

        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertIn("status: READY_FOR_EXPOSURE_PLAN", status.stdout)
        self.assertIn("next_recommended_task: LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00", status.stdout)
        self.assertNotEqual(bad_validate.code, 0)
        self.assertIn("public_mutation_enabled must be false", bad_validate.stderr)

    def test_exposure_plan_without_ops_posture_still_blocks_on_ops(self) -> None:
        with _ExposureDemo() as demo:
            result = _run_exposure_main(
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
            payload = json.loads(demo.plan_path.read_text(encoding="utf-8"))

        self.assertEqual(result.code, 0, result.stderr)
        ids = {item["id"] for item in payload["remaining_blockers"]}
        self.assertIn("ops_posture_missing", ids)
        self.assertEqual(payload["next_recommended_task"], "PUBLIC-ALPHA-OPS-POSTURE-00")

    def test_valid_ops_posture_satisfies_only_ops_blocker_for_exposure_plan(self) -> None:
        with _ExposureDemo() as demo:
            ops_path = write_plan(_plan(), demo.root / "ops")
            result = _run_exposure_main(
                "plan",
                "--local-machine-staging-report",
                str(demo.local_machine_report_path),
                "--release-check-report",
                str(demo.release_report_path),
                "--launch-gate-report",
                str(demo.launch_gate_report_path),
                "--ops-posture",
                str(ops_path),
                "--out",
                str(demo.exposure_path),
            )
            payload = json.loads(demo.plan_path.read_text(encoding="utf-8"))

        self.assertEqual(result.code, 0, result.stderr)
        ids = {item["id"] for item in payload["remaining_blockers"]}
        self.assertNotIn("ops_posture_missing", ids)
        self.assertNotIn("production_auth_or_noauth_posture_missing", ids)
        self.assertIn("public_exposure_not_configured", ids)
        self.assertIn("tls_domain_missing", ids)
        self.assertIn("full_discovery_not_passed", ids)
        self.assertIn("public_launch_approval_missing", ids)
        self.assertFalse(payload["public_exposure_enabled"])
        self.assertEqual(payload["next_recommended_task"], "LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00")


def _plan(**kwargs: object) -> dict[str, object]:
    values = {
        "generated_at": "2026-06-17T00:00:00Z",
        "branch": "dev",
        "head": "test-head",
        "worktree_status": "## dev...origin/dev",
    }
    values.update(kwargs)
    return build_default_plan(**values)  # type: ignore[arg-type]


def _run_ops_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = ops_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
