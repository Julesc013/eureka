from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from surfaces.native.cli.main import main


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class LocalIndexCliTestCase(unittest.TestCase):
    def test_index_build_status_and_query_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            build_exit_code, build_output = run_cli("index-build", "--index-path", index_path)
            status_exit_code, status_output = run_cli("index-status", "--index-path", index_path)
            query_exit_code, query_output = run_cli("index-query", "synthetic", "--index-path", index_path)

        self.assertEqual(build_exit_code, 0)
        self.assertIn("Local index", build_output)
        self.assertEqual(status_exit_code, 0)
        self.assertIn("record_count:", status_output)
        self.assertEqual(query_exit_code, 0)
        self.assertIn("synthetic", query_output.casefold())

    def test_index_query_supports_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            run_cli("index-build", "--index-path", index_path)
            exit_code, output = run_cli(
                "index-query",
                "archive",
                "--index-path",
                index_path,
                "--json",
            )

        payload = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "queried")
        self.assertGreaterEqual(payload["result_count"], 1)

    def test_index_query_shows_synthetic_member_parent_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            run_cli("index-build", "--index-path", index_path)
            exit_code, output = run_cli(
                "index-query",
                "driver.inf",
                "--index-path",
                index_path,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("synthetic_member", output)
        self.assertIn("drivers/wifi/thinkpad_t42/windows2000/driver.inf", output)
        self.assertIn("parent_target_ref: local-bundle-fixture:driver-support-cd@1.0", output)
        self.assertIn("member_kind: driver", output)
        self.assertIn("lane: inside_bundles", output)
        self.assertIn("user_cost: 1", output)
        self.assertIn("compatibility: Windows 2000", output)
        self.assertIn("compatibility_evidence: Windows 2000", output)


if __name__ == "__main__":
    unittest.main()
