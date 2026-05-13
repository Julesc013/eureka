from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h7_library_research.fixture_loader import load_h7_library_research_fixture
from control.prototypes.legacy_runtime.connectors.h7_library_research import openalex, datacite, europeana

REPO_ROOT = Path(__file__).resolve().parents[2]


class H7ResearchDatasetCulturalMappingTests(unittest.TestCase):
    def test_research_work_fields_do_not_become_work_truth(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/openalex/identity_record.json")
        candidate = openalex.normalize(fixture)["research_work_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["research_work_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_research_work_truth"])

    def test_dataset_fields_do_not_become_dataset_validity_truth(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/datacite/identity_record.json")
        candidate = datacite.normalize(fixture)["dataset_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["dataset_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["dataset_validity_verified"])

    def test_cultural_object_fields_do_not_become_object_truth(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/europeana/identity_record.json")
        candidate = europeana.normalize(fixture)["cultural_object_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["cultural_object_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_cultural_object_truth"])


if __name__ == "__main__":
    unittest.main()
