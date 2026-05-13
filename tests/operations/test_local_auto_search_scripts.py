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


class LocalAutoSearchScriptTests(unittest.TestCase):
    def test_auto_search_refuses_non_localhost(self) -> None:
        completed = run_cmd("scripts/eureka_local_auto_search.py", "--base-url", "http://example.com:8765", "--json")
        self.assertNotEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("fail", payload["status"])

    def test_auto_search_runs_with_builtin_and_query_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd("scripts/eureka_init_instance.py", "--instance", str(instance), "--json").returncode)
            port = free_port()
            process = start_server(instance, port)
            try:
                base_url = f"http://127.0.0.1:{port}"
                builtin = run_cmd("scripts/eureka_local_auto_search.py", "--base-url", base_url, "--json", timeout=90)
                self.assertEqual(0, builtin.returncode, builtin.stderr)
                payload = json.loads(builtin.stdout)
                self.assertEqual("pass", payload["status"])
                self.assertTrue(payload["queries"])
                query_file = Path(tmp) / "queries.json"
                query_file.write_text(json.dumps(["sampleproject", "definitely-not-present-local-10"]), encoding="utf-8")
                custom = run_cmd("scripts/eureka_local_auto_search.py", "--base-url", base_url, "--query-file", str(query_file), "--json")
                self.assertEqual(0, custom.returncode, custom.stderr)
            finally:
                stop_server(process)

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
