from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.validators.validate_taxonomy_closeout_policy import validate_taxonomy_closeout_policy


class TaxonomyCloseoutPolicyValidatorTestCase(unittest.TestCase):
    def test_minimal_policy_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_fixture(root)
            git_add(root)

            report = validate_taxonomy_closeout_policy(root)

        self.assertEqual(report["status"], "valid")

    def test_forbidden_active_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_fixture(root)
            write(root / "release/render/render.yaml", "services: []\n")
            git_add(root)

            report = validate_taxonomy_closeout_policy(root)

        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("release/render" in error for error in report["errors"]))


def write_minimal_fixture(root: Path) -> None:
    write_json(
        root / "control/policies/taxonomy_closeout_policy.json",
        {
            "status": "active_closeout_policy",
            "product_behavior_change_allowed": False,
            "runtime": {"closeout_mode": "canonical_with_compatibility_wrappers", "target_families": ["runtime/local"]},
            "contracts": {"closeout_mode": "canonical_paths_with_alias_inventory", "target_families": ["contracts/source"]},
            "examples": {"closeout_mode": "canonical_families_with_remaining_classified_debt", "target_families": ["examples/packs"]},
        },
    )
    write_json(
        root / "control/policies/aide_ledger_size_policy.json",
        {
            "status": "active_control_plane_policy",
            "areas": [
                {"path": ".aide", "class": "active_authority"},
                {"path": ".aide/generated", "class": "generated"},
                {"path": ".aide/export", "class": "export_only"},
                {"path": ".aide/cache", "class": "cache"},
                {"path": ".aide/reports", "class": "retention_capped"},
            ],
        },
    )
    write_json(
        root / "control/audits/generated-artifact-visibility-v1/tracked_generated_paths.json",
        {"status": "valid", "tracked_tmp_count": 0},
    )
    for relative in [
        "control/audits/generated-artifact-visibility-v1/excluded_dir_policy.json",
        "control/audits/taxonomy-closeout-v1/runtime_taxonomy_closeout.json",
        "control/audits/taxonomy-closeout-v1/contracts_taxonomy_migration_map.json",
        "control/audits/taxonomy-closeout-v1/examples_taxonomy_closeout.json",
        "control/audits/taxonomy-closeout-v1/aide_ledger_size_report.json",
        "control/audits/eureka-structure-final-closeout-v1/before_state.json",
        "control/audits/eureka-structure-final-closeout-v1/path_migration_map.json",
    ]:
        write_json(root / relative, {"status": "valid"})
    for relative in [
        "control/audits/generated-artifact-visibility-v1/generated_artifact_risk_report.md",
        "control/audits/taxonomy-closeout-v1/runtime_taxonomy_closeout.md",
        "control/audits/taxonomy-closeout-v1/contracts_taxonomy_closeout.md",
        "control/audits/taxonomy-closeout-v1/examples_taxonomy_closeout.md",
        "control/audits/taxonomy-closeout-v1/aide_ledger_size_report.md",
    ]:
        write(root / relative, "ok\n")
    write(root / "contracts/schema/control/README.md", "compatibility canonical target not active runtime\n")
    write(root / "runtime/README.md", "runtime/engine taxonomy closeout compatibility\n")
    write(root / "runtime/pages/README.md", "runtime metadata not presentation surfaces/web\n")
    write(root / "examples/README.md", "durable families taxonomy closeout public-safe\n")
    write(root / ".aide/README.md", "not product truth export-only retention-capped\n")
    write(root / "docs/architecture/PATH_TAXONOMY_CLOSEOUT.md", "no behavior change migration map first runtime/engine\n")


def write_json(path: Path, payload: object) -> None:
    write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_add(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "add", "."], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
