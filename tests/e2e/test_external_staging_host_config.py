from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

from runtime.local.external_staging_mvp import (
    CONFIG_SCHEMA_VERSION,
    LOCAL_CONFIG_EXAMPLE_JSON,
    LOCAL_CONFIG_JSON,
    deploy_from_plan,
    smoke_from_plan,
)
from tests.e2e.test_external_staging_host_provision import (
    _ExternalStagingDemo,
    _fake_probe,
    _fake_transfer,
    _load_json,
    _run_external_main,
    _run_launch_gate,
    _write_json,
    _write_rehearsal,
)


class ExternalStagingHostConfigTests(unittest.TestCase):
    def test_init_config_writes_redacted_template(self) -> None:
        with _ExternalStagingDemo() as demo:
            target = demo.external_path / LOCAL_CONFIG_EXAMPLE_JSON
            result = _run_external_main("init-config", "--out", str(target))
            payload = _load_json(target)
            body = target.read_text(encoding="utf-8")

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(payload["config_schema_version"], CONFIG_SCHEMA_VERSION)
        self.assertEqual(payload["bind_host"], "127.0.0.1")
        self.assertFalse(payload["workbench_enabled"])
        self.assertFalse(payload["live_metadata_enabled"])
        self.assertNotIn("PRIVATE KEY", body)

    def test_validate_config_reports_missing_config_without_secret_output(self) -> None:
        with _ExternalStagingDemo() as demo:
            result = _run_external_main("validate-config", "--config", str(demo.config_path))
            status = _run_external_main("config-status", "--config", str(demo.config_path))

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(status.code, 0, status.stderr)
        self.assertIn("status: missing_config", status.stdout)
        self.assertNotIn("PRIVATE KEY", status.stdout)
        self.assertNotIn("token=", status.stdout)

    def test_validate_config_passes_for_valid_temp_config(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_config(demo.config_path)
            result = _run_external_main("validate-config", "--config", str(demo.config_path))
            status = _run_external_main("config-status", "--config", str(demo.config_path))

        self.assertEqual(result.code, 0, result.stderr)
        self.assertIn("status: pass", status.stdout)
        self.assertIn("host_configured: true", status.stdout)
        self.assertNotIn("staging.example.invalid", status.stdout)

    def test_validate_config_rejects_unsafe_flags(self) -> None:
        cases = (
            ("workbench_enabled", True, "workbench_enabled must be false"),
            ("live_metadata_enabled", True, "live_metadata_enabled must be false"),
            ("mutation_enabled", True, "mutation_enabled must be false"),
            ("downloads_enabled", True, "downloads_enabled must be false"),
            ("public_live_fanout", True, "public_live_fanout must be false"),
        )
        for key, value, expected in cases:
            with self.subTest(key=key), _ExternalStagingDemo() as demo:
                config = _valid_config()
                config[key] = value
                _write_json(demo.config_path, config)
                result = _run_external_main("validate-config", "--config", str(demo.config_path))

                self.assertEqual(result.code, 1)
                self.assertIn(expected, result.stderr)

    def test_validate_config_rejects_exposure_and_required_ssh_field_gaps(self) -> None:
        with _ExternalStagingDemo() as demo:
            config = _valid_config()
            config["bind_host"] = "0.0.0.0"
            config["exposure_approved"] = False
            _write_json(demo.config_path, config)
            bind_result = _run_external_main("validate-config", "--config", str(demo.config_path))

        self.assertEqual(bind_result.code, 1)
        self.assertIn("non-loopback bind_host requires exposure_approved true", bind_result.stderr)

        with _ExternalStagingDemo() as demo:
            config = _valid_config()
            config["host"] = ""
            config["user"] = ""
            config["remote_dir"] = ""
            _write_json(demo.config_path, config)
            missing_result = _run_external_main("validate-config", "--config", str(demo.config_path))

        self.assertEqual(missing_result.code, 1)
        self.assertIn("host is required for ssh deployment mode", missing_result.stderr)
        self.assertIn("user is required for ssh deployment mode", missing_result.stderr)
        self.assertIn("remote_dir is required for ssh deployment mode", missing_result.stderr)

    def test_plan_consumes_local_config_and_environment_config(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_config(demo.config_path)
            local_result = _run_external_main("plan", "--bundle", str(demo.bundle_path), "--config", str(demo.config_path), "--out", str(demo.external_path))
            local_plan = _load_json(demo.plan_path)

        self.assertEqual(local_result.code, 0, local_result.stderr)
        self.assertEqual(local_plan["config_source"], "local_config")
        self.assertTrue(local_plan["host_configured"])

        with _ExternalStagingDemo() as demo:
            with _temporary_env(
                EUREKA_STAGING_HOST="staging.example.invalid",
                EUREKA_STAGING_USER="deploy",
                EUREKA_STAGING_REMOTE_DIR="/srv/eureka-public-alpha",
                EUREKA_STAGING_BASE_URL="http://127.0.0.1:8765",
            ):
                env_result = _run_external_main("plan", "--bundle", str(demo.bundle_path), "--out", str(demo.external_path))
            env_plan = _load_json(demo.plan_path)

        self.assertEqual(env_result.code, 0, env_result.stderr)
        self.assertEqual(env_plan["config_source"], "env")
        self.assertTrue(env_plan["remote_dir_configured"])

    def test_apply_requires_confirmation_and_mocked_transfer_preserves_safety(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_config(demo.config_path)
            _run_external_main("plan", "--bundle", str(demo.bundle_path), "--config", str(demo.config_path), "--out", str(demo.external_path))
            _run_external_main("package", "--bundle", str(demo.bundle_path), "--plan", str(demo.plan_path), "--out", str(demo.package_path))
            no_confirm = _run_external_main("deploy", "--plan", str(demo.plan_path), "--apply")
            no_confirm_report = _load_json(demo.report_path)
            report = deploy_from_plan(plan=demo.plan_path, apply=True, confirm_apply=True, transfer_runner=_fake_transfer)
            validate = _run_external_main("validate-report", "--report", str(demo.report_path))

        self.assertEqual(no_confirm.code, 1)
        self.assertEqual(no_confirm_report["deployment_status"], "confirmation_required")
        self.assertEqual(report["deployment_status"], "transfer_complete_manual_start_required")
        self.assertTrue(report["apply_confirmation"])
        self.assertFalse(report["safety_checks"]["workbench_exposed"])
        self.assertEqual(validate.code, 0, validate.stderr)

    def test_smoke_blocks_without_base_url_and_passes_with_mocked_public_routes(self) -> None:
        with _ExternalStagingDemo() as demo:
            config = _valid_config()
            config["base_url"] = ""
            _write_json(demo.config_path, config)
            _run_external_main("plan", "--bundle", str(demo.bundle_path), "--config", str(demo.config_path), "--out", str(demo.external_path))
            _run_external_main("deploy", "--plan", str(demo.plan_path), "--dry-run")
            blocked = _run_external_main("smoke", "--plan", str(demo.plan_path))
            blocked_report = _load_json(demo.report_path)

        self.assertEqual(blocked.code, 0, blocked.stderr)
        self.assertEqual(blocked_report["smoke_status"], "blocked")

        with _ExternalStagingDemo() as demo:
            _write_config(demo.config_path)
            _run_external_main("plan", "--bundle", str(demo.bundle_path), "--config", str(demo.config_path), "--out", str(demo.external_path))
            _run_external_main("package", "--bundle", str(demo.bundle_path), "--plan", str(demo.plan_path), "--out", str(demo.package_path))
            deploy_from_plan(plan=demo.plan_path, apply=True, confirm_apply=True, transfer_runner=_fake_transfer)
            passed = smoke_from_plan(plan=demo.plan_path, probe=_fake_probe)

        self.assertEqual(passed["smoke_status"], "pass")
        self.assertFalse(passed["safety_checks"]["live_metadata_enabled"])

    def test_validate_report_rejects_false_deployment_and_unsafe_claims(self) -> None:
        cases = (
            ({"deployment_status": "transfer_complete_manual_start_required", "host_configured": True, "apply_confirmation": False}, "without apply confirmation"),
            ({"deployment_status": "deployed", "host_configured": False, "apply_confirmation": True}, "deployed without host"),
            ({"smoke_status": "pass", "base_url_configured": False, "route_probe_results": [{"status_code": 200}]}, "smoke pass without base_url_configured"),
            ({"safety_checks": {"workbench_exposed": True}}, "workbench_exposed"),
            ({"safety_checks": {"live_metadata_enabled": True}}, "live_metadata_enabled"),
            ({"safety_checks": {"mutation_enabled": True}}, "mutation_enabled"),
            ({"binary_verified_count": 1}, "binary_verified_count"),
            ({"download_safe_count": 1}, "download_safe_count"),
            ({"execution_safe_count": 1}, "execution_safe_count"),
            ({"rights_cleared_count": 1}, "rights_cleared_count"),
        )
        for patch, expected in cases:
            with self.subTest(expected=expected), _ExternalStagingDemo() as demo:
                _run_external_main("plan", "--bundle", str(demo.bundle_path), "--out", str(demo.external_path))
                _run_external_main("deploy", "--plan", str(demo.plan_path), "--dry-run")
                report = _load_json(demo.report_path)
                _deep_update(report, patch)
                _write_json(demo.report_path, report)
                result = _run_external_main("validate-report", "--report", str(demo.report_path))

                self.assertEqual(result.code, 1)
                self.assertIn(expected, result.stderr)

    def test_launch_gate_consumes_config_report_without_clearing_other_launch_blockers(self) -> None:
        with _ExternalStagingDemo() as demo:
            _write_config(demo.config_path)
            _run_external_main("plan", "--bundle", str(demo.bundle_path), "--config", str(demo.config_path), "--out", str(demo.external_path))
            _run_external_main("package", "--bundle", str(demo.bundle_path), "--plan", str(demo.plan_path), "--out", str(demo.package_path))
            deploy_from_plan(plan=demo.plan_path, apply=True, confirm_apply=True, transfer_runner=_fake_transfer)
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


def _valid_config() -> dict[str, object]:
    return {
        "config_schema_version": CONFIG_SCHEMA_VERSION,
        "host": "staging.example.invalid",
        "user": "deploy",
        "ssh_port": 22,
        "ssh_key_path": "",
        "remote_dir": "/srv/eureka-public-alpha",
        "base_url": "http://127.0.0.1:8765",
        "service_port": 8765,
        "bind_host": "127.0.0.1",
        "exposure_approved": False,
        "deployment_mode": "ssh",
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "workbench_enabled": False,
        "public_live_fanout": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
    }


def _write_config(path: Path) -> None:
    _write_json(path, _valid_config())


def _temporary_env(**updates: str):
    return _TemporaryEnv(updates)


class _TemporaryEnv:
    def __init__(self, updates: dict[str, str]) -> None:
        self.updates = updates
        self.previous: dict[str, str | None] = {}

    def __enter__(self) -> None:
        for key, value in self.updates.items():
            self.previous[key] = os.environ.get(key)
            os.environ[key] = value

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        for key, value in self.previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _deep_update(target: dict[str, object], patch: dict[str, object]) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)  # type: ignore[arg-type,index]
        else:
            target[key] = value


if __name__ == "__main__":
    unittest.main()
