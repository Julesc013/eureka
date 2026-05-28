from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import scripts.eureka_gate as gate_tool


class EurekaGateTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_complete_gate_artifacts(self, out_dir: Path, *, status: str = "pass") -> None:
        summary = {
            "schema_version": "full_unittest_summary.v0",
            "command": "python -m unittest discover -s tests -t .",
            "status": status,
            "exit_code": 0 if status == "pass" else 1,
            "duration_seconds": 42.5,
            "counts": {
                "tests_run": 5,
                "failures": 0 if status == "pass" else 1,
                "errors": 0,
                "skipped": 0,
            },
            "git": {
                "branch": "dev",
                "head": "abc123",
                "working_tree_clean": True,
            },
        }
        self.write_json(out_dir / "full_unittest_summary.json", summary)
        self.write_json(
            out_dir / "failure_families.json",
            {
                "schema_version": "failure_family_list.v0",
                "failure_families": [
                    {
                        "family_id": "unittest-example",
                        "exception_type": "AssertionError",
                        "representative_test": "tests.example.TestCase.test_fail",
                        "normalized_message": "example failure",
                        "failed_tests": ["tests.example.TestCase.test_fail"],
                    }
                ]
                if status != "pass"
                else [],
            },
        )
        (out_dir / "failed_tests.txt").write_text(
            "tests.example.TestCase.test_fail\n" if status != "pass" else "",
            encoding="utf-8",
        )
        self.write_json(
            out_dir / "status.json",
            {
                "schema_version": "full_discovery_status.v0",
                "run_id": "public_alpha_readonly_closeout",
                "status": status,
                "pid": None,
                "command": "python -m unittest discover -s tests -t .",
                "elapsed_seconds": 42.5,
                "stdout_path": str(out_dir / "full_unittest_stdout.txt"),
                "stderr_path": str(out_dir / "full_unittest_stderr.txt"),
                "stdout_bytes": 123,
                "stderr_bytes": 0,
                "exit_code": 0 if status == "pass" else 1,
                "summary_path": str(out_dir / "full_unittest_summary.json"),
                "failure_families_path": str(out_dir / "failure_families.json"),
                "failed_tests_path": str(out_dir / "failed_tests.txt"),
            },
        )

    def test_supported_hyphen_gates_and_legacy_aliases_resolve(self) -> None:
        self.assertEqual("public-alpha-closeout", gate_tool.resolve_gate("public-alpha-closeout").name)
        self.assertEqual("public-alpha-closeout", gate_tool.resolve_gate("public_alpha_readonly_closeout").name)
        self.assertEqual("source-snapshot-closeout", gate_tool.resolve_gate("source_snapshot_closeout").name)
        self.assertEqual("promotion-gate", gate_tool.resolve_gate("promotion_gate").name)

    def test_json_status_reports_missing_gate_without_running_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()

            exit_code = gate_tool.main(
                ["public-alpha-closeout", "--out", str(Path(tmp) / "missing"), "--status", "--json"],
                stdout=stdout,
            )

            self.assertEqual(0, exit_code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("eureka_gate_status.v0", payload["schema_version"])
            self.assertEqual("public-alpha-closeout", payload["gate"])
            self.assertEqual("missing", payload["status"])
            self.assertIn("python scripts/eureka_gate.py public-alpha-closeout --watch", payload["watch_command"])

    def test_handoff_writes_json_markdown_and_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            stdout = io.StringIO()

            exit_code = gate_tool.main(
                ["public-alpha-closeout", "--out", str(out_dir), "--handoff", "--json"],
                stdout=stdout,
            )

            self.assertEqual(0, exit_code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("eureka_ai_handoff.v0", payload["schema_version"])
            self.assertEqual("public-alpha-closeout", payload["gate"])
            self.assertTrue(payload["safe_to_continue"])
            self.assertEqual("DEV-TO-MAIN-PROMOTION-REVIEW-04", payload["recommended_next_task"])
            self.assertTrue((out_dir / "ai_handoff.json").is_file())
            self.assertTrue((out_dir / "ai_handoff.md").is_file())
            self.assertTrue((out_dir / "ai_handoff.zip").is_file())
            text = (out_dir / "ai_handoff.md").read_text(encoding="utf-8")
            self.assertIn("STATUS: PASS", text)
            self.assertIn("COMPACT_HANDOFF_JSON", text)
            self.assertNotIn("full_unittest_stdout.txt", text)
            self.assertNotIn("full_unittest_stderr.txt", text)
            with zipfile.ZipFile(out_dir / "ai_handoff.zip") as archive:
                self.assertEqual({"ai_handoff.json", "ai_handoff.md"}, set(archive.namelist()))

    def test_copy_and_open_apply_to_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with patch.object(gate_tool, "copy_to_clipboard") as copy_to_clipboard, patch.object(gate_tool, "open_path") as open_path:
                exit_code = gate_tool.main(
                    ["public-alpha-closeout", "--out", str(out_dir), "--handoff", "--copy", "--open"],
                    stdout=stdout,
                    stderr=stderr,
                )

            self.assertEqual(0, exit_code)
            copy_to_clipboard.assert_called_once()
            open_path.assert_called_once()
            self.assertIn("PASTE_TO_AI", stdout.getvalue())

    def test_background_prints_new_gate_followup_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            stdout = io.StringIO()
            metadata = {
                "schema_version": "full_discovery_start.v0",
                "run_id": "public_alpha_readonly_closeout",
                "pid": 4321,
                "out_dir": str(out_dir),
                "status_path": str(out_dir / "status.json"),
                "summary_path": str(out_dir / "full_unittest_summary.json"),
                "failure_families_path": str(out_dir / "failure_families.json"),
                "failed_tests_path": str(out_dir / "failed_tests.txt"),
                "harness_stdout_path": str(out_dir / "harness_stdout.txt"),
                "harness_stderr_path": str(out_dir / "harness_stderr.txt"),
                "command": ["python", "scripts/run_full_unittest_discovery.py"],
            }

            with patch.object(gate_tool, "start_discovery", return_value=metadata) as start_discovery:
                exit_code = gate_tool.main(
                    [
                        "public-alpha-closeout",
                        "--out",
                        str(out_dir),
                        "--background",
                        "--heartbeat-seconds",
                        "1",
                    ],
                    stdout=stdout,
                )

            self.assertEqual(0, exit_code)
            start_discovery.assert_called_once()
            self.assertIn("Eureka Gate: public-alpha-closeout", stdout.getvalue())
            self.assertIn("PID: 4321", stdout.getvalue())
            self.assertIn("python scripts/eureka_gate.py public-alpha-closeout --handoff", stdout.getvalue())

    def test_commit_handoff_writes_only_compact_repo_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            payload = gate_tool.load_status(out_dir)
            handoff_paths = gate_tool.write_ai_handoff_bundle(
                gate=gate_tool.resolve_gate("public-alpha-closeout"),
                out_dir=out_dir,
                status_payload=payload,
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            changed = gate_tool.commit_handoff_bundle(
                gate=gate_tool.resolve_gate("public-alpha-closeout"),
                out_dir=out_dir,
                handoff_paths=handoff_paths,
                repo_root=repo_root,
                git_commit=False,
                stdout=stdout,
                stderr=stderr,
            )

            self.assertIn(
                "control/audits/public-alpha-readonly-closeout-01-v0/external_gate_result.json",
                changed,
            )
            self.assertIn(
                "control/audits/public-alpha-readonly-closeout-01-v0/external_gate_handoff.md",
                changed,
            )
            self.assertIn("control/inventory/public_alpha_readonly_closeout_full_discovery_result.json", changed)
            for path in changed:
                self.assertNotIn("full_unittest_stdout", path)
                self.assertNotIn("full_unittest_stderr", path)
                self.assertNotIn("eureka-test-runs", path)

    def test_commit_handoff_cli_does_not_git_commit_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            stdout = io.StringIO()

            with patch.object(gate_tool, "commit_handoff_bundle", return_value=["control/audits/example/external_gate_result.json"]) as commit_handoff:
                exit_code = gate_tool.main(
                    ["public-alpha-closeout", "--out", str(out_dir), "--commit-handoff", "--json"],
                    stdout=stdout,
                )

            self.assertEqual(0, exit_code)
            self.assertFalse(commit_handoff.call_args.kwargs["git_commit"])
            payload = json.loads(stdout.getvalue())
            self.assertEqual("eureka_gate_commit_handoff.v0", payload["schema_version"])
            self.assertFalse(payload["git_commit_performed"])


if __name__ == "__main__":
    unittest.main()
