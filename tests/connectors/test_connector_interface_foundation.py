import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts/validate_connector_interface_foundation.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_connector_interface_foundation", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def load_json(rel):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def load_payloads():
    files = (
        validator.CONTRACTS
        + validator.INVENTORIES
        + validator.FAMILY_EXAMPLES
        + validator.FIXTURE_REPLAY_EXAMPLES
        + validator.LIVE_PROBE_EXAMPLES
        + validator.OUTPUT_ENVELOPE_EXAMPLES
        + ("control/audits/h0-bundle-02-connector-interface-replay-v0/h0_bundle_02_report.json",)
    )
    return {rel: load_json(rel) for rel in files}


class ConnectorInterfaceFoundationTest(unittest.TestCase):
    def test_validator_passes_current_repo(self):
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_connector_family_registry_validates(self):
        payloads = load_payloads()
        errors = []
        validator.validate_family_registry(payloads, errors)
        self.assertEqual(errors, [])

    def test_named_connector_family_examples_validate(self):
        for rel in validator.FAMILY_EXAMPLES:
            with self.subTest(rel=rel):
                errors = []
                validator.validate_family(load_json(rel), rel, errors)
                self.assertEqual(errors, [])

    def test_unknown_source_family_fails(self):
        family = copy.deepcopy(load_json("examples/connectors/core/families/api_json_connector_family_v0.json"))
        family["source_families_supported"] = ["not_a_source_family"]
        errors = []
        validator.validate_family(family, "mutated_family", errors)
        self.assertTrue(any("unknown source_family" in error for error in errors), errors)

    def test_capability_is_permission_true_fails(self):
        payloads = load_payloads()
        target = "control/inventory/connectors/connector_capability_policy.json"
        payloads[target] = copy.deepcopy(payloads[target])
        payloads[target]["capability_is_permission"] = True
        errors = []
        validator.validate_capability_and_policy(payloads, errors)
        self.assertTrue(any("capability_is_permission" in error for error in errors), errors)

    def test_live_access_without_approval_fails(self):
        family = copy.deepcopy(load_json("examples/connectors/core/families/api_json_connector_family_v0.json"))
        family["live_access_default"] = True
        errors = []
        validator.validate_family(family, "mutated_family", errors)
        self.assertTrue(any("live_access_default" in error for error in errors), errors)

    def test_forbidden_operation_allowed_by_default_fails(self):
        family = copy.deepcopy(load_json("examples/connectors/core/families/api_json_connector_family_v0.json"))
        family["allowed_default_operations"] = ["download_binary"]
        errors = []
        validator.validate_family(family, "mutated_family", errors)
        self.assertTrue(any("forbidden operations allowed" in error for error in errors), errors)

    def test_fixture_replay_runs_offline(self):
        from runtime.connectors.core.fixture_replay import run_fixture_replay

        result = run_fixture_replay(REPO_ROOT / "examples/connectors/internet_archive/fixtures/minimal_item_metadata.json", None, {})
        self.assertTrue(result["no_network_used"])
        self.assertTrue(result["no_live_source_used"])

    def test_fixture_replay_rejects_network_used_claim(self):
        from runtime.connectors.core.fixture_replay import run_fixture_replay

        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture.json"
            fixture.write_text(json.dumps({"network_used": True}), encoding="utf-8")
            with self.assertRaises(ValueError):
                run_fixture_replay(fixture, None, {})

    def test_live_probe_envelope_blocks_missing_approval(self):
        from runtime.connectors.core.live_probe_envelope import build_live_probe_request_envelope
        from runtime.connectors.core.policy_evaluator import evaluate_connector_policy

        request = load_json("examples/connectors/core/live_probe/policy_blocked_live_probe_request_v0.json")
        request["live_call_allowed"] = True
        with self.assertRaises(ValueError):
            build_live_probe_request_envelope(request, {})
        decision = evaluate_connector_policy({**request, "dry_run_only": False}, {})
        self.assertEqual(decision["decision"], "blocked_missing_approval")

    def test_output_envelope_rejects_accepted_truth(self):
        from runtime.connectors.core.output_envelope import validate_connector_output_envelope

        envelope = copy.deepcopy(load_json("examples/connectors/core/output_envelopes/minimal_connector_output_envelope_v0.json"))
        envelope["truth_boundary"]["accepted_source_truth"] = True
        with self.assertRaises(ValueError):
            validate_connector_output_envelope(envelope, {})

    def test_output_envelope_rejects_public_and_master_index_mutation(self):
        from runtime.connectors.core.output_envelope import validate_connector_output_envelope

        for key in ("mutated_public_index", "mutated_master_index"):
            with self.subTest(key=key):
                envelope = copy.deepcopy(load_json("examples/connectors/core/output_envelopes/minimal_connector_output_envelope_v0.json"))
                envelope["product_boundary"][key] = True
                with self.assertRaises(ValueError):
                    validate_connector_output_envelope(envelope, {})

    def test_output_envelope_rejects_download_execution_claim(self):
        from runtime.connectors.core.output_envelope import build_connector_output_envelope

        for output_type in ("downloaded_file", "executed_artifact"):
            with self.subTest(output_type=output_type):
                with self.assertRaises(ValueError):
                    build_connector_output_envelope({"output_type": output_type}, {})


if __name__ == "__main__":
    unittest.main()
