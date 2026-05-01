from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = REPO_ROOT / "contracts" / "packs" / "local_staging_manifest.v0.json"
EXAMPLE_ROOT = REPO_ROOT / "examples" / "local_staging_manifests" / "minimal_local_staging_manifest_v0"
EXAMPLE_MANIFEST = EXAMPLE_ROOT / "LOCAL_STAGING_MANIFEST.json"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_MANIFEST_FORMAT.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "architecture" / "LOCAL_QUARANTINE_STAGING_MODEL.md"
PATH_CONTRACT_DOC = REPO_ROOT / "docs" / "reference" / "STAGING_REPORT_PATH_CONTRACT.md"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "local-staging-manifest-format-v0"
AUDIT_REPORT = AUDIT_ROOT / "local_staging_manifest_format_report.json"


class LocalStagingManifestFormatOperationTestCase(unittest.TestCase):
    def test_schema_and_example_exist_and_parse(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        manifest = json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "EurekaLocalStagingManifestV0")
        self.assertEqual(manifest["schema_version"], "local_staging_manifest.v0")
        self.assertEqual(manifest["manifest_kind"], "local_staging_manifest")
        self.assertEqual(manifest["status"], "planned_example")

    def test_example_records_no_mutation_guarantees(self) -> None:
        manifest = json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))
        for field in [
            "public_search_mutated",
            "local_index_mutated",
            "canonical_source_registry_mutated",
            "runtime_state_mutated",
            "master_index_mutated",
            "upload_performed",
            "live_network_performed",
        ]:
            self.assertFalse(manifest[field])
            self.assertFalse(manifest["no_mutation_guarantees"][field])

    def test_staged_entities_are_candidates_and_counts_match(self) -> None:
        manifest = json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))
        entities = manifest["staged_entities"]
        self.assertEqual(manifest["counts"]["staged_pack_count"], len(manifest["staged_pack_refs"]))
        self.assertEqual(manifest["counts"]["staged_entity_count"], len(entities))
        for entity in entities:
            self.assertTrue(entity["entity_type"].startswith("staged_"))
            self.assertNotIn("accepted", entity["review_status"])
            self.assertNotIn("canonical", entity["summary"].lower())
            self.assertGreater(len(entity["provenance_refs"]), 0)

    def test_reset_delete_export_policy_is_present(self) -> None:
        policy = json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))["reset_delete_export_policy"]
        self.assertTrue(policy["delete_staged_pack_supported_future"])
        self.assertTrue(policy["clear_all_staged_state_supported_future"])
        self.assertTrue(policy["export_manifest_supported_future"])
        self.assertTrue(policy["export_public_safe_report_supported_future"])
        self.assertFalse(policy["export_private_data_default"])
        self.assertTrue(policy["irreversible_delete_requires_confirmation_future"])

    def test_example_contains_no_private_paths_or_secrets(self) -> None:
        text = EXAMPLE_MANIFEST.read_text(encoding="utf-8")
        for forbidden in ["C:\\Users\\", "/Users/", "/home/", "api_key", "private_key", "password"]:
            self.assertNotIn(forbidden, text)
        self.assertNotIn("accepted_public", text)

    def test_audit_pack_records_contract_only_status(self) -> None:
        required = {
            "README.md",
            "MANIFEST_FORMAT_SUMMARY.md",
            "STAGED_PACK_REFERENCE_MODEL.md",
            "STAGED_ENTITY_MODEL.md",
            "NO_MUTATION_GUARANTEES.md",
            "RESET_DELETE_EXPORT_POLICY.md",
            "PRIVACY_RIGHTS_RISK_POLICY.md",
            "EXAMPLE_MANIFEST_REVIEW.md",
            "FUTURE_STAGED_INSPECTOR_PATH.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "local_staging_manifest_format_report.json",
        }
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(required.issubset({path.name for path in AUDIT_ROOT.iterdir()}))
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "contract_only")
        self.assertFalse(report["staging_runtime_implemented"])
        self.assertEqual(report["next_recommended_milestone"], "Staged Pack Inspector v0")

    def test_docs_record_no_runtime_or_search_index_master_impact(self) -> None:
        for path in [REFERENCE_DOC, ARCHITECTURE_DOC, PATH_CONTRACT_DOC]:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("no staging runtime", text)
                self.assertIn("public search", text)
                self.assertIn("local index", text)
                self.assertIn("master index", text)
                self.assertIn("candidate", text)

    def test_no_runtime_local_state_directory_created(self) -> None:
        for root in [".eureka-local", ".eureka-cache", ".eureka-staging", ".eureka-reports"]:
            self.assertFalse((REPO_ROOT / root).exists())


if __name__ == "__main__":
    unittest.main()
