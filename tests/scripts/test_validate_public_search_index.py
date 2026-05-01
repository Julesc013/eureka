from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_public_search_index.py"
INDEX_ROOT = REPO_ROOT / "data" / "public_index"


class ValidatePublicSearchIndexScriptTest(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])
        self.assertGreater(payload["document_count"], 0)
        self.assertFalse(payload["private_paths_detected"])

    def test_documents_have_required_public_safe_fields(self) -> None:
        docs = [
            json.loads(line)
            for line in (INDEX_ROOT / "search_documents.ndjson").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertGreater(len(docs), 0)
        doc_ids = [doc["doc_id"] for doc in docs]
        self.assertEqual(len(doc_ids), len(set(doc_ids)))
        sample = docs[0]
        for field_name in (
            "doc_id",
            "record_id",
            "record_kind",
            "title",
            "source_id",
            "evidence_summary",
            "compatibility_summary",
            "blocked_actions",
            "limitations",
            "search_text",
        ):
            self.assertIn(field_name, sample)
        for doc in docs:
            self.assertTrue({"download", "upload", "install_handoff", "execute"}.issubset(set(doc["blocked_actions"])))
            self.assertFalse(doc["live_source_used"])
            self.assertFalse(doc["external_call_performed"])


if __name__ == "__main__":
    unittest.main()
