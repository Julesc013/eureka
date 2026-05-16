from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts/validate_aide_report_sizes.py"
SPEC = importlib.util.spec_from_file_location("validate_aide_report_sizes", SCRIPT_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class AideReportSizeValidatorTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".aide/policies").mkdir(parents=True)
        (root / ".aide/policies/report-size.yaml").write_text(
            "\n".join(
                [
                    "schema_version: aide.report-size-policy.v0",
                    "warning_threshold_mb: 1",
                    "hard_threshold_mb: 2",
                    "preferred_max_report_mb: 1",
                    "shard_hard_threshold_mb: 2",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return root

    def write_valid_ledger(self, root: Path) -> None:
        shard_path = root / ".aide/reports/file-quality-ledger/shards/file-quality-ledger-0001.json"
        shard_path.parent.mkdir(parents=True)
        shard_path.write_text(
            json.dumps(
                {
                    "schema_version": "aide.file-quality-ledger-shard.v0",
                    "records": [{"path": "README.md"}],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        ledger = {
            "schema_version": "aide.file-quality-ledger.v0",
            "record_storage": "sharded",
            "record_count": 1,
            "records": [],
            "record_shards": [
                {
                    "shard_id": "file-quality-ledger-0001",
                    "path": ".aide/reports/file-quality-ledger/shards/file-quality-ledger-0001.json",
                    "record_count": 1,
                }
            ],
        }
        (root / ".aide/reports").mkdir(exist_ok=True)
        (root / ".aide/reports/file-quality-ledger.json").write_text(json.dumps(ledger, sort_keys=True) + "\n", encoding="utf-8")

    def test_report_size_validator_detects_oversized_files(self) -> None:
        root = self.make_repo()
        self.write_valid_ledger(root)
        big_path = root / ".aide/reports/big.json"
        big_path.write_bytes(b"x" * (3 * 1024 * 1024))
        result = validator.validate(root)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(result["hard_threshold_violations"])

    def test_compact_sharded_ledger_validates(self) -> None:
        root = self.make_repo()
        self.write_valid_ledger(root)
        result = validator.validate(root)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["ledger"]["shard_count"], 1)

    def test_validator_rejects_binary_only_opaque_report(self) -> None:
        root = self.make_repo()
        self.write_valid_ledger(root)
        archive = root / ".aide/reports/file-quality-ledger.zip"
        archive.write_bytes(b"PK\x03\x04")
        result = validator.validate(root)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("opaque compressed" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
