from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "contracts" / "packs" / "contribution_pack.v0.json"
EXAMPLE_PACK = REPO_ROOT / "examples" / "contribution_packs" / "minimal_contribution_pack_v0"
DOC = REPO_ROOT / "docs" / "reference" / "CONTRIBUTION_PACK_CONTRACT.md"
SOURCE_DOC = REPO_ROOT / "docs" / "reference" / "SOURCE_PACK_CONTRACT.md"
EVIDENCE_DOC = REPO_ROOT / "docs" / "reference" / "EVIDENCE_PACK_CONTRACT.md"
INDEX_DOC = REPO_ROOT / "docs" / "reference" / "INDEX_PACK_CONTRACT.md"
AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "contribution-pack-contract-v0" / "contribution_pack_contract_report.json"


class ContributionPackContractTestCase(unittest.TestCase):
    def test_schema_and_report_parse(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["x-contract_id"], "eureka_contribution_pack_v0")
        self.assertTrue(schema["x-contribution_items_are_review_candidates"])
        self.assertIn("automatic acceptance", schema["x-non_goals"])

        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_contract_validation_example_only")
        self.assertFalse(report["validator"]["performs_upload"])
        self.assertFalse(report["validator"]["performs_import"])
        self.assertFalse(report["validator"]["performs_review_queue_runtime"])
        self.assertFalse(report["validator"]["performs_network"])
        self.assertFalse(report["contributions_are_canonical_truth"])

    def test_example_pack_required_files_and_manifest(self) -> None:
        for name in (
            "CONTRIBUTION_PACK.json",
            "README.md",
            "PRIVACY_AND_RIGHTS.md",
            "CHECKSUMS.SHA256",
            "contribution_items.jsonl",
            "source_pack_refs.jsonl",
            "evidence_pack_refs.jsonl",
            "manual_observations.jsonl",
            "alias_suggestions.jsonl",
            "absence_reports.jsonl",
        ):
            self.assertTrue((EXAMPLE_PACK / name).is_file(), name)

        manifest = json.loads((EXAMPLE_PACK / "CONTRIBUTION_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "contribution_pack.v0")
        self.assertEqual(manifest["status"], "shareable_candidate")
        self.assertEqual(manifest["contribution_scope"]["mutation_authority"], "review_candidate_only")
        self.assertFalse(manifest["referenced_packs"]["embedded_packs"])
        self.assertFalse(manifest["privacy"]["contains_private_paths"])
        self.assertFalse(manifest["privacy"]["contains_executables"])
        self.assertTrue(manifest["rights_and_access"]["not_canonical_truth"])
        self.assertTrue(manifest["review_requirements"]["no_automatic_acceptance"])
        self.assertFalse(manifest["review_requirements"]["review_queue_runtime_implemented"])

    def test_checksums_validate(self) -> None:
        checksums = {}
        for line in (EXAMPLE_PACK / "CHECKSUMS.SHA256").read_text(encoding="utf-8").splitlines():
            digest, rel_path = line.split(None, 1)
            checksums[rel_path.strip()] = digest

        manifest = json.loads((EXAMPLE_PACK / "CONTRIBUTION_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(set(checksums), set(manifest["checksum_policy"]["covers"]))
        for rel_path, expected in checksums.items():
            actual = hashlib.sha256((EXAMPLE_PACK / rel_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel_path)

    def test_contribution_items_and_references_parse(self) -> None:
        items = _read_jsonl(EXAMPLE_PACK / "contribution_items.jsonl")
        self.assertEqual(len(items), 3)
        self.assertEqual(len({item["contribution_id"] for item in items}), len(items))
        types = {item["contribution_type"] for item in items}
        self.assertIn("compatibility_suggestion", types)
        self.assertIn("alias_suggestion", types)
        self.assertIn("absence_report", types)
        self.assertTrue(all(item["review_status"] == "review_required" for item in items))

        source_refs = _read_jsonl(EXAMPLE_PACK / "source_pack_refs.jsonl")
        evidence_refs = _read_jsonl(EXAMPLE_PACK / "evidence_pack_refs.jsonl")
        self.assertEqual(source_refs[0]["pack_type"], "source_pack")
        self.assertEqual(evidence_refs[0]["pack_type"], "evidence_pack")

        observations = _read_jsonl(EXAMPLE_PACK / "manual_observations.jsonl")
        self.assertEqual(observations[0]["observation_status"], "pending")

    def test_example_pack_has_no_database_executables_private_paths_or_live_urls(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".iso", ".db", ".sqlite", ".sqlite3"}
        for path in EXAMPLE_PACK.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, path)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertNotRegex(text, r"[A-Za-z]:\\")

    def test_docs_record_boundaries_and_relationships(self) -> None:
        text = DOC.read_text(encoding="utf-8").lower()
        compact = " ".join(text.split())
        for phrase in (
            "does not implement contribution upload",
            "source/evidence/index pack import",
            "master-index review queue runtime",
            "automatic acceptance",
            "review candidates, not truth",
            "source packs",
            "evidence packs",
            "index packs",
            "master index review queue",
        ):
            self.assertIn(phrase, compact)

        source_text = SOURCE_DOC.read_text(encoding="utf-8").lower()
        evidence_text = EVIDENCE_DOC.read_text(encoding="utf-8").lower()
        index_text = INDEX_DOC.read_text(encoding="utf-8").lower()
        self.assertIn("contribution pack", source_text)
        self.assertIn("contribution pack", evidence_text)
        self.assertIn("contribution pack", index_text)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
