from __future__ import annotations

import unittest

from runtime.source.action import REQUIRED_SOURCE_WAVE_FAMILIES, list_registered_source_families


class SourceWaveTests(unittest.TestCase):
    def test_all_required_families_are_listed(self) -> None:
        self.assertEqual(set(REQUIRED_SOURCE_WAVE_FAMILIES), set(list_registered_source_families()))
        self.assertEqual(8, len(list_registered_source_families()))


if __name__ == "__main__":
    unittest.main()
