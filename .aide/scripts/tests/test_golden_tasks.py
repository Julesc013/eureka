from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / ".aide/scripts/aide_lite.py"
SPEC = importlib.util.spec_from_file_location("aide_lite", MODULE_PATH)
aide_lite = importlib.util.module_from_spec(SPEC)
sys.modules["aide_lite"] = aide_lite
assert SPEC.loader is not None
SPEC.loader.exec_module(aide_lite)


class GoldenTaskTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        aide_lite._write_minimal_repo(root)
        aide_lite.run_context(root)
        aide_lite.write_task_packet(root, "EUREKA-AIDE-GOLDEN-01 Add Eureka-specific AIDE golden tasks")
        aide_lite.adapt_agents(root)
        report = aide_lite.build_verification_report(root, task_packet_path=aide_lite.LATEST_PACKET_PATH)
        aide_lite.write_verification_report(root, aide_lite.LATEST_VERIFICATION_REPORT_PATH, report)
        aide_lite.write_review_packet(root)
        records = aide_lite.build_ledger_scan_records(root)
        aide_lite.write_ledger_records(root, records)
        aide_lite.write_token_savings_summary(root, records, [])
        return root

    def test_catalog_loading(self) -> None:
        root = self.make_repo()
        tasks = aide_lite.parse_golden_task_catalog(root)
        self.assertGreaterEqual(len(tasks), len(aide_lite.REQUIRED_GOLDEN_TASK_IDS))
        self.assertEqual([task.task_id for task in tasks], sorted(task.task_id for task in tasks))
        self.assertIn("compact-task-packet-required-sections", {task.task_id for task in tasks})
        for task_id in [
            "repo_boundary_golden",
            "compact_task_packet_golden",
            "evidence_review_packet_golden",
            "no_secret_or_local_state_golden",
            "eureka_architecture_context_golden",
            "generated_agent_guidance_golden",
            "commit_message_standard_golden",
            "task_resumption_standard_golden",
        ]:
            self.assertIn(task_id, {task.task_id for task in tasks})

    def test_eval_list_command(self) -> None:
        root = self.make_repo()
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = aide_lite.main(["--repo-root", str(root), "eval", "list"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("task_count:", output)
        self.assertIn("token-ledger-budget-check", output)

    def test_run_one_golden_task(self) -> None:
        root = self.make_repo()
        result = aide_lite.run_golden_task(root, "compact-task-packet-required-sections")
        self.assertEqual(result.result, "PASS")
        self.assertGreater(result.checks_run, 0)
        self.assertEqual(result.errors, ())

    def test_run_all_writes_json_and_markdown_reports(self) -> None:
        root = self.make_repo()
        run = aide_lite.run_golden_tasks(root)
        self.assertEqual(run.result, "PASS")
        json_result, md_result = aide_lite.write_golden_run_reports(root, run)
        self.assertIn(json_result.action, {"written", "unchanged"})
        self.assertIn(md_result.action, {"written", "unchanged"})
        data = json.loads(aide_lite.read_text(root / aide_lite.GOLDEN_RUN_JSON_PATH))
        self.assertEqual(data["schema_version"], "aide.golden-tasks-run.v0")
        self.assertEqual(data["result"], "PASS")
        self.assertEqual(data["task_count"], len(aide_lite.REQUIRED_GOLDEN_TASK_IDS))
        markdown = aide_lite.read_text(root / aide_lite.GOLDEN_RUN_MD_PATH)
        self.assertIn("# Latest Golden Tasks", markdown)
        self.assertIn("Token reduction remains valid only if golden tasks pass.", markdown)
        self.assertIn("repo_boundary_golden", markdown)

    def test_eureka_specific_golden_tasks_pass(self) -> None:
        root = self.make_repo()
        for task_id in [
            "repo_boundary_golden",
            "compact_task_packet_golden",
            "evidence_review_packet_golden",
            "no_secret_or_local_state_golden",
            "eureka_architecture_context_golden",
            "generated_agent_guidance_golden",
            "commit_message_standard_golden",
            "task_resumption_standard_golden",
        ]:
            with self.subTest(task_id=task_id):
                result = aide_lite.run_golden_task(root, task_id)
                self.assertEqual(result.result, "PASS", result)
                self.assertGreater(result.checks_run, 0)
                self.assertEqual(result.errors, ())

    def test_commit_message_check_command(self) -> None:
        root = self.make_repo()
        message_path = root / "COMMIT_EDITMSG"
        aide_lite.write_text(message_path, aide_lite.COMMIT_GOOD_EXAMPLE)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = aide_lite.main(
                [
                    "--repo-root",
                    str(root),
                    "commit",
                    "check",
                    "--message-file",
                    "COMMIT_EDITMSG",
                ]
            )
        self.assertEqual(code, 0, buffer.getvalue())
        self.assertIn("result: PASS", buffer.getvalue())

    def test_commit_message_check_rejects_vague_subject(self) -> None:
        root = self.make_repo()
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = aide_lite.main(
                [
                    "--repo-root",
                    str(root),
                    "commit",
                    "check",
                    "--message",
                    "update\n",
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("result: FAIL", buffer.getvalue())

    def test_commit_message_range_check_reports_history(self) -> None:
        root = self.make_repo()
        subprocess = __import__("subprocess")
        subprocess.run(["git", "init"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        subprocess.run(["git", "config", "user.name", "AIDE Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "aide@example.test"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", aide_lite.COMMIT_GOOD_EXAMPLE], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = aide_lite.main(["--repo-root", str(root), "commit", "check", "--range", "HEAD", "--max-count", "1"])
        self.assertEqual(code, 0, buffer.getvalue())
        self.assertIn("commit_count: 1", buffer.getvalue())

    def test_fail_result_rendering_from_bad_packet_fixture(self) -> None:
        root = self.make_repo()
        aide_lite.write_text(root / aide_lite.LATEST_PACKET_PATH, "# Broken\n")
        result = aide_lite.run_golden_task(root, "compact-task-packet-required-sections")
        self.assertEqual(result.result, "FAIL")
        self.assertTrue(result.errors)

    def test_eval_command_returns_nonzero_on_fail(self) -> None:
        root = self.make_repo()
        aide_lite.write_text(root / aide_lite.LATEST_PACKET_PATH, "# Broken\n")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = aide_lite.main(
                [
                    "--repo-root",
                    str(root),
                    "eval",
                    "run",
                    "--task",
                    "compact-task-packet-required-sections",
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("result: FAIL", buffer.getvalue())

    def test_reports_are_deterministic_and_metadata_only(self) -> None:
        root = self.make_repo()
        run = aide_lite.run_golden_tasks(root)
        aide_lite.write_golden_run_reports(root, run)
        first_json = aide_lite.read_text(root / aide_lite.GOLDEN_RUN_JSON_PATH)
        first_md = aide_lite.read_text(root / aide_lite.GOLDEN_RUN_MD_PATH)
        aide_lite.write_golden_run_reports(root, aide_lite.run_golden_tasks(root))
        self.assertEqual(first_json, aide_lite.read_text(root / aide_lite.GOLDEN_RUN_JSON_PATH))
        self.assertEqual(first_md, aide_lite.read_text(root / aide_lite.GOLDEN_RUN_MD_PATH))
        data = json.loads(first_json)
        self.assertFalse(data["raw_prompt_storage"])
        self.assertFalse(data["raw_response_storage"])
        self.assertNotIn("raw_prompt_body", first_json)
        self.assertNotIn("raw_response_body", first_json)
        self.assertNotIn("print('hello')", first_md)

    def test_eval_report_command_reads_latest_report(self) -> None:
        root = self.make_repo()
        aide_lite.write_golden_run_reports(root, aide_lite.run_golden_tasks(root))
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = aide_lite.main(["--repo-root", str(root), "eval", "report"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("result: PASS", output)
        self.assertIn(aide_lite.GOLDEN_RUN_JSON_PATH, output)

    def test_selftest_includes_eval_checks(self) -> None:
        ok, messages = aide_lite.run_selftest()
        self.assertTrue(ok)
        self.assertTrue(any("eval" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
