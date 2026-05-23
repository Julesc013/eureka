from __future__ import annotations

import subprocess
import sys
import tempfile
import socket
from pathlib import Path
import unittest

from runtime.local.eval import run_safety_checks


ROOT = Path(__file__).resolve().parents[2]


class LocalEvalSafetyTests(unittest.TestCase):
    def test_safety_checks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = subprocess.run(
                [sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            port = free_port()
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
            self.assertIn('"status": "pass"', line)
            try:
                result = run_safety_checks(f"http://127.0.0.1:{port}")
            finally:
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
            self.assertEqual("pass", result["status"])
            self.assertFalse(result["lan_enabled"])
            self.assertTrue(result["source_probe_routes_absent_or_disabled"])


def free_port() -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


if __name__ == "__main__":
    unittest.main()
