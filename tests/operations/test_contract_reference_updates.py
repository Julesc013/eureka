import json
import tempfile
import unittest
from pathlib import Path

from scripts import update_contract_schema_references as updater


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class ContractReferenceUpdateTests(unittest.TestCase):
    def make_repo(self) -> tempfile.TemporaryDirectory:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        write_json(root / "control/inventory/r0_03b_1_migration_result.json", {"task": "R0-03B-1"})
        write_json(root / "control/inventory/contract_reference_graph.json", {"schema_version": "contract_reference_graph.v0", "edges": []})
        write_json(root / "control/inventory/r0_03b_1_compatibility_shim_report.json", {"shims": []})
        write_json(
            root / "control/inventory/contract_migration_plan.json",
            {
                "moves": [
                    {
                        "source_path": "contracts/audits/demo_next_task.v0.json",
                        "target_path": "contracts/schema/control/tasks/audits/demo_next_task.v0.json",
                        "contract_class_before": "task_queue_schema",
                        "rationale": "fixture move",
                        "references_to_update": [
                            "scripts/validate_demo.py",
                            "control/audits/history/demo_report.json",
                        ],
                    }
                ]
            },
        )
        (root / "contracts/audits").mkdir(parents=True)
        (root / "contracts/audits/demo_next_task.v0.json").write_text("{}", encoding="utf-8")
        (root / "scripts").mkdir()
        (root / "scripts/validate_demo.py").write_text(
            'SCHEMA = "contracts/audits/demo_next_task.v0.json"\n',
            encoding="utf-8",
        )
        (root / "control/audits/history").mkdir(parents=True)
        (root / "control/audits/history/demo_report.json").write_text(
            '{"schema":"contracts/audits/demo_next_task.v0.json"}',
            encoding="utf-8",
        )
        return temp

    def test_reference_updater_defaults_to_dry_run(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            result = updater.update_references(
                root,
                json.loads((root / "control/inventory/r0_03b_1_migration_result.json").read_text()),
                json.loads((root / "control/inventory/contract_reference_graph.json").read_text()),
                json.loads((root / "control/inventory/contract_migration_plan.json").read_text()),
                json.loads((root / "control/inventory/r0_03b_1_compatibility_shim_report.json").read_text()),
                apply_changes=False,
            )["reference_update_result"]
            self.assertEqual(result["mode"], "dry_run")
            self.assertEqual(result["updates_completed"], 0)
            self.assertTrue((root / "contracts/audits/demo_next_task.v0.json").exists())

    def test_reference_updater_refuses_missing_migration_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            code = updater.main(["--repo-root", temp, "--migration-result", "missing.json", "--json"])
            self.assertEqual(code, 1)

    def test_reference_updater_updates_allowed_active_reference_fixture(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            result = updater.update_references(
                root,
                json.loads((root / "control/inventory/r0_03b_1_migration_result.json").read_text()),
                json.loads((root / "control/inventory/contract_reference_graph.json").read_text()),
                json.loads((root / "control/inventory/contract_migration_plan.json").read_text()),
                json.loads((root / "control/inventory/r0_03b_1_compatibility_shim_report.json").read_text()),
                apply_changes=True,
            )["reference_update_result"]
            self.assertGreaterEqual(result["updates_completed"], 1)
            self.assertFalse((root / "contracts/audits/demo_next_task.v0.json").exists())
            self.assertTrue((root / "contracts/schema/control/tasks/audits/demo_next_task.v0.json").exists())
            self.assertIn("contracts/schema/control/tasks/audits/demo_next_task.v0.json", (root / "scripts/validate_demo.py").read_text())

    def test_reference_updater_leaves_historical_audit_narrative_fixture_intact(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            result = updater.update_references(
                root,
                json.loads((root / "control/inventory/r0_03b_1_migration_result.json").read_text()),
                json.loads((root / "control/inventory/contract_reference_graph.json").read_text()),
                json.loads((root / "control/inventory/contract_migration_plan.json").read_text()),
                json.loads((root / "control/inventory/r0_03b_1_compatibility_shim_report.json").read_text()),
                apply_changes=True,
            )["reference_update_result"]
            self.assertEqual(len(result["historical_references_left_intact"]), 1)
            self.assertIn("contracts/audits/demo_next_task.v0.json", (root / "control/audits/history/demo_report.json").read_text())

    def test_reference_updater_refuses_forbidden_output_roots(self) -> None:
        with self.make_repo() as temp:
            code = updater.main(["--repo-root", temp, "--output", "runtime/out.json", "--json"])
            self.assertEqual(code, 1)

    def test_f0_and_dev_to_main_remain_blocked(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            result = updater.update_references(
                root,
                json.loads((root / "control/inventory/r0_03b_1_migration_result.json").read_text()),
                json.loads((root / "control/inventory/contract_reference_graph.json").read_text()),
                json.loads((root / "control/inventory/contract_migration_plan.json").read_text()),
                json.loads((root / "control/inventory/r0_03b_1_compatibility_shim_report.json").read_text()),
                apply_changes=False,
            )["reference_update_result"]
            self.assertTrue(result["f0_should_remain_blocked"])
            self.assertTrue(result["dev_to_main_should_remain_blocked"])


if __name__ == "__main__":
    unittest.main()
