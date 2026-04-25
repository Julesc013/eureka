import json
import unittest

from tests.hardening.helpers import repo_path, read_text


REQUIRED_LANES = {
    "fast",
    "standard",
    "full",
    "docs_only",
    "public_alpha",
    "parity",
    "audit",
    "hardening",
    "rust_optional",
}

KEY_COMMANDS = {
    "architecture_boundaries",
    "public_alpha_smoke",
    "python_oracle_golden_check",
    "archive_resolution_eval_runner",
    "search_usefulness_audit_runner",
    "hardening_tests",
}


def _load_json(relative_path):
    return json.loads(read_text(relative_path))


class AideTestRegistryConsistencyTest(unittest.TestCase):
    def test_aide_task_and_report_artifacts_exist(self):
        required = [
            ".aide/tasks/README.md",
            ".aide/tasks/queue.yaml",
            ".aide/tasks/audit_backlog.yaml",
            ".aide/reports/README.md",
        ]
        missing = [path for path in required if not repo_path(path).exists()]
        self.assertEqual(missing, [])

        queue = read_text(".aide/tasks/queue.yaml")
        backlog = read_text(".aide/tasks/audit_backlog.yaml")
        self.assertIn("hard_test_pack_v0", queue)
        self.assertIn("hard_test_pack_v0", backlog)

    def test_command_matrix_references_registered_commands(self):
        registry = _load_json("control/inventory/tests/test_registry.json")
        matrix = _load_json("control/inventory/tests/command_matrix.json")
        registered = {record["test_id"] for record in registry["records"]}

        unknown = []
        for lane in matrix["lanes"]:
            for command_id in lane["commands"]:
                if command_id not in registered:
                    unknown.append(f"{lane['lane_id']}::{command_id}")
        self.assertEqual(unknown, [])

    def test_required_lanes_and_key_commands_are_present(self):
        registry = _load_json("control/inventory/tests/test_registry.json")
        matrix = _load_json("control/inventory/tests/command_matrix.json")
        lanes = {lane["lane_id"]: lane for lane in matrix["lanes"]}
        registered = {record["test_id"] for record in registry["records"]}

        self.assertTrue(REQUIRED_LANES.issubset(lanes))
        self.assertTrue(KEY_COMMANDS.issubset(registered))
        self.assertEqual(lanes["rust_optional"]["required_status"], "optional")
        self.assertEqual(lanes["hardening"]["required_status"], "required")

    def test_aide_command_metadata_mentions_key_lanes(self):
        dev = read_text(".aide/commands/dev.yaml")
        ci = read_text(".aide/commands/ci.yaml")
        combined = dev + "\n" + ci

        for expected in [
            "hardening_tests",
            "public_alpha_smoke",
            "python_oracle_golden_check",
            "search_usefulness_audit",
        ]:
            self.assertIn(expected, combined)


if __name__ == "__main__":
    unittest.main()
