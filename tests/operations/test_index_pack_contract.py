from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "contracts" / "packs" / "index_pack.v0.json"
EXAMPLE_PACK = REPO_ROOT / "examples" / "index_packs" / "minimal_index_pack_v0"
DOC = REPO_ROOT / "docs" / "reference" / "INDEX_PACK_CONTRACT.md"
SOURCE_DOC = REPO_ROOT / "docs" / "reference" / "SOURCE_PACK_CONTRACT.md"
EVIDENCE_DOC = REPO_ROOT / "docs" / "reference" / "EVIDENCE_PACK_CONTRACT.md"
AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "index-pack-contract-v0" / "index_pack_contract_report.json"


class IndexPackContractTestCase(unittest.TestCase):
    def test_schema_and_report_parse(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["x-contract_id"], "eureka_index_pack_v0")
        self.assertIn("raw SQLite or cache export", schema["x-non_goals"])

        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_contract_validation_example_only")
        self.assertFalse(report["validator"]["performs_import"])
        self.assertFalse(report["validator"]["performs_merge"])
        self.assertFalse(report["validator"]["performs_network"])
        self.assertFalse(report["index_records_are_canonical_truth"])

    def test_example_pack_required_files_and_manifest(self) -> None:
        for name in (
            "INDEX_PACK.json",
            "README.md",
            "PRIVACY_AND_RIGHTS.md",
            "CHECKSUMS.SHA256",
            "index_summary.json",
            "source_coverage.json",
            "record_summaries.jsonl",
            "field_coverage.json",
            "query_examples.jsonl",
        ):
            self.assertTrue((EXAMPLE_PACK / name).is_file(), name)

        manifest = json.loads((EXAMPLE_PACK / "INDEX_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "index_pack.v0")
        self.assertEqual(manifest["status"], "shareable_candidate")
        self.assertEqual(manifest["index_mode"], "local_index_only")
        self.assertEqual(manifest["index_build"]["index_format"], "summary_only")
        self.assertFalse(manifest["index_build"]["database_included"])
        self.assertFalse(manifest["index_build"]["raw_cache_included"])
        self.assertFalse(manifest["privacy"]["contains_private_paths"])
        self.assertTrue(manifest["validation"]["no_import_performed"])
        self.assertTrue(manifest["validation"]["no_merge_performed"])
        self.assertTrue(manifest["validation"]["no_database_export_performed"])

    def test_checksums_validate(self) -> None:
        checksums = {}
        for line in (EXAMPLE_PACK / "CHECKSUMS.SHA256").read_text(encoding="utf-8").splitlines():
            digest, rel_path = line.split(None, 1)
            checksums[rel_path.strip()] = digest

        manifest = json.loads((EXAMPLE_PACK / "INDEX_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(set(checksums), set(manifest["checksum_policy"]["covers"]))
        for rel_path, expected in checksums.items():
            actual = hashlib.sha256((EXAMPLE_PACK / rel_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel_path)

    def test_index_summary_source_coverage_and_records_parse(self) -> None:
        index_summary = json.loads((EXAMPLE_PACK / "index_summary.json").read_text(encoding="utf-8"))
        source_coverage = json.loads((EXAMPLE_PACK / "source_coverage.json").read_text(encoding="utf-8"))
        records = _read_jsonl(EXAMPLE_PACK / "record_summaries.jsonl")

        self.assertEqual(index_summary["record_count"], 4)
        self.assertEqual(index_summary["source_count"], 2)
        self.assertEqual(len(source_coverage["sources"]), 2)
        self.assertEqual(len(records), 4)
        self.assertEqual(len({record["record_id"] for record in records}), len(records))
        self.assertTrue(all(record["public_safe"] for record in records))
        source_ids = {source["source_id"] for source in source_coverage["sources"]}
        self.assertTrue(all(record["source_id"] in source_ids for record in records))

    def test_example_pack_has_no_database_executables_private_paths_or_live_urls(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".iso", ".db", ".sqlite", ".sqlite3"}
        for path in EXAMPLE_PACK.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, path)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertNotRegex(text, r"[A-Za-z]:\\")

    def test_docs_record_contract_only_boundaries_and_relationships(self) -> None:
        text = DOC.read_text(encoding="utf-8").lower()
        compact = " ".join(text.split())
        for phrase in (
            "does not implement index pack import, merge, uploads",
            "raw sqlite export",
            "not canonical proof",
            "master-index acceptance",
            "source packs",
            "evidence packs",
            "contribution packs",
        ):
            self.assertIn(phrase, compact)

        source_text = SOURCE_DOC.read_text(encoding="utf-8").lower()
        evidence_text = EVIDENCE_DOC.read_text(encoding="utf-8").lower()
        self.assertIn("index pack", source_text)
        self.assertIn("index pack", evidence_text)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
