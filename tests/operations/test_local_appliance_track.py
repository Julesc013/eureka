from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from scripts.local_queue_progress import current_recommended_task, is_later_control_or_handoff


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_local_appliance_track.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_local_appliance_track", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class LocalApplianceTrackTests(unittest.TestCase):
    def test_queue_points_to_local_track_successor(self) -> None:
        text = (ROOT / ".aide/queue/index.yaml").read_text(encoding="utf-8")
        current = current_recommended_task(ROOT)
        self.assertTrue(
            "current_recommended_task: LOCAL-01" in text
            or "current_recommended_task: LOCAL-02" in text
            or is_later_control_or_handoff(current),
            text,
        )
        if "current_recommended_task: LOCAL-02" in text:
            self.assertIn("id: LOCAL-01", text)
            self.assertIn("status: completed", text)

    def test_queue_helper_accepts_historical_validator_repair_successor(self) -> None:
        self.assertTrue(is_later_control_or_handoff("HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-03"))

    def test_queue_helper_accepts_external_artifact_wait_state(self) -> None:
        self.assertTrue(is_later_control_or_handoff("WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE"))

    def test_f0_deferred_until_local_14(self) -> None:
        payload = load_json("control/inventory/f0_deferral_for_local_appliance.json")
        self.assertEqual("LOCAL-14", payload["deferred_until"])
        self.assertEqual("deferred", payload["f0_current_status"])

    def test_localhost_default_true(self) -> None:
        payload = load_json("control/policies/local_appliance_policy.json")
        self.assertIs(payload["localhost_default"], True)

    def test_lan_disabled_by_default(self) -> None:
        appliance = load_json("control/policies/local_appliance_policy.json")
        network = load_json("control/policies/local_network_safety_policy.json")
        report = load_json("control/audits/local-00-local-appliance-track-v0/local_00_report.json")
        self.assertIs(appliance["lan_binding_default"], False)
        self.assertIs(network["lan_binding_default"], False)
        self.assertIs(report["lan_enabled"], False)

    def test_read_only_default_true(self) -> None:
        appliance = load_json("control/policies/local_appliance_policy.json")
        network = load_json("control/policies/local_network_safety_policy.json")
        self.assertIs(appliance["read_only_default"], True)
        self.assertIs(network["read_only_default"], True)

    def test_explicit_instance_path_required(self) -> None:
        payload = load_json("control/policies/local_appliance_policy.json")
        self.assertIs(payload["explicit_instance_path_required"], True)

    def test_hidden_local_state_roots_forbidden(self) -> None:
        payload = load_json("control/policies/local_appliance_policy.json")
        self.assertIs(payload["hidden_state_roots_forbidden"], True)

    def test_agent_policy_blocks_truth_acceptance(self) -> None:
        payload = load_json("control/policies/local_agent_workunit_policy.json")
        self.assertIs(payload["agents_may_accept_truth"], False)

    def test_agent_policy_blocks_direct_public_index_mutation(self) -> None:
        payload = load_json("control/policies/local_agent_workunit_policy.json")
        self.assertIs(payload["agents_may_mutate_public_index_directly"], False)

    def test_agent_policy_blocks_package_download_install_execute(self) -> None:
        payload = load_json("control/policies/local_agent_workunit_policy.json")
        self.assertIs(payload["agents_may_download_packages"], False)
        self.assertIs(payload["agents_may_install_packages"], False)
        self.assertIs(payload["agents_may_execute_packages"], False)

    def test_future_task_gate_rejects_scaffold_only_product_completion(self) -> None:
        payload = load_json("control/policies/future_task_behavior_gate_policy.json")
        self.assertIs(payload["scaffold_only_product_completion_allowed"], False)
        self.assertIs(payload["product_tasks_must_prove_runtime_behavior"], True)

    def test_proof_levels_are_defined(self) -> None:
        payload = load_json("control/policies/local_track_completion_policy.json")
        self.assertEqual("command/runtime proof", payload["proof_levels"]["L1"])
        self.assertEqual("local workbench proof", payload["proof_levels"]["L3"])
        self.assertEqual("L4", payload["required_task_levels"]["LOCAL-14"])

    def test_validator_passes(self) -> None:
        validator = load_validator()
        result = validator.validate(ROOT)
        self.assertEqual("pass", result["status"], result)


if __name__ == "__main__":
    unittest.main()
