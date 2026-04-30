from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "pack-import-planning-v0"
REPORT = AUDIT_ROOT / "pack_import_planning_report.json"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_PLANNING.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md"


class PackImportPlanningTestCase(unittest.TestCase):
    def test_audit_pack_exists_and_report_parses(self) -> None:
        required = [
            "README.md",
            "IMPORT_SCOPE.md",
            "IMPORT_MODES.md",
            "STAGING_MODEL.md",
            "VALIDATION_PIPELINE.md",
            "PRIVACY_RIGHTS_RISK_REVIEW.md",
            "PROVENANCE_AND_CLAIM_MODEL.md",
            "LOCAL_SEARCH_AND_INDEX_INTERACTION.md",
            "MASTER_INDEX_REVIEW_INTERACTION.md",
            "IMPLEMENTATION_BOUNDARIES.md",
            "FUTURE_IMPLEMENTATION_SEQUENCE.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "pack_import_planning_report.json",
        ]
        for name in required:
            self.assertTrue((AUDIT_ROOT / name).exists(), name)
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "planning_only")
        self.assertFalse(payload["import_runtime_implemented"])

    def test_report_declares_validate_only_and_supported_pack_types(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["default_future_mode"], "validate_only")
        self.assertEqual(payload["next_future_mode"], "stage_local_quarantine")
        self.assertEqual(
            set(payload["supported_pack_types"]),
            {"source_pack", "evidence_pack", "index_pack", "contribution_pack"},
        )
        for behavior in [
            "arbitrary_directory_scan",
            "live_fetch",
            "canonical_registry_merge",
            "hosted_master_index_mutation",
            "raw_db_import",
            "executable_plugin_loading",
        ]:
            self.assertIn(behavior, payload["prohibited_import_behaviors"])

    def test_pipeline_references_pack_validators(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        commands = set(payload["validation_pipeline"]["validator_commands"])
        for command in [
            "python scripts/validate_source_pack.py",
            "python scripts/validate_evidence_pack.py",
            "python scripts/validate_index_pack.py",
            "python scripts/validate_contribution_pack.py",
            "python scripts/validate_master_index_review_queue.py",
        ]:
            self.assertIn(command, commands)

    def test_staging_and_search_boundaries_are_documented(self) -> None:
        staging = (AUDIT_ROOT / "STAGING_MODEL.md").read_text(encoding="utf-8").lower()
        self.assertIn(".eureka-local/staged_packs/", staging)
        self.assertIn("private by default", staging)
        self.assertIn("not committed", staging)
        self.assertIn("must not leak", staging)

        search = (AUDIT_ROOT / "LOCAL_SEARCH_AND_INDEX_INTERACTION.md").read_text(encoding="utf-8").lower()
        self.assertIn("no search impact by default", search)
        self.assertIn("no index impact by default", search)
        self.assertIn("local_index_only", search)

    def test_master_index_auto_acceptance_is_forbidden(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        master_index = payload["master_index_review_impact"]
        self.assertFalse(master_index["automatic_acceptance"])
        self.assertFalse(master_index["hosted_master_index_mutation"])
        text = (AUDIT_ROOT / "MASTER_INDEX_REVIEW_INTERACTION.md").read_text(encoding="utf-8").lower()
        self.assertIn("no automatic acceptance", text)
        self.assertIn("never writes the hosted/master index", text)

    def test_docs_state_no_import_runtime(self) -> None:
        combined = (
            REFERENCE_DOC.read_text(encoding="utf-8")
            + "\n"
            + ARCHITECTURE_DOC.read_text(encoding="utf-8")
        ).lower()
        for phrase in [
            "planning only",
            "does not implement import",
            "validate_only",
            "no search impact by default",
            "import never creates automatic acceptance",
        ]:
            self.assertIn(phrase, combined)
        for forbidden in [
            "pack import runtime is implemented",
            "imported packs affect public search",
            "imported packs are accepted by the master index",
        ]:
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
