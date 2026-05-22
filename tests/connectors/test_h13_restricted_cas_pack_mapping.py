from __future__ import annotations

import unittest

from archive.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture
from archive.prototypes.legacy_runtime.connectors.h13_local_private import restricted_source_manifest_only, local_disk_image_metadata, local_package_cache_metadata
from scripts import validate_h13_local_private_fixture_runtime as validator


class H13RestrictedCasPackMappingTests(unittest.TestCase):
    def test_restricted_manifest_does_not_grant_access(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/restricted_source_manifest_only/restricted_source_manifest_record.json")
        candidate = restricted_source_manifest_only.normalize(fixture)["restricted_source_manifest_candidate"]
        self.assertFalse(candidate["truth_boundary"]["restricted_source_manifest_candidate_grants_access_permission"])

    def test_cas_candidate_does_not_import(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/local_disk_image_metadata/local_cas_import_boundary_record.json")
        candidate = local_disk_image_metadata.normalize(fixture)["local_cas_import_boundary_candidate"]
        self.assertFalse(candidate["truth_boundary"]["local_cas_import_boundary_candidate_is_import_permission"])

    def test_pack_candidate_does_not_export_or_import(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/local_package_cache_metadata/pack_export_import_boundary_record.json")
        candidate = local_package_cache_metadata.normalize(fixture)["pack_export_import_boundary_candidate"]
        self.assertFalse(candidate["truth_boundary"]["pack_export_import_boundary_candidate_is_export_import_permission"])


if __name__ == "__main__":
    unittest.main()
