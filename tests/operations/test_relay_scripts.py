import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_script(*args, expect_success=True):
    result = subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True)
    if expect_success and result.returncode:
        raise AssertionError(f"{' '.join(args)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


class RelayScriptTests(unittest.TestCase):
    def test_scripts_write_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "not_written.txt"
            run_script(
                "scripts/render_relay_fixture.py",
                "--snapshot",
                "examples/snapshots/fixtures/search_snapshot_input_v0.json",
                "--profile",
                "examples/relay/profiles/localhost_readonly_profile_v0.json",
                "--route",
                "/search",
                "--render-profile",
                "text",
            )
            self.assertFalse(output.exists())

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "relay.txt"
            run_script(
                "scripts/render_relay_fixture.py",
                "--snapshot",
                "examples/snapshots/fixtures/search_snapshot_input_v0.json",
                "--profile",
                "examples/relay/profiles/localhost_readonly_profile_v0.json",
                "--route",
                "/search",
                "--render-profile",
                "text",
                "--output",
                str(output),
            )
            self.assertIn("Source posture", output.read_text(encoding="utf-8"))

    def test_scripts_refuse_site_dist_output(self):
        result = run_script(
            "scripts/render_relay_fixture.py",
            "--snapshot",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--route",
            "/search",
            "--render-profile",
            "text",
            "--output",
            "site/dist/relay.txt",
            expect_success=False,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_scripts_refuse_data_public_index_output(self):
        result = run_script(
            "scripts/check_relay_routes.py",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--output",
            "data/public_index/relay.json",
            expect_success=False,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_run_script_does_not_start_server_by_default(self):
        result = run_script(
            "scripts/run_readonly_relay_fixture.py",
            "--snapshot",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--check",
        )
        payload = json.loads(result.stdout)
        self.assertFalse(payload["server_starts_by_default"])

    def test_run_script_rejects_public_bind(self):
        result = run_script(
            "scripts/run_readonly_relay_fixture.py",
            "--snapshot",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--host",
            "0.0.0.0",
            "--check",
            expect_success=False,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_validator_passes_current_repo(self):
        run_script("scripts/validate_relay_runtime.py")

    def test_validator_does_not_create_local_private_roots(self):
        run_script("scripts/validate_relay_runtime.py")
        self.assertFalse((REPO_ROOT / ".aide.local").exists())
        self.assertFalse((REPO_ROOT / ".local/eureka").exists())
        self.assertFalse((REPO_ROOT / ".cache/eureka").exists())


if __name__ == "__main__":
    unittest.main()

