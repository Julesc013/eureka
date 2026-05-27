from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "scripts/validate_source_snapshot_baseline_closeout.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_source_snapshot_baseline_closeout", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceSnapshotBaselineCloseoutTests(unittest.TestCase):
    def test_scope_matrix_covers_closeout_baseline(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/source_snapshot_closeout_scope_matrix.json").read_text(encoding="utf-8"))
        scope_ids = {item["subsystem_id"] for item in payload["scope"]}

        self.assertEqual(scope_ids, {"source_action_kernel", "source_wave", "snapshot_relay"})

    def test_boundary_report_keeps_unsafe_actions_disabled(self) -> None:
        boundary = json.loads((REPO_ROOT / "control/inventory/source_snapshot_closeout_boundary_report.json").read_text(encoding="utf-8"))

        for field in load_validator().BOUNDARY_FALSE_FIELDS:
            self.assertFalse(boundary[field], field)

    def test_red_full_discovery_is_not_reported_as_pass(self) -> None:
        result = json.loads((REPO_ROOT / "control/inventory/source_snapshot_closeout_result.json").read_text(encoding="utf-8"))
        full = json.loads((REPO_ROOT / "control/inventory/source_snapshot_closeout_full_discovery_result.json").read_text(encoding="utf-8"))

        if full["status"] == "fail":
            self.assertEqual(result["status"], "blocked")
            self.assertFalse(result["full_unittest_discovery_passed"])
            self.assertFalse(result["dev_ready_for_main_promotion"])
        elif full["status"] == "external_not_provided":
            self.assertEqual(result["status"], load_validator().WAITING_STATUS)
            self.assertFalse(result["external_full_discovery_summary_received"])
            self.assertFalse(result["full_unittest_discovery_passed"])
            self.assertFalse(result["dev_ready_for_main_promotion"])

    def test_validator_passes(self) -> None:
        result = load_validator().validate(REPO_ROOT)

        self.assertEqual(result["status"], "pass", result["errors"])


if __name__ == "__main__":
    unittest.main()
