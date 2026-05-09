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


class SnapshotScriptTests(unittest.TestCase):
    def test_build_script_writes_no_files_by_default(self):
        before = {path.as_posix() for path in (REPO_ROOT / "examples/snapshots/manifests").glob("*.json")}
        run_script("scripts/build_snapshot_fixture.py", "--input", "examples/snapshots/fixtures/search_snapshot_input_v0.json")
        after = {path.as_posix() for path in (REPO_ROOT / "examples/snapshots/manifests").glob("*.json")}
        self.assertEqual(before, after)

    def test_render_script_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "not_written.txt"
            run_script("scripts/render_snapshot_fixture.py", "--input", "examples/snapshots/fixtures/search_snapshot_input_v0.json", "--profile", "text")
            self.assertFalse(output.exists())

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = tmp_path / "manifest.json"
            text = tmp_path / "snapshot.txt"
            run_script(
                "scripts/build_snapshot_fixture.py",
                "--input",
                "examples/snapshots/fixtures/search_snapshot_input_v0.json",
                "--manifest-output",
                str(manifest),
            )
            run_script(
                "scripts/render_snapshot_fixture.py",
                "--input",
                "examples/snapshots/fixtures/search_snapshot_input_v0.json",
                "--profile",
                "text",
                "--output",
                str(text),
            )
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["schema_version"], "snapshot_manifest.v0")
            self.assertIn("Source posture", text.read_text(encoding="utf-8"))

    def test_scripts_refuse_site_dist_output(self):
        result = run_script(
            "scripts/render_snapshot_fixture.py",
            "--input",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "text",
            "--output",
            "site/dist/snapshot.txt",
            expect_success=False,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_scripts_refuse_data_public_index_output(self):
        result = run_script(
            "scripts/build_snapshot_fixture.py",
            "--input",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--manifest-output",
            "data/public_index/snapshot.json",
            expect_success=False,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_scripts_refuse_relay_hosted_private_roots(self):
        for path in ("relay/snapshot.txt", "hosted/snapshot.txt", ".cache/eureka/snapshot.txt"):
            result = run_script(
                "scripts/render_snapshot_fixture.py",
                "--input",
                "examples/snapshots/fixtures/search_snapshot_input_v0.json",
                "--profile",
                "text",
                "--output",
                path,
                expect_success=False,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_validator_passes_current_repo(self):
        run_script("scripts/validate_snapshot_runtime.py")

    def test_validator_does_not_create_local_private_roots(self):
        run_script("scripts/validate_snapshot_runtime.py")
        self.assertFalse((REPO_ROOT / ".aide.local").exists())
        self.assertFalse((REPO_ROOT / ".local/eureka").exists())
        self.assertFalse((REPO_ROOT / ".cache/eureka").exists())


if __name__ == "__main__":
    unittest.main()
