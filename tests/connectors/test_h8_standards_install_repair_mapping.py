from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.fixture_loader import load_h8_manuals_docs_fixture
from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards import rfc_editor_ietf, service_manual_schematic_archive, vendor_documentation_portal

REPO_ROOT = Path(__file__).resolve().parents[2]


class H8StandardsInstallRepairMappingTests(unittest.TestCase):
    def test_standards_fields_do_not_become_conformance_truth(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/rfc_editor_ietf/standards_specification_record.json")
        candidate = rfc_editor_ietf.normalize(fixture)["standards_specification_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["standards_specification_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["standards_conformance_verified"])

    def test_install_requirement_fields_do_not_become_installability_truth(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/vendor_documentation_portal/install_requirement_record.json")
        candidate = vendor_documentation_portal.normalize(fixture)["install_requirement_claim_candidate"][0]
        self.assertFalse(candidate["truth_boundary"]["install_requirement_candidate_is_installability_truth"])
        self.assertFalse(candidate["truth_boundary"]["installability_claimed"])

    def test_repair_safety_fields_do_not_authorize_action(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/service_manual_schematic_archive/repair_service_safety_record.json")
        candidate = service_manual_schematic_archive.normalize(fixture)["repair_service_safety_candidate"][0]
        self.assertFalse(candidate["truth_boundary"]["repair_service_safety_candidate_is_safety_truth"])
        self.assertFalse(candidate["truth_boundary"]["repair_service_candidate_authorizes_action"])


if __name__ == "__main__":
    unittest.main()
