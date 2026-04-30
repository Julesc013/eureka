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
VALIDATOR = REPO_ROOT / "scripts" / "validate_evidence_pack.py"
EXAMPLE_PACK = REPO_ROOT / "examples" / "evidence_packs" / "minimal_evidence_pack_v0"


class ValidateEvidencePackScriptTestCase(unittest.TestCase):
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
        self.assertEqual(payload["pack_id"], "example.minimal_evidence_pack_v0")
        self.assertEqual(payload["evidence_record_count"], 4)
        self.assertEqual(payload["source_reference_count"], 1)

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
        self.assertTrue(any("EVIDENCE_PACK.json" in error for error in payload["errors"]))

    def test_validator_rejects_public_pack_private_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private_path_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            evidence_path = root / "evidence_records.jsonl"
            records = []
            for line in evidence_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                record["locator"] = "C:\\Users\\Alice\\private\\note.txt"
                records.append(json.dumps(record, sort_keys=True))
            evidence_path.write_text("\n".join(records) + "\n", encoding="utf-8")
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

    def test_validator_rejects_executable_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "executable_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            tool = root / "tool.exe"
            tool.write_text("not executable, but extension is forbidden\n", encoding="utf-8")
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
        self.assertTrue(any("forbidden executable/archive payload extension" in error for error in payload["errors"]))

    def test_validator_rejects_invalid_claim_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "invalid_claim_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            evidence_path = root / "evidence_records.jsonl"
            records = []
            for index, line in enumerate(evidence_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["claim_type"] = "is_truth"
                records.append(json.dumps(record, sort_keys=True))
            evidence_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("unsupported claim_type" in error for error in payload["errors"]))

    def test_validator_rejects_long_snippet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "long_snippet_pack"
            shutil.copytree(EXAMPLE_PACK, root)
            evidence_path = root / "evidence_records.jsonl"
            records = []
            for index, line in enumerate(evidence_path.read_text(encoding="utf-8").splitlines()):
                record = json.loads(line)
                if index == 0:
                    record["snippet"] = "x" * 501
                records.append(json.dumps(record, sort_keys=True))
            evidence_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("snippet exceeds" in error for error in payload["errors"]))


def _read_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "EVIDENCE_PACK.json").read_text(encoding="utf-8"))


def _write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "EVIDENCE_PACK.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


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
