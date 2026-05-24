from __future__ import annotations

import unittest

from runtime.source.action import REQUIRED_SOURCE_WAVE_FAMILIES, build_source_wave_scorecard


class SourceWaveScorecardTests(unittest.TestCase):
    def test_scorecards_include_risk_and_next_validation(self) -> None:
        for family in REQUIRED_SOURCE_WAVE_FAMILIES:
            with self.subTest(family=family):
                scorecard = build_source_wave_scorecard(family)
                dimensions = scorecard["dimensions"]
                self.assertIn("metadata_quality", dimensions)
                self.assertIn("rights_risk", dimensions)
                self.assertIn("next_validation_task", dimensions)


if __name__ == "__main__":
    unittest.main()
