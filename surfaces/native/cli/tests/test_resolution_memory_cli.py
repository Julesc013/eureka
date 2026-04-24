from __future__ import annotations

import json
from io import StringIO
import tempfile
import unittest

from surfaces.native.cli.main import main


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class ResolutionMemoryCliTestCase(unittest.TestCase):
    def test_memory_create_read_and_list_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_exit_code, _ = run_cli(
                "run-resolve",
                KNOWN_TARGET_REF,
                "--run-store-root",
                temp_dir,
            )
            create_exit_code, create_output = run_cli(
                "memory-create",
                "--run-store-root",
                temp_dir,
                "--memory-store-root",
                temp_dir,
                "--run-id",
                "run-exact-resolution-0001",
            )
            read_exit_code, read_output = run_cli(
                "memory",
                "memory-successful-resolution-0001",
                "--memory-store-root",
                temp_dir,
            )
            list_exit_code, list_output = run_cli(
                "memories",
                "--memory-store-root",
                temp_dir,
            )

        self.assertEqual(resolve_exit_code, 0)
        self.assertEqual(create_exit_code, 0)
        self.assertEqual(read_exit_code, 0)
        self.assertEqual(list_exit_code, 0)
        self.assertIn("Resolution memory", create_output)
        self.assertIn("memory-successful-resolution-0001", read_output)
        self.assertIn("successful_resolution", read_output)
        self.assertIn("memory-successful-resolution-0001", list_output)

    def test_memory_create_supports_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_cli(
                "run-planned-search",
                "latest Firefox before XP support ended",
                "--run-store-root",
                temp_dir,
            )
            exit_code, output = run_cli(
                "memory-create",
                "--run-store-root",
                temp_dir,
                "--memory-store-root",
                temp_dir,
                "--run-id",
                "run-planned-search-0001",
                "--json",
            )

        payload = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "available")
        self.assertEqual(payload["selected_memory_id"], "memory-absence-finding-0001")
        self.assertEqual(payload["memories"][0]["memory_kind"], "absence_finding")


if __name__ == "__main__":
    unittest.main()
