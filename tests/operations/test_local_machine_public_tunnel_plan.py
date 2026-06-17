from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.local_machine_public_exposure import build_tunnel_plan
from runtime.local.local_machine_public_exposure import validate_tunnel_plan
from runtime.local.local_machine_public_exposure import write_tunnel_plan
from runtime.local.public_alpha_ops_posture import build_default_plan
from runtime.local.public_alpha_ops_posture import write_plan as write_ops_plan
from scripts.eureka_local_machine_public_exposure import main as exposure_main


class LocalMachinePublicTunnelPlanTests(unittest.TestCase):
    def test_reverse_tunnel_without_public_url_is_ready_for_operator_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path = _write_ops(tmp)
            plan = _tunnel_plan(ops_path)
            validation = validate_tunnel_plan(plan)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["plan_status"], "READY_FOR_OPERATOR_URL")
        self.assertFalse(plan["public_exposure_enabled"])
        self.assertFalse(plan["tunnel_started"])
        self.assertEqual(validation["next_recommended_task"], "LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00")
        self.assertTrue(any(item["id"] == "BLOCKED_ON_PUBLIC_URL" for item in validation["blockers"]))

    def test_reverse_tunnel_with_https_url_is_ready_for_tunnel_rehearsal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path = _write_ops(tmp)
            plan = _tunnel_plan(ops_path, public_url="https://alpha.example.test")
            validation = validate_tunnel_plan(plan)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["plan_status"], "READY_FOR_TUNNEL_REHEARSAL")
        self.assertEqual(plan["public_url_status"], "planned")
        self.assertEqual(plan["provider_https_status"], "planned")
        self.assertEqual(validation["next_recommended_task"], "LOCAL-MACHINE-PUBLIC-TUNNEL-00")

    def test_missing_ops_posture_blocks(self) -> None:
        plan = _tunnel_plan(None)
        validation = validate_tunnel_plan(plan)

        self.assertEqual(validation["status"], "fail")
        self.assertEqual(validation["plan_status"], "BLOCKED")
        self.assertIn("ops posture is missing", validation["errors"])

    def test_invalid_ops_posture_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops = _ops()
            ops["public_mutation_enabled"] = True
            ops_path = Path(tmp) / "bad_ops.json"
            ops_path.write_text(json.dumps(ops, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            plan = _tunnel_plan(ops_path)
            validation = validate_tunnel_plan(plan)

        self.assertEqual(validation["status"], "fail")
        self.assertIn("ops posture is not valid", validation["errors"])

    def test_public_unsafe_flags_fail_validation(self) -> None:
        cases = (
            ("mutation", "public_mutation_enabled"),
            ("workbench", "public_workbench_exposed"),
            ("live_metadata", "live_metadata_enabled"),
            ("downloads", "downloads_enabled"),
            ("uploads", "uploads_enabled"),
        )
        for label, key in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                ops_path = _write_ops(tmp)
                plan = _tunnel_plan(ops_path)
                bad = copy.deepcopy(plan)
                bad["safety_flags"][key] = True
                validation = validate_tunnel_plan(bad)

            self.assertEqual(validation["status"], "fail")
            self.assertTrue(any(key in error for error in validation["errors"]), validation)

    def test_risky_modes_require_explicit_approval(self) -> None:
        for mode in ("router_port_forward", "direct_public_ip"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                ops_path = _write_ops(tmp)
                plan = _tunnel_plan(ops_path, exposure_mode=mode)
                validation = validate_tunnel_plan(plan)
                approved = _tunnel_plan(ops_path, exposure_mode=mode, approve_risky_mode=True)
                approved_validation = validate_tunnel_plan(approved)

            self.assertEqual(validation["status"], "fail")
            self.assertTrue(any("requires explicit operator approval" in error for error in validation["errors"]))
            self.assertEqual(approved_validation["status"], "pass")

    def test_missing_rollback_or_route_denylist_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path = _write_ops(tmp)
            plan = _tunnel_plan(ops_path)
            missing_rollback = copy.deepcopy(plan)
            missing_rollback["rollback_steps"] = []
            missing_routes = copy.deepcopy(plan)
            missing_routes["route_denylist"] = []

        rollback_validation = validate_tunnel_plan(missing_rollback)
        route_validation = validate_tunnel_plan(missing_routes)
        self.assertEqual(rollback_validation["status"], "fail")
        self.assertIn("rollback steps are missing", rollback_validation["errors"])
        self.assertEqual(route_validation["status"], "fail")
        self.assertTrue(any("route denylist missing" in error for error in route_validation["errors"]))

    def test_cli_plan_validate_status_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path = _write_ops(tmp)
            out = Path(tmp) / "exposure"
            plan_result = _run_exposure_main("plan", "--mode", "reverse_tunnel", "--ops-posture", str(ops_path), "--out", str(out))
            plan_path = out / "exposure_plan.json"
            report_path = out / "EXPOSURE_PLAN_REPORT.md"
            validate_result = _run_exposure_main("validate", "--plan", str(plan_path), "--strict")
            status_result = _run_exposure_main("status", "--plan", str(plan_path))
            report_result = _run_exposure_main("report", "--plan", str(plan_path))
            plan_exists = plan_path.is_file()
            report_exists = report_path.is_file()
            payload = json.loads(plan_path.read_text(encoding="utf-8"))

        self.assertEqual(plan_result.code, 0, plan_result.stderr)
        self.assertTrue(plan_exists)
        self.assertTrue(report_exists)
        self.assertEqual(validate_result.code, 0, validate_result.stderr)
        self.assertEqual(status_result.code, 0, status_result.stderr)
        self.assertEqual(report_result.code, 0, report_result.stderr)
        self.assertIn("READY_FOR_OPERATOR_URL", status_result.stdout)
        self.assertFalse(payload["public_exposure_enabled"])
        self.assertFalse(payload["tunnel_started"])
        self.assertFalse(payload["proxy_started"])
        self.assertFalse(payload["server_started_by_this_task"])

    def test_cli_validate_fails_for_unsafe_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path = _write_ops(tmp)
            out = Path(tmp) / "exposure"
            _run_exposure_main("plan", "--mode", "reverse_tunnel", "--ops-posture", str(ops_path), "--out", str(out))
            plan_path = out / "exposure_plan.json"
            payload = json.loads(plan_path.read_text(encoding="utf-8"))
            payload["public_exposure_enabled"] = True
            plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result = _run_exposure_main("validate", "--plan", str(plan_path))

        self.assertNotEqual(result.code, 0)
        self.assertIn("public_exposure_enabled must remain false", result.stderr)

    def test_write_plan_outputs_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path = _write_ops(tmp)
            out = Path(tmp) / "out"
            plan_path = write_tunnel_plan(_tunnel_plan(ops_path, out_dir=out), out)
            report_exists = (out / "EXPOSURE_PLAN_REPORT.md").is_file()

        self.assertEqual(plan_path.name, "exposure_plan.json")
        self.assertTrue(report_exists)


def _ops() -> dict[str, object]:
    return build_default_plan(
        generated_at="2026-06-17T00:00:00Z",
        branch="dev",
        head="test-head",
        worktree_status="## dev...origin/dev",
    )


def _write_ops(root: str | Path) -> Path:
    return write_ops_plan(_ops(), root)


def _tunnel_plan(
    ops_path: str | Path | None,
    *,
    exposure_mode: str = "reverse_tunnel",
    public_url: str = "",
    approve_risky_mode: bool = False,
    out_dir: str | Path = ".eureka/public-alpha/exposure/latest",
) -> dict[str, object]:
    return build_tunnel_plan(
        ops_posture=ops_path,
        out_dir=out_dir,
        exposure_mode=exposure_mode,
        public_url=public_url,
        approve_risky_mode=approve_risky_mode,
        generated_at="2026-06-17T00:00:00Z",
        branch="dev",
        head="test-head",
        worktree_status="## dev...origin/dev",
    )


def _run_exposure_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = exposure_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
