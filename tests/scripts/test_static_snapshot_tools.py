from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPO_ROOT / "scripts" / "generate_static_snapshot.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_static_snapshot.py"
SNAPSHOT_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"


class StaticSnapshotToolsTest(unittest.TestCase):
    def test_generator_json_and_check_pass(self) -> None:
        payload = self._run_json(GENERATOR, "--json")

        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["snapshot_format_version"], "0.1.0")
        self.assertFalse(payload["production_signed_release"])
        self.assertFalse(payload["real_signing_keys_present"])
        self.assertFalse(payload["contains_real_binaries"])
        self.assertIn("SNAPSHOT_MANIFEST.json", payload["files"])

        check = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", check.stdout)

    def test_generator_writes_temp_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "snapshot"
            subprocess.run(
                [sys.executable, str(GENERATOR), "--update", "--output-root", str(out)],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue((out / "SNAPSHOT_MANIFEST.json").is_file())
            self.assertTrue((out / "CHECKSUMS.SHA256").is_file())
            payload = json.loads((out / "SNAPSHOT_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["snapshot_format_version"], "0.1.0")
            self.assertFalse(payload["contains_live_backend"])

    def test_validator_json_passes_and_checksum_entries_match(self) -> None:
        payload = self._run_json(VALIDATOR, "--json")

        self.assertEqual(payload["status"], "valid")
        self.assertIn("SNAPSHOT_MANIFEST.json", payload["checksum_entries"])
        self.assertEqual(payload["errors"], [])

        entries: dict[str, str] = {}
        for line in (SNAPSHOT_ROOT / "CHECKSUMS.SHA256").read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            entries[relative] = digest
        for relative, digest in entries.items():
            with self.subTest(relative=relative):
                actual = hashlib.sha256((SNAPSHOT_ROOT / relative).read_bytes()).hexdigest()
                self.assertEqual(actual, digest)

    def _run_json(self, script: Path, *args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
