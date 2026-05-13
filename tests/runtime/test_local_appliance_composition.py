from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import (
    LocalApplianceError,
    LocalReadOnlyStoreMutationError,
    close_local_appliance,
    open_local_appliance,
)


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class LocalApplianceCompositionTests(unittest.TestCase):
    def test_open_local_appliance_requires_explicit_instance_path(self) -> None:
        with self.assertRaises(LocalApplianceError):
            open_local_appliance("")

    def test_temp_instance_opens_all_four_stores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, init.returncode, init.stderr)
            runtime = open_local_appliance(instance)
            try:
                self.assertIsNotNone(runtime.source_cache)
                self.assertIsNotNone(runtime.evidence_ledger)
                self.assertIsNotNone(runtime.review_queue)
                self.assertIsNotNone(runtime.public_index)
                self.assertEqual("pass", runtime.check_integrity()["status"])
            finally:
                close_local_appliance(runtime)

    def test_status_reports_disabled_runtime_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                status = runtime.status().to_dict()
                self.assertEqual("pass", status["status"])
                self.assertIs(status["server_enabled"], False)
                self.assertIs(status["lan_enabled"], False)
                self.assertIs(status["deployment_performed"], False)
                self.assertIs(status["production_readiness_claimed"], False)
                self.assertIs(status["public_launch_readiness_claimed"], False)
            finally:
                runtime.close()

    def test_close_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            runtime.close()
            runtime.close()

    def test_read_only_mode_reports_and_blocks_mutation_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                self.assertIs(runtime.status().to_dict()["read_only"], True)
                with self.assertRaises(LocalReadOnlyStoreMutationError):
                    runtime.source_cache.init
            finally:
                runtime.close()

    def test_unsupported_schema_version_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            manifest_path = instance / "config" / "instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["instance_schema_version"] = 999
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            state_path = instance / "config" / "migration_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["current_instance_schema_version"] = 999
            state["migration_needed"] = True
            state["blockers"] = ["unsupported instance_schema_version 999"]
            state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaises(LocalApplianceError):
                open_local_appliance(instance)


if __name__ == "__main__":
    unittest.main()
