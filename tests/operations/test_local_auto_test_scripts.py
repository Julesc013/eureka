from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import socket
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


class LocalAutoTestScriptTests(unittest.TestCase):
    def test_auto_test_refuses_non_localhost(self) -> None:
        completed = run_cmd("scripts/eureka_local_auto_test.py", "--base-url", "http://example.com:8765", "--json")
        self.assertNotEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("fail", payload["status"])

    def test_auto_test_and_report_scripts_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd("scripts/eureka_init_instance.py", "--instance", str(instance), "--json").returncode)
            port = free_port()
            process = start_server(instance, port)
            try:
                report_path = Path(tmp) / "report.json"
                summary_path = Path(tmp) / "summary.md"
                completed = run_cmd(
                    "scripts/eureka_local_auto_test.py",
                    "--base-url",
                    f"http://127.0.0.1:{port}",
                    "--json",
                    "--output",
                    str(report_path),
                    "--summary-output",
                    str(summary_path),
                    timeout=90,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertEqual("pass", payload["status"])
                converted = run_cmd(
                    "scripts/eureka_local_eval_report.py",
                    "--input",
                    str(report_path),
                    "--output",
                    str(Path(tmp) / "converted.md"),
                    "--json",
                )
                self.assertEqual(0, converted.returncode, converted.stderr)
            finally:
                stop_server(process)

    def test_validator_passes(self) -> None:
        completed = run_cmd("scripts/validate_local_auto_test_harness.py", "--json", timeout=240)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["service_health_suite_passed"])
        self.assertFalse(payload["source_probe_executed"])

def free_port() -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


def start_server(instance: Path, port: int) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [
            sys.executable,
            "scripts/eureka_local_server.py",
            "--instance",
            str(instance),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--json-startup",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    line = process.stdout.readline() if process.stdout else ""
    if '"status": "pass"' not in line:
        raise AssertionError(line)
    return process


def stop_server(process: subprocess.Popen[str]) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()


if __name__ == "__main__":
    unittest.main()
