from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_contribution_pack.py"
EXAMPLE_PACK = REPO_ROOT / "examples" / "contribution_packs" / "minimal_contribution_pack_v0"


class ValidateContributionPackScriptTestCase(unittest.TestCase):
    def test_validator_passes_plain_json_and_strict(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["pack_id"], "example.minimal_contribution_pack_v0")
        self.assertEqual(payload["contribution_item_count"], 3)
        self.assertEqual(payload["manual_observation_count"], 1)

        strict = subprocess.run(
            [sys.executable, str(VALIDATOR), "--strict"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", strict.stdout)

    def test_validator_supports_all_examples_aliases(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["mode"], "all_examples")
        self.assertEqual(payload["example_count"], 1)

        alias = subprocess.run(
            [sys.executable, str(VALIDATOR), "--known-examples"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("mode: all_examples", alias.stdout)

    def test_validator_fails_for_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "missing_manifest"
            root.mkdir()
            (root / "README.md").write_text("Example\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(any("CONTRIBUTION_PACK.json" in error for error in payload["errors"]))

    def test_validator_rejects_public_pack_private_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private_path_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            records_path = root / "contribution_items.jsonl"
            records = []
            for index, line in enumerate(records_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["summary"] = "This leaks C:\\Users\\Alice\\private\\cache\\note.txt"
                records.append(json.dumps(record, sort_keys=True))
            records_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("private or absolute local path" in error for error in payload["errors"]))

    def test_validator_rejects_sqlite_database_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "database_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            db_path = root / "review.sqlite"
            db_path.write_text("not a real database, but extension is forbidden\n", encoding="utf-8")
            manifest = _read_manifest(root)
            manifest["checksum_policy"]["covers"].append("review.sqlite")
            _write_manifest(root, manifest)
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("raw database/cache extension" in error for error in payload["errors"]))

    def test_validator_rejects_executable_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "executable_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            tool = root / "plugin.exe"
            tool.write_text("extension is forbidden\n", encoding="utf-8")
            manifest = _read_manifest(root)
            manifest["checksum_policy"]["covers"].append("plugin.exe")
            _write_manifest(root, manifest)
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("forbidden executable payload extension" in error for error in payload["errors"]))

    def test_validator_rejects_invalid_contribution_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "invalid_type_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            records_path = root / "contribution_items.jsonl"
            records = []
            for index, line in enumerate(records_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["contribution_type"] = "auto_accept_payload"
                records.append(json.dumps(record, sort_keys=True))
            records_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("unsupported contribution_type" in error for error in payload["errors"]))

    def test_validator_rejects_invalid_proposed_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "invalid_action_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            records_path = root / "contribution_items.jsonl"
            records = []
            for index, line in enumerate(records_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["proposed_action"] = "auto_merge_now"
                records.append(json.dumps(record, sort_keys=True))
            records_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("unsupported proposed_action" in error for error in payload["errors"]))

    def test_validator_rejects_fake_observed_manual_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "fake_observed_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            observations_path = root / "manual_observations.jsonl"
            observations = []
            for line in observations_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                record["observation_status"] = "observed"
                observations.append(json.dumps(record, sort_keys=True))
            observations_path.write_text("\n".join(observations) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("observed manual observation" in error or "synthetic" in error for error in payload["errors"]))


def _read_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "CONTRIBUTION_PACK.json").read_text(encoding="utf-8"))


def _write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "CONTRIBUTION_PACK.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _write_checksums(root: Path) -> None:
    manifest = _read_manifest(root)
    policy = manifest["checksum_policy"]  # type: ignore[index]
    lines = []
    for rel_path in policy["covers"]:  # type: ignore[index]
        data = (root / str(rel_path)).read_bytes()
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {rel_path}")
    (root / "CHECKSUMS.SHA256").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
