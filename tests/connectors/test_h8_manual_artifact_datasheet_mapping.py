from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.fixture_loader import load_h8_manuals_docs_fixture
from archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards import bitsavers_docs, semiconductor_datasheets

REPO_ROOT = Path(__file__).resolve().parents[2]


class H8ManualArtifactDatasheetMappingTests(unittest.TestCase):
    def test_manual_artifact_relation_fields_do_not_become_relation_truth(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/manual_artifact_relation_record.json")
        candidate = bitsavers_docs.normalize(fixture)["manual_artifact_relation_candidate"][0]
        self.assertFalse(candidate["truth_boundary"]["manual_artifact_relation_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["compatibility_correctness_claimed"])

    def test_datasheet_fields_do_not_become_device_truth(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/semiconductor_datasheets/datasheet_device_record.json")
        candidate = semiconductor_datasheets.normalize(fixture)["datasheet_device_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["datasheet_device_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["electrical_safety_claimed"])


if __name__ == "__main__":
    unittest.main()
