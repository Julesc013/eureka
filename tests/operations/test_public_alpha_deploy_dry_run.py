from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_public_alpha_deploy_dry_run import (
    FALSE_BOUNDARY_FIELDS,
    validate_public_alpha_deploy_dry_run,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class PublicAlphaDeployDryRunTests(unittest.TestCase):
    def test_validator_accepts_dry_run_state(self) -> None:
        report = validate_public_alpha_deploy_dry_run()

        self.assertEqual(report["status"], "pass", report["errors"])
        self.assertTrue(report["deploy_dry_run_rehearsal_passed"])
        self.assertTrue(report["deploy_smoke_passed"])
        self.assertTrue(report["rollback_rehearsal_passed"])
        self.assertFalse(report["deployment_performed"])
        self.assertFalse(report["public_launch_performed"])

    def test_result_is_rehearsal_only(self) -> None:
        result = load_json("control/inventory/public_alpha_deploy_dry_run_result.json")

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["deploy_dry_run_rehearsal_passed"])
        self.assertTrue(result["deploy_smoke_passed"])
        self.assertTrue(result["rollback_rehearsal_passed"])
        self.assertFalse(result["deployment_performed"])
        self.assertFalse(result["public_launch_performed"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertFalse(result["public_launch_readiness_claimed"])
        self.assertTrue(result["recommended_next_task"].startswith("DEV-TO-MAIN-PROMOTION-REVIEW-05"))

    def test_manifest_does_not_write_deploy_artifacts(self) -> None:
        manifest = load_json("control/inventory/public_alpha_deploy_dry_run_manifest.json")

        self.assertEqual(manifest["hosting_mode"], "static_snapshot_site")
        self.assertGreaterEqual(len(manifest["inputs"]), 3)
        self.assertFalse(manifest["site_dist_write_planned"])
        self.assertFalse(manifest["site_dist_written"])
        self.assertFalse(manifest["deployment_performed"])
        self.assertFalse(manifest["public_launch_performed"])
        self.assertFalse(manifest["dns_change_required"])

    def test_smoke_and_rollback_rehearsals_pass_without_live_execution(self) -> None:
        smoke = load_json("control/inventory/public_alpha_deploy_dry_run_smoke_checklist.json")
        rollback = load_json("control/inventory/public_alpha_deploy_dry_run_rollback_rehearsal.json")

        self.assertTrue(smoke["deploy_smoke_passed"])
        self.assertFalse(smoke["live_http_used"])
        self.assertGreaterEqual(len(smoke["checks"]), 6)
        self.assertTrue(rollback["rollback_rehearsal_passed"])
        self.assertFalse(rollback["public_mutation_state_created"])

    def test_boundary_report_keeps_forbidden_actions_false(self) -> None:
        boundary = load_json("control/inventory/public_alpha_deploy_dry_run_boundary_report.json")

        for field in FALSE_BOUNDARY_FIELDS:
            self.assertIs(boundary[field], False, field)


if __name__ == "__main__":
    unittest.main()
