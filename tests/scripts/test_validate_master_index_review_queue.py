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
VALIDATOR = REPO_ROOT / "scripts" / "validate_master_index_review_queue.py"
EXAMPLE_QUEUE = REPO_ROOT / "examples" / "master_index_review_queue" / "minimal_review_queue_v0"


class ValidateMasterIndexReviewQueueScriptTestCase(unittest.TestCase):
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
        self.assertEqual(payload["queue_id"], "example.master_index_review_queue_v0")
        self.assertEqual(payload["queue_entry_count"], 1)
        self.assertEqual(payload["decision_count"], 1)

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
                [sys.executable, str(VALIDATOR), "--queue-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("REVIEW_QUEUE_MANIFEST.json" in error for error in payload["errors"]))

    def test_validator_rejects_unknown_decision_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "unknown_entry"
            shutil.copytree(EXAMPLE_QUEUE, root)
            decisions_path = root / "review_decisions.jsonl"
            records = []
            for line in decisions_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                record["queue_entry_id"] = "queue.example.missing"
                records.append(json.dumps(record, sort_keys=True))
            decisions_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--queue-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("unknown queue_entry_id" in error for error in payload["errors"]))

    def test_validator_rejects_private_path_in_public_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private_path"
            shutil.copytree(EXAMPLE_QUEUE, root)
            entries_path = root / "queue_entries.jsonl"
            records = []
            for line in entries_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                record["reviewer_notes"].append("Private note leaked C:\\Users\\Alice\\review\\queue.json")
                records.append(json.dumps(record, sort_keys=True))
            entries_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--queue-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("private or absolute local path" in error for error in payload["errors"]))

    def test_validator_rejects_auto_acceptance_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "auto_accept"
            shutil.copytree(EXAMPLE_QUEUE, root)
            manifest = _read_manifest(root)
            manifest["no_auto_acceptance"] = False
            _write_manifest(root, manifest)
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--queue-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("no_auto_acceptance" in error for error in payload["errors"]))

    def test_validator_rejects_executable_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "executable"
            shutil.copytree(EXAMPLE_QUEUE, root)
            (root / "plugin.exe").write_text("not executable content, but forbidden extension\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--queue-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("forbidden executable payload extension" in error for error in payload["errors"]))

    def test_validator_rejects_accept_public_without_limitations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "accept_without_limitations"
            shutil.copytree(EXAMPLE_QUEUE, root)
            decisions_path = root / "review_decisions.jsonl"
            records = []
            for line in decisions_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                record["decision"] = "accept_public"
                record["limitations"] = []
                record["public_claims_allowed"]["allowed"] = True
                record["public_claims_allowed"]["claims"] = ["synthetic metadata claim only"]
                records.append(json.dumps(record, sort_keys=True))
            decisions_path.write_text("\n".join(records) + "\n", encoding="utf-8")
            _write_checksums(root)

            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--queue-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("limitations" in error for error in payload["errors"]))


def _read_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "REVIEW_QUEUE_MANIFEST.json").read_text(encoding="utf-8"))


def _write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "REVIEW_QUEUE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _write_checksums(root: Path) -> None:
    rel_paths = [
        "README.md",
        "REVIEW_QUEUE_MANIFEST.json",
        "queue_entries.jsonl",
        "review_decisions.jsonl",
    ]
    lines = []
    for rel_path in rel_paths:
        digest = hashlib.sha256((root / rel_path).read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel_path}")
    (root / "CHECKSUMS.SHA256").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
