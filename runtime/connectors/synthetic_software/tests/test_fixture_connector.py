from __future__ import annotations

import unittest

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector, load_synthetic_source_records


class SyntheticSoftwareConnectorTestCase(unittest.TestCase):
    def test_source_loading_returns_a_small_governed_fixture_corpus(self) -> None:
        records = load_synthetic_source_records()

        self.assertEqual(len(records), 5)
        self.assertEqual(
            [record.target_ref for record in records],
            [
                "fixture:software/synthetic-demo-app@1.0.0",
                "fixture:software/synthetic-demo-suite@2.0.0",
                "fixture:software/compatibility-lab@3.2.1",
                "fixture:software/archive-viewer@0.9.0",
                "fixture:software/archivebox@0.8.5",
            ],
        )
        self.assertEqual(records[0].source_name, "synthetic_software_fixture")
        self.assertEqual(
            records[0].source_locator,
            "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
        )

    def test_connector_reports_default_target_ref_from_loaded_source(self) -> None:
        connector = SyntheticSoftwareConnector()

        self.assertEqual(
            connector.default_target_ref(),
            "fixture:software/synthetic-demo-app@1.0.0",
        )
