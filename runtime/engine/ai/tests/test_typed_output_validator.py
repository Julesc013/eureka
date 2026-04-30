from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from runtime.engine.ai.typed_output_validator import (
    MAX_GENERATED_TEXT_CHARS,
    load_json,
    validate_ai_output_bundle,
    validate_provider_manifest,
    validate_typed_ai_output,
    validate_typed_ai_output_file,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_PROVIDER = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0" / "AI_PROVIDER.json"
EXAMPLES_DIR = EXAMPLE_PROVIDER.parent / "examples"


class TypedOutputValidatorModuleTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = load_json(EXAMPLE_PROVIDER)
        self.alias = load_json(EXAMPLES_DIR / "alias_candidate.valid.json")

    def test_valid_examples_pass_module_validation(self) -> None:
        self.assertEqual(validate_provider_manifest(self.provider), [])
        for path in sorted(EXAMPLES_DIR.glob("*.valid.json")):
            result = validate_typed_ai_output_file(path, provider_manifest=self.provider)
            self.assertTrue(result["ok"], result)

    def test_bundle_validation_checks_all_examples_without_side_effect_flags(self) -> None:
        report = validate_ai_output_bundle(EXAMPLE_PROVIDER.parent)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["passed"], 4)
        self.assertFalse(report["model_calls_performed"])
        self.assertFalse(report["network_performed"])
        self.assertFalse(report["mutation_performed"])
        self.assertFalse(report["import_performed"])

    def test_rejects_missing_required_review(self) -> None:
        output = copy.deepcopy(self.alias)
        output["required_review"] = False
        errors = validate_typed_ai_output(output, provider_manifest=self.provider)
        self.assertTrue(any("required_review must be true" in error for error in errors))

    def test_rejects_missing_prohibited_uses(self) -> None:
        output = copy.deepcopy(self.alias)
        output["prohibited_uses"] = ["canonical_truth"]
        errors = validate_typed_ai_output(output, provider_manifest=self.provider)
        self.assertTrue(any("prohibited_uses must include" in error for error in errors))

    def test_rejects_authority_claims(self) -> None:
        for field, value in (
            ("output_type", "rights_clearance_decision"),
            ("task_type", "malware_safety_decision"),
            ("status", "accepted_public"),
        ):
            output = copy.deepcopy(self.alias)
            output[field] = value
            errors = validate_typed_ai_output(output, provider_manifest=self.provider)
            self.assertTrue(errors, field)

    def test_rejects_secret_private_path_and_oversized_text(self) -> None:
        secret_output = copy.deepcopy(self.alias)
        secret_output["api_key"] = "sk-testsecretvalue000"
        self.assertTrue(validate_typed_ai_output(secret_output, provider_manifest=self.provider))

        path_output = copy.deepcopy(self.alias)
        path_output["generated_text"] = r"Review C:\\Users\\Example\\private\\cache.sqlite3"
        self.assertTrue(any("private" in error.lower() for error in validate_typed_ai_output(path_output, provider_manifest=self.provider)))

        long_output = copy.deepcopy(self.alias)
        long_output["generated_text"] = "x" * (MAX_GENERATED_TEXT_CHARS + 1)
        self.assertTrue(any("characters or fewer" in error for error in validate_typed_ai_output(long_output, provider_manifest=self.provider)))

    def test_rejects_enabled_provider_manifest(self) -> None:
        provider = copy.deepcopy(self.provider)
        provider["default_enabled"] = True
        errors = validate_provider_manifest(provider)
        self.assertTrue(any("default_enabled must be false" in error for error in errors))

    def test_serializable_errors_are_deterministic(self) -> None:
        output = copy.deepcopy(self.alias)
        output.pop("output_id")
        errors = validate_typed_ai_output(output, provider_manifest=self.provider)
        json.dumps(errors)
        self.assertTrue(any("output_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
