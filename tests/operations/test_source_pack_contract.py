from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "contracts" / "packs" / "source_pack.v0.json"
EXAMPLE_PACK = REPO_ROOT / "examples" / "source_packs" / "minimal_recorded_source_pack_v0"
DOC = REPO_ROOT / "docs" / "reference" / "SOURCE_PACK_CONTRACT.md"
LIFECYCLE_DOC = REPO_ROOT / "docs" / "reference" / "PACK_LIFECYCLE.md"
AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "source-pack-contract-v0" / "source_pack_contract_report.json"


class SourcePackContractTestCase(unittest.TestCase):
    def test_schema_and_report_parse(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["x-contract_id"], "eureka_source_pack_v0")
        self.assertIn("runtime import", schema["x-non_goals"])

        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_contract_validation_example_only")
        self.assertFalse(report["validator"]["performs_import"])
        self.assertFalse(report["validator"]["performs_network"])

    def test_example_pack_required_files_and_manifest(self) -> None:
        for name in ("SOURCE_PACK.json", "README.md", "RIGHTS_AND_ACCESS.md", "CHECKSUMS.SHA256"):
            self.assertTrue((EXAMPLE_PACK / name).is_file(), name)

        manifest = json.loads((EXAMPLE_PACK / "SOURCE_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "source_pack.v0")
        self.assertEqual(manifest["status"], "shareable_candidate")
        self.assertEqual(manifest["privacy"]["classification"], "public_safe")
        self.assertFalse(manifest["capabilities"]["network_required"])
        self.assertFalse(manifest["capabilities"]["live_supported"])
        self.assertFalse(manifest["capabilities"]["import_implemented"])
        self.assertFalse(manifest["capabilities"]["indexing_implemented"])

    def test_checksums_validate(self) -> None:
        checksums = {}
        for line in (EXAMPLE_PACK / "CHECKSUMS.SHA256").read_text(encoding="utf-8").splitlines():
            digest, rel_path = line.split(None, 1)
            checksums[rel_path.strip()] = digest

        manifest = json.loads((EXAMPLE_PACK / "SOURCE_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(set(checksums), set(manifest["checksums"]["covers"]))
        for rel_path, expected in checksums.items():
            actual = hashlib.sha256((EXAMPLE_PACK / rel_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel_path)

    def test_jsonl_records_parse_and_stay_fixture_only(self) -> None:
        source_records = _read_jsonl(EXAMPLE_PACK / "source_records.jsonl")
        evidence_records = _read_jsonl(EXAMPLE_PACK / "evidence_records.jsonl")
        representation_records = _read_jsonl(EXAMPLE_PACK / "representation_records.jsonl")

        self.assertEqual(len(source_records), 1)
        self.assertEqual(len(evidence_records), 2)
        self.assertEqual(len(representation_records), 1)
        source = source_records[0]
        self.assertTrue(source["fixture_backed"])
        self.assertFalse(source["live_supported"])
        self.assertFalse(source["network_required"])
        self.assertIn("No live connector", source["limitations"])

    def test_example_pack_has_no_executables_private_paths_or_live_urls(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".iso", ".zip"}
        for path in EXAMPLE_PACK.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, path)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertNotRegex(text, r"[A-Za-z]:\\")

    def test_docs_record_contract_only_boundaries(self) -> None:
        text = DOC.read_text(encoding="utf-8").lower()
        compact = " ".join(text.split())
        for phrase in (
            "does not implement source pack import, local indexing, uploads",
            "master-index acceptance",
            "evidence packs",
            "index packs",
            "contribution packs",
            "not an ai prompt",
        ):
            self.assertIn(phrase, compact)
        self.assertTrue(LIFECYCLE_DOC.is_file())


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
