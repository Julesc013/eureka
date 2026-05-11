from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import summarize_h12_retro_community_fixture_outputs as summary
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12RetroCommunityFixtureScriptTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=validator.REPO_ROOT, text=True, capture_output=True, check=False)

    def test_scripts_write_no_files_by_default_and_pass_check(self) -> None:
        normalize = self.run_cmd("scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/retro_software_identity_record.json", "--check")
        replay = self.run_cmd("scripts/replay_h12_retro_community_fixtures.py", "--check")
        summarize = self.run_cmd("scripts/summarize_h12_retro_community_fixture_outputs.py", "--input", "examples/connectors/h12_retro_community", "--check")
        self.assertEqual(normalize.returncode, 0, normalize.stdout + normalize.stderr)
        self.assertEqual(replay.returncode, 0, replay.stdout + replay.stderr)
        self.assertEqual(summarize.returncode, 0, summarize.stdout + summarize.stderr)

    def test_scripts_write_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            normalize = self.run_cmd("scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/retro_software_identity_record.json", "--output", str(tmp_path / "normalized.json"))
            replay = self.run_cmd("scripts/replay_h12_retro_community_fixtures.py", "--source-id", "winworld_metadata", "--output-dir", str(tmp_path / "replay"))
            self.assertEqual(normalize.returncode, 0, normalize.stdout + normalize.stderr)
            self.assertEqual(replay.returncode, 0, replay.stdout + replay.stderr)
            self.assertTrue((tmp_path / "normalized.json").exists())
            self.assertTrue((tmp_path / "replay" / "winworld_metadata" / "normalized_record.json").exists())

    def test_forbidden_output_roots_rejected(self) -> None:
        for root in ("site/dist/h12.json", "data/public_index/h12.json", "roms/h12.json", "archive_extractions/h12.json"):
            proc = self.run_cmd("scripts/normalize_h12_retro_community_fixture.py", "--source-id", "winworld_metadata", "--input", "examples/connectors/h12_retro_community/fixtures/winworld_metadata/minimal_record.json", "--output", root)
            self.assertNotEqual(proc.returncode, 0, root)

    def test_summary_builds(self) -> None:
        result = summary.build_summary(["examples/connectors/h12_retro_community"])
        self.assertEqual(result["status"], "pass")
        self.assertGreaterEqual(result["source_count"], 13)


if __name__ == "__main__":
    unittest.main()
