import json
import unittest
from pathlib import Path

from scripts.validate_native_packaging_manifests import LANES, build_track_c_integration_audit, detect_forbidden_claims

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeTrackCIntegrationTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_track_c_audit_returns_exit_gate(self) -> None:
        audit = build_track_c_integration_audit()
        self.assertEqual(audit["track_c_exit_gate"], "PASS")
        self.assertEqual(audit["next_phase_recommendation"], "READY_FOR_E_BUNDLE_01")
        self.assertEqual(set(audit["audited_lanes"]), set(LANES))

    def test_integration_audit_example_matches_required_lanes(self) -> None:
        audit = self.load_json("examples/native/integration/first_wave_integration_audit_v0.json")
        self.assertEqual(set(audit["audited_lanes"]), set(LANES))
        self.assertEqual(audit["boundary_status"], "pass")
        self.assertFalse(detect_forbidden_claims(audit), audit)

    def test_c_bundle_03_audit_report_recommends_e_bundle_01(self) -> None:
        report = self.load_json("control/audits/c-bundle-03-native-smoke-packaging-v0/c_bundle_03_report.json")
        self.assertEqual(report["track_c_exit_gate"], "PASS")
        self.assertEqual(report["next_phase_recommendation"], "READY_FOR_E_BUNDLE_01")
        self.assertIs(report["native_scope"]["release_binaries_committed"], False)
        self.assertIs(report["native_scope"]["build_outputs_committed"], False)

    def test_public_and_master_index_mutation_claims_are_rejected(self) -> None:
        payload = {
            "mutated_public_index": True,
            "mutated_master_index": True,
            "public_index_mutation_allowed": True,
            "master_index_mutation_allowed": True,
        }
        errors = detect_forbidden_claims(payload)
        self.assertEqual(len(errors), 4)


if __name__ == "__main__":
    unittest.main()
