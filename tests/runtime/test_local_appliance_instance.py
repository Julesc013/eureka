from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import (
    LocalInstancePathError,
    load_instance_config,
    load_instance_ref,
    load_migration_state,
    load_store_manifest,
    resolve_instance_paths,
)


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class LocalApplianceInstanceTests(unittest.TestCase):
    def test_resolve_instance_paths_requires_explicit_instance_path(self) -> None:
        with self.assertRaises(LocalInstancePathError):
            resolve_instance_paths("")

    def test_forbidden_roots_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LocalInstancePathError):
                resolve_instance_paths(Path(tmp) / ".cache" / "eureka-instance")
        with self.assertRaises(LocalInstancePathError):
            resolve_instance_paths(ROOT)

    def test_instance_ref_and_paths_load_from_initialized_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, init.returncode, init.stderr)
            ref = load_instance_ref(instance)
            paths = resolve_instance_paths(instance)
            manifest = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["instance_id"], ref.instance_id)
            self.assertEqual(1, ref.instance_schema_version)
            self.assertEqual(instance.resolve(), paths.instance_root)
            self.assertEqual(instance / "db" / "source_cache.sqlite", paths.source_cache_db)

    def test_config_manifest_and_migration_state_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, init.returncode, init.stderr)
            config = load_instance_config(instance)
            manifest = load_store_manifest(instance)
            migration = load_migration_state(instance)
            self.assertEqual(config.instance_id, manifest.instance_id)
            self.assertEqual(config.instance_id, migration.instance_id)
            self.assertEqual(["source_cache", "evidence_ledger", "review_queue", "public_index"], list(manifest.stores))
            self.assertFalse(migration.destructive_migration_required)


if __name__ == "__main__":
    unittest.main()
