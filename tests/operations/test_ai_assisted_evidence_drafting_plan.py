from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY = REPO_ROOT / "control" / "inventory" / "ai_providers" / "ai_assisted_drafting_policy.json"
EXAMPLE_ROOT = REPO_ROOT / "examples" / "ai_assisted_drafting" / "minimal_drafting_flow_v0"
ARCH_DOC = REPO_ROOT / "docs" / "architecture" / "AI_ASSISTED_EVIDENCE_DRAFTING.md"
REF_DOC = REPO_ROOT / "docs" / "reference" / "AI_ASSISTED_DRAFTING_CONTRACT.md"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "ai-assisted-evidence-drafting-plan-v0"


class AIAssistedEvidenceDraftingPlanOperationsTestCase(unittest.TestCase):
    def test_policy_exists_and_records_disabled_defaults(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["status"], "planning_only")
        self.assertFalse(policy["drafting_runtime_implemented"])
        self.assertFalse(policy["model_calls_implemented"])
        self.assertFalse(policy["default_enabled"])
        self.assertFalse(policy["remote_providers_enabled_by_default"])
        self.assertFalse(policy["private_data_allowed_by_default"])
        self.assertFalse(policy["telemetry_enabled_by_default"])
        self.assertTrue(policy["output_validation_required"])
        self.assertTrue(policy["required_review"])
        self.assertFalse(policy["evidence_acceptance_automatic"])
        self.assertFalse(policy["contribution_acceptance_automatic"])
        self.assertFalse(policy["master_index_acceptance_automatic"])

    def test_forbidden_tasks_cover_authority_and_external_actions(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        forbidden = set(policy["forbidden_drafting_tasks"])
        for task in [
            "decide_canonical_truth",
            "decide_rights_clearance",
            "decide_malware_safety",
            "decide_source_trust",
            "auto_accept_master_index",
            "auto_mutate_public_search",
            "auto_mutate_local_index",
            "fetch_arbitrary_url",
            "scrape_web",
            "process_private_data_remotely_by_default",
            "extract_credentials",
            "execute_installer",
            "download_artifact",
        ]:
            self.assertIn(task, forbidden)

    def test_example_flow_files_are_synthetic_candidate_only(self) -> None:
        required = {
            "README.md",
            "DRAFTING_FLOW.json",
            "INPUT_CONTEXT.example.json",
            "TYPED_AI_OUTPUT.example.json",
            "EVIDENCE_CANDIDATE.example.json",
            "CONTRIBUTION_CANDIDATE.example.json",
            "CHECKSUMS.SHA256",
        }
        self.assertTrue(required.issubset({path.name for path in EXAMPLE_ROOT.iterdir()}))
        flow = _load("DRAFTING_FLOW.json")
        evidence = _load("EVIDENCE_CANDIDATE.example.json")
        contribution = _load("CONTRIBUTION_CANDIDATE.example.json")
        typed = _load("TYPED_AI_OUTPUT.example.json")

        self.assertEqual(flow["status"], "synthetic_example")
        self.assertFalse(flow["model_call_performed"])
        self.assertFalse(flow["drafting_runtime_implemented"])
        self.assertTrue(flow["candidate_only"])
        self.assertTrue(typed["required_review"])
        self.assertFalse(typed["created_by_provider"]["runtime_call_performed"])

        self.assertEqual(evidence["review_status"], "review_required")
        self.assertTrue(evidence["candidate_only"])
        self.assertFalse(evidence["accepted_as_evidence"])
        self.assertFalse(evidence["automatic_acceptance"])

        self.assertEqual(contribution["review_status"], "review_required")
        self.assertTrue(contribution["candidate_only"])
        self.assertFalse(contribution["accepted_as_contribution"])
        self.assertFalse(contribution["automatic_acceptance"])
        self.assertFalse(contribution["master_index_acceptance"])

    def test_examples_have_no_private_paths_or_secret_values(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in EXAMPLE_ROOT.iterdir() if path.is_file())
        for forbidden in ["C:\\Users\\", "/Users/", "/home/", "sk-", "-----BEGIN"]:
            self.assertNotIn(forbidden, combined)

    def test_docs_say_no_runtime_model_calls_or_truth(self) -> None:
        combined = f"{ARCH_DOC.read_text(encoding='utf-8')}\n{REF_DOC.read_text(encoding='utf-8')}".lower()
        for phrase in [
            "ai-assisted evidence drafting",
            "does not implement ai runtime",
            "no model calls",
            "ai is an assistant, not authority",
            "not truth",
            "required review",
            "public search",
            "local index",
            "master index",
        ]:
            self.assertIn(phrase, combined)

    def test_audit_pack_placeholder_is_expected_to_exist_after_audit_commit(self) -> None:
        # The audit pack is added in the next P49 commit; this test becomes
        # active once the validator/audit slice lands.
        if AUDIT_ROOT.exists():
            report = json.loads((AUDIT_ROOT / "ai_assisted_evidence_drafting_plan_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "planning_only")
            self.assertFalse(report["model_calls_implemented"])


def _load(filename: str) -> dict:
    return json.loads((EXAMPLE_ROOT / filename).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
