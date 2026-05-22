from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_resolution_run_kernel import validate_repo


class ValidateResolutionRunKernelTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate_repo(ROOT)
        self.assertEqual("valid", result["status"], result)
        self.assertGreater(result["workunit_count"], 0)
        self.assertGreater(result["lane_count"], 0)
        self.assertFalse(result["source_probe_executed"])
        self.assertFalse(result["live_ia_call_performed"])


if __name__ == "__main__":
    unittest.main()
