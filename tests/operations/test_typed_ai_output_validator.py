from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "contracts" / "ai" / "typed_ai_output.v0.json"
REGISTRY = REPO_ROOT / "control" / "inventory" / "ai_providers" / "typed_output_examples.json"
EXAMPLE_PROVIDER = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0"
SCRIPT = REPO_ROOT / "scripts" / "validate_ai_output.py"
MODULE = REPO_ROOT / "runtime" / "engine" / "ai" / "typed_output_validator.py"
OPERATIONS_DOC = REPO_ROOT / "docs" / "operations" / "AI_OUTPUT_VALIDATION.md"
AI_DOC = REPO_ROOT / "docs" / "reference" / "AI_PROVIDER_CONTRACT.md"
OUTPUT_DOC = REPO_ROOT / "docs" / "reference" / "TYPED_AI_OUTPUT_CONTRACT.md"
EVIDENCE_DOC = REPO_ROOT / "docs" / "reference" / "EVIDENCE_PACK_CONTRACT.md"
CONTRIBUTION_DOC = REPO_ROOT / "docs" / "reference" / "CONTRIBUTION_PACK_CONTRACT.md"
MASTER_INDEX_DOC = REPO_ROOT / "docs" / "reference" / "MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md"


class TypedAIOutputValidatorOperationsTestCase(unittest.TestCase):
    def test_contract_registry_module_and_script_exist(self) -> None:
        schema = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(schema["x-contract_id"], "eureka_typed_ai_output_v0")
        self.assertEqual(schema["x-max_generated_text_chars"], 2000)
        self.assertFalse(schema["x-runtime_implemented"])
        self.assertIn("privacy_classification", schema["properties"])

        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["inventory_kind"], "eureka.typed_ai_output_examples")
        self.assertEqual(len(registry["examples"]), 4)
        self.assertTrue(SCRIPT.is_file())
        self.assertTrue(MODULE.is_file())

    def test_registered_examples_exist_and_are_valid_only(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for item in registry["examples"]:
            path = REPO_ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(item["expected_validation_status"], "pass")
            self.assertTrue(path.name.endswith(".valid.json"))
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(payload["required_review"])
            self.assertIn("canonical_truth", payload["prohibited_uses"])
            self.assertIn("rights_clearance", payload["prohibited_uses"])
            self.assertIn("malware_safety", payload["prohibited_uses"])
            self.assertIn("automatic_acceptance", payload["prohibited_uses"])
            self.assertFalse(payload["created_by_provider"]["runtime_call_performed"])

    def test_examples_have_no_invalid_fixtures_private_paths_or_secrets(self) -> None:
        for path in EXAMPLE_PROVIDER.rglob("*"):
            if path.is_file():
                self.assertFalse(path.name.endswith(".invalid.json"), path)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("sk-", text)
                self.assertNotRegex(text, r"[A-Za-z]:\\")

    def test_docs_record_validator_boundary_and_workflow_relationships(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (OPERATIONS_DOC, AI_DOC, OUTPUT_DOC, EVIDENCE_DOC, CONTRIBUTION_DOC, MASTER_INDEX_DOC)
        )
        compact = " ".join(combined.split())
        for phrase in (
            "validate_ai_output.py",
            "typed output validation",
            "does not implement model calls",
            "required review",
            "not canonical truth",
            "evidence packs",
            "contribution packs",
            "master index review queue",
            "does not enter evidence",
            "does not enter contribution",
            "does not mutate",
        ):
            self.assertIn(phrase, compact)


if __name__ == "__main__":
    unittest.main()
