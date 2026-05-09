import json
import unittest
from pathlib import Path

from scripts.validate_native_packaging_manifests import CHECKS, build_smoke_evidence_packet, detect_forbidden_claims

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeSmokeEvidenceTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_smoke_evidence_packet_builds(self) -> None:
        packet = build_smoke_evidence_packet("win.winforms")
        self.assertEqual(packet["schema_version"], "native_smoke_evidence_packet.v0")
        self.assertEqual(packet["smoke_status"], "checklist_only")
        self.assertIs(packet["no_download_install_execute_verified"], True)
        self.assertFalse(detect_forbidden_claims(packet), packet)

    def test_smoke_evidence_examples_cover_required_checks(self) -> None:
        packet = self.load_json("examples/native/smoke/winforms_smoke_evidence_packet_v0.json")
        check_ids = {check["check_id"] for check in packet["checks"]}
        self.assertTrue(set(CHECKS).issubset(check_ids), check_ids)

    def test_toolchain_unavailable_build_log_record_validates(self) -> None:
        record = self.load_json("examples/native/build_logs/toolchain_unavailable_build_log_record_v0.json")
        self.assertEqual(record["build_status"], "skipped_toolchain_unavailable")
        self.assertIs(record["build_attempted"], False)
        self.assertEqual(record["produced_artifact_refs"], [])

    def test_manual_required_build_log_records_validate(self) -> None:
        for relative in (
            "examples/native/build_logs/win32_manual_build_log_record_v0.json",
            "examples/native/build_logs/appkit_manual_build_log_record_v0.json",
            "examples/native/build_logs/carbon_manual_build_log_record_v0.json",
        ):
            record = self.load_json(relative)
            self.assertEqual(record["build_status"], "manual_required")
            self.assertIs(record["build_attempted"], False)
            self.assertEqual(record["produced_artifact_refs"], [])

    def test_forbidden_download_install_execute_claims_are_rejected(self) -> None:
        payload = {
            "enabled_downloads": True,
            "enabled_installers": True,
            "enabled_execution": True,
        }
        errors = detect_forbidden_claims(payload)
        self.assertEqual(len(errors), 3)

    def test_forbidden_rights_malware_installability_claims_are_rejected(self) -> None:
        payload = {
            "rights_clearance_claimed": True,
            "malware_safety_claimed": True,
            "verified_installability_claimed": True,
        }
        errors = detect_forbidden_claims(payload)
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
