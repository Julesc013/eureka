from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "contracts" / "packs" / "evidence_pack.v0.json"
EXAMPLE_PACK = REPO_ROOT / "examples" / "evidence_packs" / "minimal_evidence_pack_v0"
DOC = REPO_ROOT / "docs" / "reference" / "EVIDENCE_PACK_CONTRACT.md"
SOURCE_DOC = REPO_ROOT / "docs" / "reference" / "SOURCE_PACK_CONTRACT.md"
AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "evidence-pack-contract-v0" / "evidence_pack_contract_report.json"


class EvidencePackContractTestCase(unittest.TestCase):
    def test_schema_and_report_parse(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["x-contract_id"], "eureka_evidence_pack_v0")
        self.assertEqual(schema["x-snippet_max_chars"], 500)
        self.assertIn("canonical truth selection", schema["x-non_goals"])

        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_contract_validation_example_only")
        self.assertFalse(report["validator"]["performs_import"])
        self.assertFalse(report["validator"]["performs_network"])
        self.assertFalse(report["claims_are_canonical_truth"])

    def test_example_pack_required_files_and_manifest(self) -> None:
        for name in ("EVIDENCE_PACK.json", "README.md", "RIGHTS_AND_ACCESS.md", "CHECKSUMS.SHA256", "evidence_records.jsonl"):
            self.assertTrue((EXAMPLE_PACK / name).is_file(), name)

        manifest = json.loads((EXAMPLE_PACK / "EVIDENCE_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "evidence_pack.v0")
        self.assertEqual(manifest["status"], "shareable_candidate")
        self.assertEqual(manifest["privacy"]["classification"], "public_safe")
        self.assertFalse(manifest["privacy"]["contains_private_paths"])
        self.assertFalse(manifest["validation"]["no_network_performed"] is False)
        self.assertTrue(manifest["validation"]["no_import_performed"])
        self.assertTrue(manifest["validation"]["no_indexing_performed"])
        self.assertTrue(manifest["validation"]["no_upload_performed"])

    def test_checksums_validate(self) -> None:
        checksums = {}
        for line in (EXAMPLE_PACK / "CHECKSUMS.SHA256").read_text(encoding="utf-8").splitlines():
            digest, rel_path = line.split(None, 1)
            checksums[rel_path.strip()] = digest

        manifest = json.loads((EXAMPLE_PACK / "EVIDENCE_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(set(checksums), set(manifest["checksum_policy"]["covers"]))
        for rel_path, expected in checksums.items():
            actual = hashlib.sha256((EXAMPLE_PACK / rel_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel_path)

    def test_jsonl_records_parse_and_stay_claim_only(self) -> None:
        evidence_records = _read_jsonl(EXAMPLE_PACK / "evidence_records.jsonl")
        source_references = _read_jsonl(EXAMPLE_PACK / "source_references.jsonl")

        self.assertEqual(len(evidence_records), 4)
        self.assertEqual(len({record["evidence_id"] for record in evidence_records}), len(evidence_records))
        self.assertEqual(len(source_references), 1)
        self.assertTrue(all(record["privacy_classification"] == "public_safe" for record in evidence_records))
        self.assertTrue(all(len(record.get("snippet", "")) <= 500 for record in evidence_records))
        self.assertFalse(source_references[0]["network_required_to_verify"])

    def test_example_pack_has_no_executables_private_paths_or_live_urls(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".iso"}
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
            "does not implement evidence pack import, indexing, uploads",
            "not canonical truth",
            "master-index acceptance",
            "source packs",
            "index packs",
            "contribution packs",
        ):
            self.assertIn(phrase, compact)

        source_text = SOURCE_DOC.read_text(encoding="utf-8").lower()
        self.assertIn("evidence pack is claim and observation focused", source_text)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
