from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestImpactMapTests(unittest.TestCase):
    def test_required_patterns_are_mapped(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/test_impact_map.json").read_text(encoding="utf-8"))
        patterns = {row["path_pattern"]: row for row in payload["mappings"]}
        for pattern in [
            "contracts/search_interaction/**",
            "runtime/local_service/**",
            "scripts/eureka_*.py",
            "scripts/validate_*.py",
            "tests/**",
        ]:
            self.assertIn(pattern, patterns)
            self.assertIn("owning_subsystem", patterns[pattern])

    def test_runtime_local_service_selects_result_lane_tests(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/test_impact_map.json").read_text(encoding="utf-8"))
        row = next(item for item in payload["mappings"] if item["path_pattern"] == "runtime/local_service/**")
        self.assertIn("python scripts/validate_workbench_result_lanes.py", row["validators"])
        self.assertIn("tests.runtime.test_workbench_result_lanes", row["test_modules"])
        self.assertTrue(row["full_discovery_required_before_promotion"])


if __name__ == "__main__":
    unittest.main()

