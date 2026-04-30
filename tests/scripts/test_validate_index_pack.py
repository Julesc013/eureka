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
VALIDATOR = REPO_ROOT / "scripts" / "validate_index_pack.py"
EXAMPLE_PACK = REPO_ROOT / "examples" / "index_packs" / "minimal_index_pack_v0"


class ValidateIndexPackScriptTestCase(unittest.TestCase):
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
        self.assertEqual(payload["pack_id"], "example.minimal_index_pack_v0")
        self.assertEqual(payload["source_count"], 2)
        self.assertEqual(payload["record_count"], 4)

        strict = subprocess.run(
            [sys.executable, str(VALIDATOR), "--strict"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", strict.stdout)

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
        self.assertTrue(any("INDEX_PACK.json" in error for error in payload["errors"]))

    def test_validator_rejects_public_pack_private_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private_path_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            records_path = root / "record_summaries.jsonl"
            records = []
            for line in records_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                record["member_path"] = "C:\\Users\\Alice\\private\\cache\\member.inf"
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
            db_path = root / "index.sqlite"
            db_path.write_text("not a real database, but extension is forbidden\n", encoding="utf-8")
            manifest = _read_manifest(root)
            manifest["checksum_policy"]["covers"].append("index.sqlite")
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
            tool = root / "tool.exe"
            tool.write_text("extension is forbidden\n", encoding="utf-8")
            manifest = _read_manifest(root)
            manifest["checksum_policy"]["covers"].append("tool.exe")
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

    def test_validator_rejects_unknown_source_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "unknown_source_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            records_path = root / "record_summaries.jsonl"
            records = []
            for index, line in enumerate(records_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["source_id"] = "example.missing_source"
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
        self.assertTrue(any("references unknown source_id" in error for error in payload["errors"]))

    def test_validator_rejects_invalid_record_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "invalid_record_kind_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            records_path = root / "record_summaries.jsonl"
            records = []
            for index, line in enumerate(records_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["record_kind"] = "raw_sqlite_row"
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
        self.assertTrue(any("unsupported record_kind" in error for error in payload["errors"]))


def _read_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "INDEX_PACK.json").read_text(encoding="utf-8"))


def _write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "INDEX_PACK.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


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
