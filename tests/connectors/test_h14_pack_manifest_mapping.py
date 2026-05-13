from __future__ import annotations

import copy
import unittest

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.connector_pack_manifest_source import normalize as normalize_connector_pack
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.source_pack_manifest_source import normalize as normalize_source_pack
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import detect_h14_registry_or_pack_mutation_violations, detect_h14_truth_boundary_violations
from scripts import validate_h14_source_discovery_fixture_runtime as validator


class H14PackManifestMappingTests(unittest.TestCase):
    def test_source_pack_manifest_is_not_exported_pack(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_pack_manifest/source_pack_manifest_record.json")
        normalized = normalize_source_pack(fixture)
        self.assertFalse(normalized["source_pack_manifest_candidate"]["truth_boundary"]["source_pack_manifest_candidate_is_exported_pack"])

    def test_connector_pack_manifest_is_not_connector_approval(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/connector_pack_manifest/connector_pack_manifest_record.json")
        normalized = normalize_connector_pack(fixture)
        self.assertFalse(normalized["connector_pack_manifest_candidate"]["truth_boundary"]["connector_pack_manifest_candidate_is_connector_approval"])

    def test_pack_boundary_grants_no_permission_and_claims_fail(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_pack_manifest/pack_import_export_boundary_record.json")
        normalized = normalize_source_pack(fixture)
        self.assertFalse(normalized["pack_import_export_boundary_candidate"]["truth_boundary"]["pack_import_export_boundary_candidate_grants_permission"])
        mutated = copy.deepcopy(normalized)
        mutated["truth_boundary"]["pack_import_export_boundary_candidate_grants_permission"] = True
        self.assertTrue(detect_h14_truth_boundary_violations(mutated))
        mutated = copy.deepcopy(normalized)
        mutated["source_pack_export_included"] = True
        self.assertTrue(detect_h14_registry_or_pack_mutation_violations(mutated))


if __name__ == "__main__":
    unittest.main()
