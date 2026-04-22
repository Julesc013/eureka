from __future__ import annotations

import unittest

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.interfaces.public import SearchRequest
from runtime.engine.resolve import DeterministicSearchService, resolved_resource_id_for_record


class DeterministicSearchServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        source_records = SyntheticSoftwareConnector().load_source_records()
        self.normalized_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in source_records
        )
        self.service = DeterministicSearchService(NormalizedCatalog(self.normalized_records))

    def test_search_returns_multiple_matches_in_catalog_order(self) -> None:
        response = self.service.search(SearchRequest.from_parts("synthetic"))

        self.assertEqual(
            [result.target_ref for result in response.results],
            [
                "fixture:software/synthetic-demo-app@1.0.0",
                "fixture:software/synthetic-demo-suite@2.0.0",
            ],
        )
        self.assertEqual(
            [result.resolved_resource_id for result in response.results],
            [
                resolved_resource_id_for_record(self.normalized_records[0]),
                resolved_resource_id_for_record(self.normalized_records[1]),
            ],
        )
        self.assertEqual(response.results[0].evidence[0].claim_kind, "label")
        self.assertEqual(response.results[0].evidence[0].claim_value, "Synthetic Demo App")
        self.assertEqual(response.results[0].evidence[0].asserted_by_label, "Synthetic Fixture")
        self.assertIsNone(response.absence)

    def test_search_returns_one_match_for_specific_query(self) -> None:
        response = self.service.search(SearchRequest.from_parts("compatibility"))

        self.assertEqual(len(response.results), 1)
        self.assertEqual(
            response.results[0].target_ref,
            "fixture:software/compatibility-lab@3.2.1",
        )
        self.assertEqual(
            response.results[0].object_summary.to_dict(),
            {
                "id": "obj.compatibility-lab",
                "kind": "software",
                "label": "Compatibility Lab",
            },
        )
        self.assertEqual(response.results[0].evidence[0].claim_kind, "label")
        self.assertIsNone(response.absence)

    def test_search_returns_zero_matches_and_structured_absence(self) -> None:
        response = self.service.search(SearchRequest.from_parts("missing"))

        self.assertEqual(response.results, ())
        assert response.absence is not None
        self.assertEqual(response.absence.code, "search_no_matches")
        self.assertEqual(
            response.absence.message,
            "No bounded records matched query 'missing'.",
        )
