from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_user_hardware_details_return.py"
TEMPLATE = REPO_ROOT / "docs" / "reference" / "user_hardware_details_00" / "RETURN_TEMPLATE.json"


class ValidateUserHardwareDetailsReturnScriptTestCase(unittest.TestCase):
    def test_valid_complete_return_passes_strict_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "user_hardware_details_return.json"
            path.write_text(json.dumps(_valid_payload(), indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json", "--strict"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertTrue(report["sufficient_for_hardware_review"])
        self.assertFalse(report["truth_created"])
        self.assertFalse(report["network_performed"])
        self.assertFalse(report["mutation_performed"])

    def test_template_shape_is_valid_but_not_strictly_complete(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--return-file", str(TEMPLATE), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertFalse(report["sufficient_for_hardware_review"])
        self.assertTrue(report["warnings"])

    def test_missing_default_return_fails_cleanly(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("file is missing" in error for error in report["errors"]))

    def test_strict_mode_rejects_missing_device_id(self) -> None:
        payload = _valid_payload()
        payload["device_ids"]["pci_vendor_device_id"] = None
        payload["device_ids"]["observed_from"] = None
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing_device_id.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json", "--strict"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertFalse(report["sufficient_for_hardware_review"])
        self.assertTrue(any("device_id" in error for error in report["errors"]))

    def test_rejects_driver_recommendation_claim(self) -> None:
        payload = _valid_payload()
        payload["truth_boundary"]["driver_recommended"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "driver_claim.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("driver_recommended" in error for error in report["errors"]))

    def test_rejects_private_path_and_secret_like_field(self) -> None:
        payload = _valid_payload()
        payload["source_or_media_context"]["candidate_source_url_or_citation"] = r"C:\Users\Alice\Downloads\driver.zip"
        payload["source_or_media_context"]["license_key"] = "redacted"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "private_path.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--return-file", str(path), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("private or absolute local evidence paths" in error for error in report["errors"]))
        self.assertTrue(any("secret-like field names" in error for error in report["errors"]))


def _valid_payload() -> dict:
    return {
        "schema_version": "user_hardware_details_return.v0",
        "task_id": "USER-HARDWARE-DETAILS-00",
        "query_id": "hq_driver_win98",
        "submitted_at": "2026-06-11T00:00:00Z",
        "submitted_by": "user",
        "device_identity": {
            "hardware_vendor": "Creative",
            "hardware_model": "Sound Blaster 16",
            "chipset": "CT1740",
            "board_revision": "example revision",
            "fcc_id_or_label": "example label",
            "product_label_text": "example product label"
        },
        "device_ids": {
            "pci_vendor_device_id": "ISA device; no PCI ID",
            "isa_pnp_id": "CTL0042",
            "usb_vid_pid": None,
            "pcmcia_cardbus_id": None,
            "other_device_id": None,
            "observed_from": "Device Manager details tab"
        },
        "machine_context": {
            "machine_vendor": "Example",
            "machine_model": "Example 486",
            "motherboard_vendor": "Example board vendor",
            "motherboard_model": "Example board model",
            "bios": "Example BIOS",
            "bus_or_interface": "ISA"
        },
        "windows_context": {
            "windows_version": "Windows 98",
            "windows_98_edition": "Second Edition",
            "language_or_region": "en-US",
            "architecture": "x86",
            "service_pack_or_update_pack": "none"
        },
        "source_or_media_context": {
            "existing_driver_media": "original driver floppy present",
            "media_label": "example media label",
            "candidate_source_url_or_citation": "example vendor support citation",
            "previously_tried_driver": "none",
            "observed_error_messages": "none"
        },
        "attachments_or_observations": [
            {
                "kind": "label_note",
                "description": "board label observed and transcribed"
            }
        ],
        "redactions_applied": [
            "serial numbers removed"
        ],
        "truth_boundary": {
            "driver_recommended": False,
            "reviewed_artifact_record_created": False,
            "verified_artifact_created": False,
            "download_or_execution_performed": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False
        },
        "recommended_next_action": "review_hardware_details"
    }


if __name__ == "__main__":
    unittest.main()

