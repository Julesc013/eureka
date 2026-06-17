from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.local_machine_public_exposure import build_operator_choice
from runtime.local.local_machine_public_exposure import build_tunnel_plan
from runtime.local.local_machine_public_exposure import validate_operator_choice
from runtime.local.local_machine_public_exposure import write_operator_choice
from runtime.local.local_machine_public_exposure import write_tunnel_plan
from runtime.local.public_alpha_ops_posture import build_default_plan
from runtime.local.public_alpha_ops_posture import write_plan as write_ops_plan
from scripts.eureka_local_machine_public_exposure import main as exposure_main


class LocalMachinePublicTunnelOperatorChoiceTests(unittest.TestCase):
    def test_default_operator_required_choice_is_safe_and_blocked_on_operator_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            choice = _choice(plan_path, ops_path)
            validation = validate_operator_choice(choice)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["choice_status"], "BLOCKED_ON_OPERATOR_PROVIDER_URL")
        self.assertTrue(validation["safe"])
        self.assertFalse(choice["public_exposure_enabled"])
        self.assertFalse(choice["tunnel_started"])
        self.assertEqual(choice["provider_name"], "OPERATOR_REQUIRED")
        self.assertTrue(any(item["id"] == "BLOCKED_ON_OPERATOR_PROVIDER_URL" for item in validation["blockers"]))

    def test_valid_provider_choice_can_be_ready_for_tunnel_rehearsal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            choice = _choice(
                plan_path,
                ops_path,
                provider_name="ngrok",
                public_url="https://eureka-alpha.example.test",
                staged_record_id="fixture-record-1",
                confirm_remote_synced=True,
            )
            validation = validate_operator_choice(choice)

        self.assertEqual(validation["status"], "pass")
        self.assertEqual(validation["choice_status"], "READY_FOR_TUNNEL_REHEARSAL")
        self.assertEqual(validation["recommended_next_task"], "LOCAL-MACHINE-PUBLIC-TUNNEL-00")

    def test_missing_or_invalid_inputs_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            missing_ops = _choice(plan_path, None)
            missing_plan = _choice(None, ops_path)
            bad_ops = _ops()
            bad_ops["public_mutation_enabled"] = True
            bad_ops_path = Path(tmp) / "bad_ops.json"
            bad_ops_path.write_text(json.dumps(bad_ops, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            invalid_ops = _choice(plan_path, bad_ops_path)

        for choice in (missing_ops, missing_plan, invalid_ops):
            with self.subTest(choice=choice.get("status")):
                validation = validate_operator_choice(choice)
                self.assertEqual(validation["status"], "fail")
                self.assertEqual(validation["choice_status"], "BLOCKED_UNSAFE")

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
                ops_path, plan_path = _write_inputs(tmp)
                choice = _choice(plan_path, ops_path)
                bad = copy.deepcopy(choice)
                bad["safety_flags"][key] = True
                validation = validate_operator_choice(bad)

            self.assertEqual(validation["status"], "fail")
            self.assertTrue(any(key in error for error in validation["errors"]), validation)

    def test_risky_modes_require_explicit_approval(self) -> None:
        cases = (
            ("router_port_forward", "router_port_forward_risky"),
            ("direct_public_ip", "direct_public_ip_risky"),
        )
        for mode, provider_class in cases:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                ops_path, plan_path = _write_inputs(tmp)
                choice = _choice(plan_path, ops_path, selected_exposure_mode=mode, provider_class=provider_class)
                approved = _choice(
                    plan_path,
                    ops_path,
                    selected_exposure_mode=mode,
                    provider_class=provider_class,
                    approve_risky_mode=True,
                )
                validation = validate_operator_choice(choice)
                approved_validation = validate_operator_choice(approved)

            self.assertEqual(validation["status"], "fail")
            self.assertTrue(any("requires explicit risky-mode approval" in error for error in validation["errors"]))
            self.assertEqual(approved_validation["status"], "pass")

    def test_missing_rollback_or_route_denylist_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            choice = _choice(plan_path, ops_path)
            missing_rollback = copy.deepcopy(choice)
            missing_rollback["rollback_steps"] = []
            missing_routes = copy.deepcopy(choice)
            missing_routes["route_denylist"] = []

        rollback_validation = validate_operator_choice(missing_rollback)
        routes_validation = validate_operator_choice(missing_routes)
        self.assertEqual(rollback_validation["status"], "fail")
        self.assertIn("rollback steps are missing", rollback_validation["errors"])
        self.assertEqual(routes_validation["status"], "fail")
        self.assertTrue(any("route denylist missing" in error for error in routes_validation["errors"]))

    def test_public_exposure_or_tunnel_started_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            choice = _choice(plan_path, ops_path)
            public = copy.deepcopy(choice)
            public["public_exposure_enabled"] = True
            started = copy.deepcopy(choice)
            started["tunnel_started"] = True

        for bad in (public, started):
            validation = validate_operator_choice(bad)
            self.assertEqual(validation["status"], "fail")

    def test_remote_ahead_status_requires_remote_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            choice = _choice(plan_path, ops_path, remote_ahead=1, remote_behind=0)
            validation = validate_operator_choice(choice)

        self.assertTrue(choice["remote_sync_required"])
        self.assertEqual(validation["choice_status"], "BLOCKED_ON_REMOTE_SYNC")
        self.assertEqual(validation["recommended_next_task"], "REMOTE-SYNC-BEFORE-PUBLIC-EXPOSURE-00")

    def test_cli_choose_validate_status_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            out = Path(tmp) / "choice"
            choose = _run_exposure_main(
                "choose",
                "--plan",
                str(plan_path),
                "--ops-posture",
                str(ops_path),
                "--mode",
                "reverse_tunnel",
                "--provider-class",
                "provider_managed_https_tunnel",
                "--provider-name",
                "OPERATOR_REQUIRED",
                "--public-url",
                "OPERATOR_REQUIRED",
                "--out",
                str(out),
            )
            choice_path = out / "operator_choice.json"
            report_path = out / "OPERATOR_CHOICE_REPORT.md"
            validate = _run_exposure_main("validate-choice", "--choice", str(choice_path), "--strict")
            status = _run_exposure_main("choice-status", "--choice", str(choice_path))
            report = _run_exposure_main("choice-report", "--choice", str(choice_path))
            choice_exists = choice_path.is_file()
            report_exists = report_path.is_file()
            payload = json.loads(choice_path.read_text(encoding="utf-8"))

        self.assertEqual(choose.code, 0, choose.stderr)
        self.assertTrue(choice_exists)
        self.assertTrue(report_exists)
        self.assertEqual(validate.code, 0, validate.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertEqual(report.code, 0, report.stderr)
        self.assertIn("BLOCKED_ON_OPERATOR_PROVIDER_URL", status.stdout)
        self.assertFalse(payload["public_exposure_enabled"])
        self.assertFalse(payload["tunnel_started"])

    def test_cli_validate_choice_fails_for_unsafe_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            out = Path(tmp) / "choice"
            _run_exposure_main("choose", "--plan", str(plan_path), "--ops-posture", str(ops_path), "--out", str(out))
            choice_path = out / "operator_choice.json"
            payload = json.loads(choice_path.read_text(encoding="utf-8"))
            payload["public_exposure_enabled"] = True
            choice_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            validation = _run_exposure_main("validate-choice", "--choice", str(choice_path))

        self.assertNotEqual(validation.code, 0)
        self.assertIn("public_exposure_enabled must remain false", validation.stderr)

    def test_write_operator_choice_outputs_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ops_path, plan_path = _write_inputs(tmp)
            out = Path(tmp) / "choice"
            choice_path = write_operator_choice(_choice(plan_path, ops_path), out)
            report_exists = (out / "OPERATOR_CHOICE_REPORT.md").is_file()

        self.assertEqual(choice_path.name, "operator_choice.json")
        self.assertTrue(report_exists)


def _ops() -> dict[str, object]:
    return build_default_plan(
        generated_at="2026-06-17T00:00:00Z",
        branch="dev",
        head="test-head",
        worktree_status="## dev...origin/dev",
    )


def _write_inputs(root: str | Path) -> tuple[Path, Path]:
    root_path = Path(root)
    ops_path = write_ops_plan(_ops(), root_path / "ops")
    plan = build_tunnel_plan(
        ops_posture=ops_path,
        out_dir=root_path / "exposure",
        exposure_mode="reverse_tunnel",
        generated_at="2026-06-17T00:00:00Z",
        branch="dev",
        head="test-head",
        worktree_status="## dev...origin/dev",
    )
    plan_path = write_tunnel_plan(plan, root_path / "exposure")
    return ops_path, plan_path


def _choice(
    plan_path: str | Path | None,
    ops_path: str | Path | None,
    **kwargs: object,
) -> dict[str, object]:
    values = {
        "exposure_plan": plan_path,
        "ops_posture": ops_path,
        "generated_at": "2026-06-17T00:00:00Z",
        "branch": "dev",
        "head": "test-head",
        "worktree_status": "## dev...origin/dev",
        "remote_ahead": 0,
        "remote_behind": 0,
    }
    values.update(kwargs)
    return build_operator_choice(**values)  # type: ignore[arg-type]


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
