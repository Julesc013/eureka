from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / ".aide/scripts/aide_lite.py"
SPEC = importlib.util.spec_from_file_location("aide_lite_size_tests", MODULE_PATH)
aide_lite = importlib.util.module_from_spec(SPEC)
sys.modules["aide_lite_size_tests"] = aide_lite
assert SPEC.loader is not None
SPEC.loader.exec_module(aide_lite)


class FileQualityLedgerShardingTests(unittest.TestCase):
    def test_write_quality_outputs_creates_deterministic_shards(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        old_target = aide_lite.FILE_QUALITY_LEDGER_SHARD_TARGET_BYTES
        aide_lite.FILE_QUALITY_LEDGER_SHARD_TARGET_BYTES = 900
        self.addCleanup(setattr, aide_lite, "FILE_QUALITY_LEDGER_SHARD_TARGET_BYTES", old_target)
        records = [
            {
                "path": f"src/file_{index:04d}.py",
                "kind": "source",
                "status": "active",
                "owner": "test",
                "quality_level": "warn",
                "dimensions": {},
                "docs_refs": [],
                "test_refs": [],
                "dependency_refs": ["dep"] * 20,
                "warnings": ["missing_doc_candidate"],
                "exemptions": [],
                "recommended_next_action": "review",
                "evidence_refs": [],
            }
            for index in range(30)
        ]
        ledger = {
            "schema_version": "aide.file-quality-ledger.v0",
            "generated_by": "aide-lite",
            "source_commit": "abc",
            "source_repo_intelligence": {},
            "summary": {"file_count": len(records), "fail_count": 0},
            "records": records,
        }
        aide_lite.write_quality_outputs(root, ledger)
        index = json.loads((root / aide_lite.FILE_QUALITY_LEDGER_JSON_PATH).read_text(encoding="utf-8"))
        self.assertEqual(index["record_storage"], "sharded")
        shard_names = [Path(item["path"]).name for item in index["record_shards"]]
        self.assertEqual(shard_names, [f"file-quality-ledger-{i:04d}.json" for i in range(1, len(shard_names) + 1)])
        hydrated = aide_lite.latest_or_missing_quality_ledger(root)
        self.assertIsNotNone(hydrated)
        assert hydrated is not None
        self.assertEqual(len(hydrated["records"]), len(records))


if __name__ == "__main__":
    unittest.main()
