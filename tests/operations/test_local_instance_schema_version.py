from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
VALIDATE = ROOT / "scripts" / "eureka_validate_instance.py"
MIGRATION_STATUS = ROOT / "scripts" / "eureka_instance_migration_status.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class LocalInstanceSchemaVersionTests(unittest.TestCase):
    def test_schema_policy_is_fail_closed(self) -> None:
        payload = load_json("control/policies/local_instance_schema_policy.json")
        self.assertEqual(1, payload["current_instance_schema_version"])
        self.assertEqual(1, payload["minimum_supported_instance_schema_version"])
        self.assertEqual("fail_closed", payload["unsupported_version_behavior"])
        self.assertIs(payload["silent_upgrade_allowed"], False)
        self.assertIs(payload["destructive_migration_allowed"], False)

    def test_migration_policy_is_check_only(self) -> None:
        payload = load_json("control/policies/local_instance_migration_policy.json")
        self.assertEqual("check_only", payload["migration_default_mode"])
        self.assertIs(payload["apply_requires_explicit_flag"], True)
        self.assertIs(payload["destructive_migrations_enabled"], False)
        self.assertIs(payload["rollback_metadata_required"], True)
        self.assertIs(payload["backup_metadata_required"], True)

    def test_schema_version_inventory(self) -> None:
        payload = load_json("control/inventory/local_instance_schema_version.json")
        self.assertEqual(1, payload["current_instance_schema_version"])
        self.assertEqual(1, payload["minimum_supported_instance_schema_version"])
        self.assertEqual("fail_closed", payload["unsupported_version_behavior"])

    def test_config_schema_inventory_lists_required_fields(self) -> None:
        payload = load_json("control/inventory/local_instance_config_schema.json")
        for field in (
            "schema_version",
            "instance_id",
            "instance_schema_version",
            "created_at",
            "updated_at",
            "stores",
            "policies",
            "warnings",
            "limitations",
        ):
            self.assertIn(field, payload["fields"])
        self.assertIs(payload["invariants"]["server_enabled"], False)
        self.assertIs(payload["invariants"]["lan_enabled"], False)

    def test_store_manifest_schema_inventory_lists_required_stores(self) -> None:
        payload = load_json("control/inventory/local_instance_store_manifest_schema.json")
        for store in ("source_cache", "evidence_ledger", "review_queue", "public_index"):
            self.assertIn(store, payload["required_store_entries"])

    def test_migration_state_schema_inventory_forbids_destructive_migration(self) -> None:
        payload = load_json("control/inventory/local_instance_migration_state_schema.json")
        self.assertIn("migration_needed", payload["fields"])
        self.assertIs(payload["invariants"]["destructive_migration_required"], False)

    def test_unsupported_version_fails_closed(self) -> None:
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
            validate = run_cmd(str(VALIDATE), "--instance", str(instance), "--json")
            self.assertNotEqual(0, validate.returncode)
            status = run_cmd(str(MIGRATION_STATUS), "--instance", str(instance), "--json")
            self.assertEqual(0, status.returncode)
            self.assertTrue(json.loads(status.stdout)["migration_needed"])

    def test_next_task_is_local_03(self) -> None:
        payload = load_json("control/inventory/local_02_next_task_decision.json")
        self.assertIn("LOCAL-03", payload["recommended_next_task"])
        self.assertEqual("deferred", payload["f0_current_status"])
        self.assertIs(payload["server_can_start"], False)
        self.assertIs(payload["lan_can_start"], False)


if __name__ == "__main__":
    unittest.main()
