import copy
import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts/validate_source_os_foundation.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_source_os_foundation", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def load_json(rel):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def load_payloads():
    return {
        rel: load_json(rel)
        for rel in validator.CONTRACTS + validator.INVENTORIES + validator.EXAMPLES
    }


class SourceOSFoundationContractsTest(unittest.TestCase):
    def test_validator_passes_current_repo(self):
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_registry_example_validates(self):
        payloads = load_payloads()
        errors = []
        validator.validate_examples(REPO_ROOT, payloads, errors)
        self.assertEqual(errors, [])

    def test_named_source_record_examples_validate(self):
        for rel in (
            "examples/sources/source_records/internet_archive_source_v2.json",
            "examples/sources/source_records/wayback_source_v2.json",
            "examples/sources/source_records/github_releases_source_v2.json",
            "examples/sources/source_records/pypi_source_v2.json",
            "examples/sources/source_records/npm_source_v2.json",
            "examples/sources/source_records/software_heritage_source_v2.json",
            "examples/sources/source_records/retro_community_source_example_v2.json",
            "examples/sources/source_records/policy_blocked_source_example_v2.json",
        ):
            with self.subTest(rel=rel):
                record = load_json(rel)
                self.assertEqual(record["schema_version"], "source_record.v2")
                self.assertFalse(record["truth_boundary"]["source_record_grants_live_access"])
                self.assertFalse(record["product_boundary"]["enabled_source_sync"])

    def test_unknown_source_family_fails(self):
        payloads = load_payloads()
        target = "examples/sources/source_records/internet_archive_source_v2.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["source_family"] = "unknown_family"
        errors = []
        validator.validate_examples(REPO_ROOT, payloads, errors)
        self.assertTrue(any("unknown source_family" in error for error in errors), errors)

    def test_unknown_trust_lane_fails(self):
        payloads = load_payloads()
        target = "examples/sources/source_records/internet_archive_source_v2.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["trust_lane"] = "not_a_lane"
        errors = []
        validator.validate_examples(REPO_ROOT, payloads, errors)
        self.assertTrue(any("unknown trust_lane" in error for error in errors), errors)

    def test_unknown_index_depth_fails(self):
        payloads = load_payloads()
        target = "examples/sources/source_records/internet_archive_source_v2.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["index_depth_current"] = "D9_everything"
        errors = []
        validator.validate_examples(REPO_ROOT, payloads, errors)
        self.assertTrue(any("unknown index_depth_current" in error for error in errors), errors)

    def test_unknown_capability_fails(self):
        payloads = load_payloads()
        target = "examples/sources/source_records/internet_archive_source_v2.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["capability_refs"] = ["source_known", "permission_granting_magic"]
        errors = []
        validator.validate_examples(REPO_ROOT, payloads, errors)
        self.assertTrue(any("unknown capability" in error for error in errors), errors)

    def test_source_capability_enabling_permission_fails(self):
        payloads = load_payloads()
        payloads["control/inventory/sources/source_capability_ladder.json"] = copy.deepcopy(
            payloads["control/inventory/sources/source_capability_ladder.json"]
        )
        payloads["control/inventory/sources/source_capability_ladder.json"]["capabilities"][0]["permission_granted"] = True
        errors = []
        validator.validate_inventories(payloads, errors)
        self.assertTrue(any("capability grants permission" in error for error in errors), errors)

    def test_live_access_enabled_without_approval_fails(self):
        payloads = load_payloads()
        target = "examples/sources/source_records/internet_archive_source_v2.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["truth_boundary"]["source_record_grants_live_access"] = True
        errors = []
        validator.validate_examples(REPO_ROOT, payloads, errors)
        self.assertTrue(any("source_record_grants_live_access" in error for error in errors), errors)

    def test_forbidden_operation_allowed_by_default_fails(self):
        payloads = load_payloads()
        target = "control/inventory/sources/source_operation_policy.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["allowed_operations_current"].append("download_binary")
        errors = []
        validator.validate_inventories(payloads, errors)
        self.assertTrue(any("forbidden operations allowed" in error for error in errors), errors)

    def test_rights_malware_installability_claims_fail(self):
        for key in (
            "source_record_can_claim_rights_clearance",
            "source_record_can_claim_malware_safety",
            "source_record_can_claim_verified_installability",
        ):
            with self.subTest(key=key):
                payloads = load_payloads()
                target = "examples/sources/source_records/internet_archive_source_v2.json"
                payloads[target] = copy.deepcopy(payloads[target])
                payloads[target]["truth_boundary"][key] = True
                errors = []
                validator.validate_examples(REPO_ROOT, payloads, errors)
                self.assertTrue(any(key in error for error in errors), errors)

    def test_public_and_master_index_mutation_claims_fail(self):
        for key in ("mutated_public_index", "mutated_master_index"):
            with self.subTest(key=key):
                payloads = load_payloads()
                target = "examples/sources/source_records/internet_archive_source_v2.json"
                payloads[target] = copy.deepcopy(payloads[target])
                payloads[target]["product_boundary"][key] = True
                errors = []
                validator.validate_examples(REPO_ROOT, payloads, errors)
                self.assertTrue(any(key in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
