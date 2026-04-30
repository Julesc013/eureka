from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = REPO_ROOT / "contracts" / "ai"
INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "ai_providers"
EXAMPLE_PROVIDER = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0"
AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "ai-provider-contract-v0" / "ai_provider_contract_report.json"
AI_DOC = REPO_ROOT / "docs" / "reference" / "AI_PROVIDER_CONTRACT.md"
OUTPUT_DOC = REPO_ROOT / "docs" / "reference" / "TYPED_AI_OUTPUT_CONTRACT.md"
BOUNDARY_DOC = REPO_ROOT / "docs" / "architecture" / "AI_ASSISTANCE_BOUNDARY.md"
PUBLIC_SEARCH_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md"
CONTRIBUTION_DOC = REPO_ROOT / "docs" / "reference" / "CONTRIBUTION_PACK_CONTRACT.md"
MASTER_INDEX_DOC = REPO_ROOT / "docs" / "reference" / "MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md"


class AIProviderContractTestCase(unittest.TestCase):
    def test_schemas_inventory_and_report_parse(self) -> None:
        provider_schema = json.loads((CONTRACT_DIR / "ai_provider_manifest.v0.json").read_text(encoding="utf-8"))
        output_schema = json.loads((CONTRACT_DIR / "typed_ai_output.v0.json").read_text(encoding="utf-8"))
        request_schema = json.loads((CONTRACT_DIR / "ai_task_request.v0.json").read_text(encoding="utf-8"))
        self.assertEqual(provider_schema["x-contract_id"], "eureka_ai_provider_manifest_v0")
        self.assertFalse(provider_schema["x-runtime_implemented"])
        self.assertFalse(provider_schema["x-model_calls_implemented"])
        self.assertTrue(output_schema["x-required_review"])
        self.assertFalse(output_schema["x-runtime_implemented"])
        self.assertTrue(request_schema["x-no_silent_private_data_transfer"])

        policy = json.loads((INVENTORY_DIR / "ai_provider_policy.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["status"], "contract_only")
        self.assertTrue(policy["no_runtime_implemented"])
        self.assertTrue(policy["no_model_calls_implemented"])
        self.assertFalse(policy["default_enabled"])
        self.assertTrue(policy["remote_providers_disabled_by_default"])
        self.assertTrue(policy["private_data_disabled_by_default"])
        self.assertTrue(policy["telemetry_disabled_by_default"])
        self.assertTrue(policy["no_truth_authority"])
        self.assertTrue(policy["no_rights_clearance"])
        self.assertTrue(policy["no_malware_safety"])
        self.assertTrue(policy["no_auto_acceptance"])

        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_contract_validation_example_only")
        self.assertFalse(report["validator"]["performs_model_calls"])
        self.assertFalse(report["validator"]["performs_runtime_provider_loading"])
        self.assertFalse(report["validator"]["performs_public_search_ai"])
        self.assertFalse(report["validator"]["stores_credentials"])
        self.assertEqual(report["next_recommended_milestone"], "Typed AI Output Validator v0")

    def test_example_provider_manifest_and_checksums(self) -> None:
        for rel_path in (
            "AI_PROVIDER.json",
            "README.md",
            "PRIVACY_AND_SAFETY.md",
            "CHECKSUMS.SHA256",
            "examples/typed_output_alias_candidate.json",
            "examples/typed_output_explanation_draft.json",
        ):
            self.assertTrue((EXAMPLE_PROVIDER / rel_path).is_file(), rel_path)

        manifest = json.loads((EXAMPLE_PROVIDER / "AI_PROVIDER.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "ai_provider_manifest.v0")
        self.assertEqual(manifest["provider_type"], "disabled_stub")
        self.assertFalse(manifest["default_enabled"])
        self.assertFalse(manifest["network_required"])
        self.assertFalse(manifest["credential_required"])
        self.assertFalse(manifest["local_filesystem_required"])
        self.assertFalse(manifest["privacy_policy"]["private_data_allowed_by_default"])
        self.assertFalse(manifest["logging_policy"]["telemetry_enabled_by_default"])
        self.assertFalse(manifest["logging_policy"]["prompt_logging_enabled_by_default"])
        self.assertFalse(manifest["output_policy"]["canonical_truth_allowed"])
        self.assertFalse(manifest["output_policy"]["rights_clearance_allowed"])
        self.assertFalse(manifest["output_policy"]["malware_safety_allowed"])
        self.assertFalse(manifest["output_policy"]["automatic_acceptance_allowed"])

        checksums = {}
        for line in (EXAMPLE_PROVIDER / "CHECKSUMS.SHA256").read_text(encoding="utf-8").splitlines():
            digest, rel_path = line.split(None, 1)
            checksums[rel_path.strip()] = digest
        for rel_path, expected in checksums.items():
            actual = hashlib.sha256((EXAMPLE_PROVIDER / rel_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel_path)

    def test_typed_outputs_require_review_and_forbid_authority(self) -> None:
        outputs = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((EXAMPLE_PROVIDER / "examples").glob("*.json"))
        ]
        self.assertEqual(len(outputs), 2)
        output_types = {item["output_type"] for item in outputs}
        self.assertIn("alias_candidate", output_types)
        self.assertIn("explanation_draft", output_types)
        for item in outputs:
            self.assertTrue(item["required_review"])
            self.assertFalse(item["created_by_provider"]["runtime_call_performed"])
            self.assertIn("canonical_truth", item["prohibited_uses"])
            self.assertIn("rights_clearance", item["prohibited_uses"])
            self.assertIn("malware_safety", item["prohibited_uses"])
            self.assertIn("automatic_acceptance", item["prohibited_uses"])
            for claim in item.get("structured_claims", []):
                self.assertTrue(claim["review_required"])

    def test_remote_future_provider_is_disabled_and_credential_gated(self) -> None:
        examples = json.loads((INVENTORY_DIR / "example_ai_providers.json").read_text(encoding="utf-8"))
        remote = next(item for item in examples["providers"] if item["provider_type"] == "remote_api")
        self.assertFalse(remote["default_enabled"])
        self.assertTrue(remote["network_required"])
        self.assertTrue(remote["credential_required"])
        self.assertTrue(remote["explicit_operator_approval_required"])
        self.assertFalse(remote["runtime_implemented"])

    def test_examples_have_no_api_keys_private_paths_or_executables(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".iso", ".dll", ".ps1", ".sh"}
        for path in EXAMPLE_PROVIDER.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, path)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertNotRegex(text, r"[A-Za-z]:\\")
                self.assertNotRegex(text, r"sk-[A-Za-z0-9_-]{12,}")

    def test_docs_record_no_runtime_no_calls_and_relationships(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (AI_DOC, OUTPUT_DOC, BOUNDARY_DOC, PUBLIC_SEARCH_DOC, CONTRIBUTION_DOC, MASTER_INDEX_DOC)
        )
        compact = " ".join(combined.split())
        for phrase in (
            "disabled by default",
            "does not implement model calls",
            "does not enable ai in public search",
            "not canonical truth",
            "rights clearance",
            "malware safety",
            "automatic acceptance",
            "source packs",
            "evidence packs",
            "index packs",
            "contribution",
            "master index review queue",
            "aide/codex",
        ):
            self.assertIn(phrase, compact)


if __name__ == "__main__":
    unittest.main()
