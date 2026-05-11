from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9MediaMetadataLiveProbeScriptTests(unittest.TestCase):
    def run_cmd(self, args):
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)

    def test_cli_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            before = set(Path(tempdir).iterdir())
            run = self.run_cmd(["scripts/run_h9_media_metadata_live_probe.py", "--source-id", "musicbrainz", "--request-key", "example_recording_metadata", "--json"])
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(before, set(Path(tempdir).iterdir()))

    def test_cli_writes_explicit_outputs_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            out = Path(tempdir) / "probe.json"
            summary = Path(tempdir) / "summary.md"
            run = self.run_cmd(["scripts/run_h9_media_metadata_live_probe.py", "--source-id", "musicbrainz", "--request-key", "example_recording_metadata", "--output", str(out), "--summary-output", str(summary), "--json"])
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertTrue(out.is_file())
            self.assertTrue(summary.is_file())
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertFalse(payload["network_used"])

    def test_cli_refuses_forbidden_output_roots(self) -> None:
        for path in ("site/dist/probe.json", "data/public_index/probe.json", "media_downloads/probe.json", "media_uploads/probe.json", "fingerprint_cache/probe.json"):
            with self.subTest(path=path):
                run = self.run_cmd(["scripts/run_h9_media_metadata_live_probe.py", "--source-id", "musicbrainz", "--request-key", "example_recording_metadata", "--output", path, "--json"])
                self.assertNotEqual(run.returncode, 0)

    def test_summary_script_writes_explicit_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            out = Path(tempdir) / "summary.json"
            md = Path(tempdir) / "summary.md"
            run = self.run_cmd(["scripts/summarize_h9_media_metadata_live_probe_outputs.py", "--input", "examples/connectors/h9_media_metadata/live_probe_results", "--output", str(out), "--summary-output", str(md), "--json"])
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertTrue(out.is_file())
            self.assertTrue(md.is_file())

    def test_summary_script_refuses_public_index(self) -> None:
        run = self.run_cmd(["scripts/summarize_h9_media_metadata_live_probe_outputs.py", "--input", "examples/connectors/h9_media_metadata/live_probe_results", "--output", "data/public_index/summary.json", "--json"])
        self.assertNotEqual(run.returncode, 0)

    def test_validator_passes_and_uses_no_private_roots(self) -> None:
        run = self.run_cmd(["scripts/validate_h9_media_metadata_live_probe.py", "--json"])
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        payload = json.loads(run.stdout)
        self.assertFalse(payload["network_calls_made"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
