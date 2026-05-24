from __future__ import annotations

import unittest

from runtime.source.action import REQUIRED_SOURCE_WAVE_FAMILIES, build_source_wave_adapter


class SourceWaveAdapterTests(unittest.TestCase):
    def test_each_required_family_builds_adapter(self) -> None:
        for family in REQUIRED_SOURCE_WAVE_FAMILIES:
            with self.subTest(family=family):
                adapter = build_source_wave_adapter(family)
                self.assertEqual(family, adapter.source_family)
                self.assertIn("fixture", adapter.supported_transport_modes)


if __name__ == "__main__":
    unittest.main()
