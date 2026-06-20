from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from runtime.local import portable_instance as portable_instance_module
from runtime.local.portable_instance import (
    PortableInstanceError,
    bootstrap_command,
    build_portable_paths,
    doctor_command,
    resolve_portable_instance_root,
    status_command,
)


class PortableEurekaInstanceRuntimeTests(unittest.TestCase):
    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dry run instance"
            result = bootstrap_command(instance=root, dry_run=True)
            self.assertEqual(result["status"], "pass")
            self.assertFalse(result["mutations_performed"])
            self.assertFalse(root.exists())

    def test_forbidden_repo_root_rejected(self) -> None:
        with self.assertRaises(PortableInstanceError):
            bootstrap_command(instance=Path(__file__).resolve().parents[2], dry_run=True)

    def test_resolution_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            explicit = Path(tmp) / "explicit"
            env_root = Path(tmp) / "env"
            self.assertEqual(resolve_portable_instance_root(explicit, env={"EUREKA_INSTANCE": str(env_root)}), explicit.resolve())
            self.assertEqual(resolve_portable_instance_root(None, env={"EUREKA_INSTANCE": str(env_root)}), env_root.resolve())

    def test_doctor_reports_missing_instance_with_remediation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "missing"
            result = doctor_command(instance=root, strict=True)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any(item["code"] == "bootstrap_required" for item in result["errors"]))
            self.assertFalse(result["mutations_performed"])

    def test_bootstrap_profile_and_status_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            result = bootstrap_command(instance=root, no_demo=True)
            self.assertEqual(result["status"], "pass")
            paths = build_portable_paths(root)
            self.assertTrue(paths.profile.is_file())
            profile = json.loads(paths.profile.read_text(encoding="utf-8"))
            self.assertFalse(profile["live_providers_enabled"])
            self.assertFalse(profile["public_exposure_enabled"])
            self.assertEqual(profile["paths"]["run_bundles"], "run/e2e-reference/runs")
            status = status_command(instance=root, include_paths=True)
            self.assertEqual(status["command"], "status")
            self.assertIn("backup", status)

    def test_stale_server_lock_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root, no_demo=True)
            paths = build_portable_paths(root)
            paths.server_lock.write_text('{"pid": 99999999, "created_at": "now"}\n', encoding="utf-8")
            result = doctor_command(instance=root)
            self.assertTrue(any(item["code"] == "stale_server_lock" for item in result["warnings"]))

    def test_windows_pid_probe_error_marks_lock_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root, no_demo=True)
            paths = build_portable_paths(root)
            paths.server_lock.write_text('{"pid": 38332, "created_at": "now"}\n', encoding="utf-8")
            with (
                mock.patch.object(portable_instance_module.os, "name", "nt"),
                mock.patch.object(portable_instance_module, "_pid_alive_windows", side_effect=SystemError("invalid pid probe")),
            ):
                result = doctor_command(instance=root)
            self.assertTrue(any(item["code"] == "stale_server_lock" for item in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
