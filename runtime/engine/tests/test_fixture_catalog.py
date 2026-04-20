from __future__ import annotations

import unittest

from runtime.engine.core import DEFAULT_SOFTWARE_FIXTURE_PATH, load_default_fixture_catalog
from runtime.engine.resolve import fixture_entry_to_object_summary


class FixtureCatalogTestCase(unittest.TestCase):
    def test_default_fixture_catalog_loads_known_entry(self) -> None:
        catalog = load_default_fixture_catalog()

        self.assertEqual(catalog.source_path, DEFAULT_SOFTWARE_FIXTURE_PATH)
        self.assertEqual(len(catalog.entries), 1)
        self.assertEqual(catalog.default_target_ref, "fixture:software/synthetic-demo-app@1.0.0")

        entry = catalog.find_by_target_ref(catalog.default_target_ref)
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.state_record["kind"], "release")
        self.assertEqual(entry.representation_record["kind"], "source_archive")
        self.assertEqual(
            entry.access_path_record["locator"],
            "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
        )

    def test_fixture_entry_maps_to_bounded_object_summary(self) -> None:
        catalog = load_default_fixture_catalog()
        entry = catalog.find_by_target_ref(catalog.default_target_ref)
        assert entry is not None

        summary = fixture_entry_to_object_summary(entry)

        self.assertEqual(
            summary.to_dict(),
            {
                "id": "obj.synthetic-demo-app",
                "kind": "software",
                "label": "Synthetic Demo App",
            },
        )
