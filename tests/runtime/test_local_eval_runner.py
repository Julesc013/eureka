from __future__ import annotations

import subprocess
import sys
import tempfile
import socket
from pathlib import Path
import unittest

from runtime.local_eval import LocalEvalRunner


ROOT = Path(__file__).resolve().parents[2]


class LocalServiceFixture:
    def __enter__(self) -> str:
        self.tempdir = tempfile.TemporaryDirectory()
        self.instance = Path(self.tempdir.name) / "eureka-instance"
        completed = subprocess.run(
            [sys.executable, "scripts/eureka_init_instance.py", "--instance", str(self.instance), "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode:
            raise AssertionError(completed.stderr or completed.stdout)
        self.port = free_port()
        self.process = subprocess.Popen(
            [
                sys.executable,
                "scripts/eureka_local_server.py",
                "--instance",
                str(self.instance),
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--json-startup",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        line = self.process.stdout.readline() if self.process.stdout else ""
        if '"status": "pass"' not in line:
            raise AssertionError(line)
        return f"http://127.0.0.1:{self.port}"

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        if self.process.stdout:
            self.process.stdout.close()
        if self.process.stderr:
            self.process.stderr.close()
        self.tempdir.cleanup()


def free_port() -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


class LocalEvalRunnerTests(unittest.TestCase):
    def test_runner_runs_all_default_suites(self) -> None:
        with LocalServiceFixture() as base_url:
            report = LocalEvalRunner().run_all(base_url)
        self.assertEqual("pass", report["status"])
        self.assertTrue(report["latency"]["route_count"])
        names = {suite["suite"] for suite in report["suite_results"]}
        self.assertIn("service_health", names)
        self.assertIn("read_only_safety", names)

    def test_runner_rejects_non_localhost(self) -> None:
        with self.assertRaises(Exception):
            LocalEvalRunner().run_all("http://example.com:8765")


if __name__ == "__main__":
    unittest.main()
