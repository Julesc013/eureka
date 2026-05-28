from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import scripts.eureka_test_gate as gate_tool


GATES = gate_tool.GATES
main = gate_tool.main


class EurekaTestGateTests(unittest.TestCase):
    def write_test_module(self, root: Path, source: str) -> Path:
        tests_dir = root / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / "test_tiny.py").write_text(source, encoding="utf-8")
        return tests_dir

    def write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_complete_gate_artifacts(self, out_dir: Path, *, status: str = "pass") -> None:
        summary = {
            "schema_version": "full_unittest_summary.v0",
            "command": "python -m unittest discover -s tests -t .",
            "status": status,
            "exit_code": 0 if status == "pass" else 1,
            "started_at": "2026-05-28T00:00:00Z",
            "finished_at": "2026-05-28T00:01:00Z",
            "duration_seconds": 60,
            "counts": {"tests_run": 3, "failures": 0 if status == "pass" else 1, "errors": 0, "skipped": 0},
        }
        self.write_json(out_dir / "full_unittest_summary.json", summary)
        self.write_json(out_dir / "failure_families.json", {"schema_version": "failure_family_list.v0", "failure_families": []})
        (out_dir / "failed_tests.txt").write_text("tests.example.TestCase.test_fail\n" if status != "pass" else "", encoding="utf-8")
        self.write_json(
            out_dir / "status.json",
            {
                "schema_version": "full_discovery_status.v0",
                "run_id": "public_alpha_readonly_closeout",
                "status": status,
                "pid": None,
                "command": "python -m unittest discover -s tests -t .",
                "started_at": "2026-05-28T00:00:00Z",
                "updated_at": "2026-05-28T00:01:00Z",
                "elapsed_seconds": 60,
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

    def test_supported_gates_are_defined(self) -> None:
        self.assertIn("public_alpha_readonly_closeout", GATES)
        self.assertIn("source_snapshot_closeout", GATES)
        self.assertIn("promotion_gate", GATES)

    def test_status_reports_missing_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()

            exit_code = main(
                ["--gate", "public_alpha_readonly_closeout", "--out", str(Path(tmp) / "missing"), "--status"],
                stdout=stdout,
            )

            self.assertEqual(0, exit_code)
            self.assertIn("status: missing", stdout.getvalue())
            self.assertIn("--watch --clean", stdout.getvalue())

    def test_handoff_writes_ai_handoff_for_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            stdout = io.StringIO()

            exit_code = main(
                ["--gate", "public_alpha_readonly_closeout", "--out", str(out_dir), "--handoff"],
                stdout=stdout,
            )

            self.assertEqual(0, exit_code)
            handoff = out_dir / "ai_handoff.md"
            self.assertTrue(handoff.is_file())
            text = stdout.getvalue()
            self.assertIn("STATUS: PASS", text)
            self.assertIn("Finish PUBLIC-ALPHA-READONLY-CLOSEOUT-01", text)
            self.assertIn("COMPACT_SUMMARY_JSON", text)

    def test_handoff_incomplete_prints_watch_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_json(
                out_dir / "status.json",
                {
                    "schema_version": "full_discovery_status.v0",
                    "run_id": "public_alpha_readonly_closeout",
                    "status": "running",
                    "pid": -1,
                    "elapsed_seconds": 30,
                    "stdout_bytes": 0,
                    "stderr_bytes": 0,
                    "summary_path": str(out_dir / "full_unittest_summary.json"),
                    "failure_families_path": str(out_dir / "failure_families.json"),
                    "failed_tests_path": str(out_dir / "failed_tests.txt"),
                },
            )
            stdout = io.StringIO()

            exit_code = main(
                ["--gate", "public_alpha_readonly_closeout", "--out", str(out_dir), "--handoff"],
                stdout=stdout,
            )

            self.assertEqual(1, exit_code)
            self.assertIn("status: running", stdout.getvalue())
            self.assertIn("python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --watch", stdout.getvalue())

    def test_background_starts_gate_and_prints_followup_commands(self) -> None:
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
                exit_code = main(
                    [
                        "--gate",
                        "public_alpha_readonly_closeout",
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
            self.assertIn("Started gate public_alpha_readonly_closeout", stdout.getvalue())
            self.assertIn("PID: 4321", stdout.getvalue())
            self.assertIn("--handoff", stdout.getvalue())

    def test_watch_runs_tiny_gate_and_writes_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = self.write_test_module(
                root,
                "import unittest\n\n"
                "class Tiny(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
            )
            out_dir = root / "run"
            stdout = io.StringIO()

            exit_code = main(
                [
                    "--gate",
                    "public_alpha_readonly_closeout",
                    "--out",
                    str(out_dir),
                    "--watch",
                    "--start-dir",
                    str(tests_dir),
                    "--top-level-dir",
                    str(root),
                    "--heartbeat-seconds",
                    "1",
                ],
                stdout=stdout,
            )

            self.assertEqual(0, exit_code)
            self.assertTrue((out_dir / "ai_handoff.md").is_file())
            self.assertIn("[eureka-test-gate] status=pass", stdout.getvalue())

    def test_watch_reuses_completed_gate_without_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            stdout = io.StringIO()

            with patch.object(gate_tool, "run_discovery") as run_discovery:
                exit_code = main(
                    ["--gate", "public_alpha_readonly_closeout", "--out", str(out_dir), "--watch"],
                    stdout=stdout,
                )

            self.assertEqual(0, exit_code)
            run_discovery.assert_not_called()
            self.assertTrue((out_dir / "ai_handoff.md").is_file())
            self.assertIn("[eureka-test-gate] status=pass", stdout.getvalue())

    def test_json_status_uses_gate_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run"
            self.write_complete_gate_artifacts(out_dir, status="pass")
            stdout = io.StringIO()

            exit_code = main(
                ["--gate", "public_alpha_readonly_closeout", "--out", str(out_dir), "--status", "--json"],
                stdout=stdout,
            )

            self.assertEqual(0, exit_code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("test_gate_status.v0", payload["schema_version"])
            self.assertEqual("public_alpha_readonly_closeout", payload["gate"])
            self.assertEqual("pass", payload["status"])


if __name__ == "__main__":
    unittest.main()
