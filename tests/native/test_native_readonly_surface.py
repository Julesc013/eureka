import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeReadOnlySurfaceTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_readonly_surface_contract_has_required_views(self) -> None:
        contract = self.load_json("contracts/native/native_readonly_surface.v0.json")
        view_enum = contract["properties"]["supported_views"]["items"]["enum"]
        for view in (
            "search_results",
            "object_summary",
            "source_summary",
            "relay_status",
            "action_manifest",
            "blocked_action",
            "diagnostics",
        ):
            self.assertIn(view, view_enum)

    def test_first_wave_boundary_policy_is_read_only(self) -> None:
        policy = self.load_json("control/inventory/native/native_first_wave_boundary_policy.json")
        self.assertIs(policy["win32_readonly"], True)
        self.assertIs(policy["appkit_readonly"], True)
        self.assertIs(policy["carbon_readonly"], True)
        for key in (
            "live_source_access_allowed",
            "download_allowed",
            "install_allowed",
            "execute_allowed",
            "emulate_allowed",
            "account_auth_allowed",
            "telemetry_allowed",
            "public_index_mutation_allowed",
            "master_index_mutation_allowed",
            "python_runtime_internal_dependency_allowed",
            "connector_runtime_dependency_allowed",
            "accepted_truth_creation_allowed",
        ):
            self.assertIs(policy[key], False, key)

    def test_manual_smoke_checklist_sample_covers_required_checks(self) -> None:
        policy = self.load_json("control/inventory/native/native_smoke_checklist_policy.json")
        sample = self.load_json(
            "control/audits/c-bundle-02-native-first-wave-skeletons-v0/generated/sample_native_smoke_checklist.json"
        )
        sample_checks = {check["check_id"] for check in sample["checks"]}
        self.assertTrue(set(policy["required_checks"]).issubset(sample_checks), sample_checks)
        self.assertEqual(sample["pass_fail_unknown"], "manual_future")

    def test_build_evidence_sample_does_not_claim_build_or_release_artifacts(self) -> None:
        sample = self.load_json(
            "control/audits/c-bundle-02-native-first-wave-skeletons-v0/generated/sample_native_build_evidence_plan.json"
        )
        self.assertIs(sample["build_attempted"], False)
        self.assertEqual(sample["build_status"], "manual_build_required")
        self.assertEqual(sample["artifact_refs"], [])
        for value in sample["truth_boundary"].values():
            self.assertIs(value, False)
        for key in ("enabled_live_access", "enabled_downloads", "enabled_installers", "enabled_execution", "enabled_accounts", "enabled_telemetry"):
            self.assertIs(sample["product_boundary"][key], False, key)


if __name__ == "__main__":
    unittest.main()
