from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_dev_to_main_r0_merge.py"
PLAN_SCRIPT = ROOT / "scripts" / "prepare_r0_dev_to_main_merge.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, text: str = "fixture\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    return completed.stdout.strip()


def make_evidence_fixture(root: Path, *, report: bool = True, merge_overrides: dict | None = None, next_overrides: dict | None = None) -> None:
    merge = {
        "schema_version": "dev_to_main_r0_merge_result.v0",
        "task": "DEV-TO-MAIN-MERGE-R0",
        "status": "pass_with_warnings",
        "merge_performed": True,
        "merge_method": "fast_forward",
        "push_main_performed": True,
        "push_dev_performed": True,
        "force_push_performed": False,
        "history_rewrite_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "f0_decision": "resume_f0",
        "recommended_next_task": "F0-BUNDLE-01 \u2014 Deep extraction source-family and extraction-boundary policy packs",
    }
    if merge_overrides:
        merge.update(merge_overrides)
    git_state = {
        "schema_version": "dev_to_main_r0_git_state.v0",
        "task": "DEV-TO-MAIN-MERGE-R0",
        "current_branch_before": "dev",
        "head_before": "a",
        "origin_dev_before": "a",
        "origin_main_before": "b",
        "dev_contains_main_before": True,
        "dev_synced_before_merge": True,
        "current_branch_after": "dev",
        "head_after": "a",
        "origin_dev_after": "a",
        "origin_main_after": "a",
        "origin_main_equals_origin_dev_after": True,
        "working_tree_clean_after": True,
    }
    validation = {
        "schema_version": "dev_to_main_r0_validation_result.v0",
        "task": "DEV-TO-MAIN-MERGE-R0",
        "status": "pass_with_warnings",
        "full_unittest_discovery_pass": True,
        "generated_artifact_cleanliness_pass": True,
        "architecture_boundary_checks_pass": True,
        "r0_validators_pass": True,
        "warnings": [],
        "blockers": [],
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    next_task = {
        "schema_version": "dev_to_main_r0_next_task_decision.v0",
        "task": "DEV-TO-MAIN-MERGE-R0",
        "recommended_next_task": "F0-BUNDLE-01 \u2014 Deep extraction source-family and extraction-boundary policy packs",
        "recommended_start_branch": "main",
        "f0_can_resume": True,
        "reason": "Recovered R0 baseline promoted to main and validated.",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    if next_overrides:
        next_task.update(next_overrides)
    write_json(root / "control/inventory/dev_to_main_r0_merge_result.json", merge)
    write_json(root / "control/inventory/dev_to_main_r0_git_state.json", git_state)
    write_json(root / "control/inventory/dev_to_main_r0_validation_result.json", validation)
    write_json(root / "control/inventory/dev_to_main_r0_next_task_decision.json", next_task)
    for rel in (
        "README.md",
        "git_state.md",
        "validation.md",
        "promotion_result.md",
        "f0_start_decision.md",
        "generated/sample_merge_result.json",
        "generated/sample_git_state.json",
        "generated/sample_summary.md",
    ):
        path = root / "control/audits/dev-to-main-merge-r0-v0" / rel
        if path.suffix == ".json":
            write_json(path, {})
        else:
            write(path)
    if report:
        report_payload = {
            "schema_version": "dev_to_main_r0_merge_report.v0",
            "status": merge["status"],
            "task": "DEV-TO-MAIN-MERGE-R0",
            "purpose": "promote_recovered_r0_dev_to_main",
            "current_branch_before": "dev",
            "origin_dev_before": "a",
            "origin_main_before": "b",
            "dev_push_performed_before_merge": True,
            "validation_passed_before_merge": True,
            "merge_performed": merge["merge_performed"],
            "merge_method": merge["merge_method"],
            "push_main_performed": merge["push_main_performed"],
            "dev_resynced_after_main": True,
            "force_push_performed": merge["force_push_performed"],
            "history_rewrite_performed": merge["history_rewrite_performed"],
            "deployment_performed": merge["deployment_performed"],
            "working_tree_clean_after": True,
            "production_readiness_claimed": merge["production_readiness_claimed"],
            "public_launch_readiness_claimed": merge["public_launch_readiness_claimed"],
            "recommended_next_task": merge["recommended_next_task"],
            "validation": {},
        }
        write_json(root / "control/audits/dev-to-main-merge-r0-v0/merge_report.json", report_payload)


def make_plan_git_fixture(root: Path) -> None:
    run(["git", "init", "-b", "main"], root)
    run(["git", "config", "user.email", "r0-test@example.invalid"], root)
    run(["git", "config", "user.name", "R0 Test"], root)
    write(root / "README.md")
    run(["git", "add", "README.md"], root)
    run(["git", "commit", "-m", "initial"], root)
    main_sha = run(["git", "rev-parse", "HEAD"], root)
    run(["git", "checkout", "-b", "dev"], root)
    write_json(
        root / "control/inventory/r0_final_closeout_result.json",
        {
            "f0_decision": "resume_f0",
            "blockers_remaining": 0,
            "warnings_fully_disposed": True,
            "full_unittest_discovery_pass": True,
            "architecture_boundary_checks_pass": True,
            "all_required_validators_pass": True,
            "source_observation_ready": True,
            "source_cache_ready": True,
            "evidence_ledger_ready": True,
            "review_queue_ready": True,
            "reviewed_public_index_ready": True,
            "one_source_live_test_ready": True,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
    )
    write_json(root / "control/inventory/r0_final_blocker_register.json", {"blockers": []})
    write_json(root / "control/inventory/r0_remaining_blockers.json", {"blockers": []})
    write_json(root / "control/inventory/r0_final_warning_disposition.json", {"warnings": []})
    write_json(root / "control/inventory/r0_warning_disposition.json", {"warnings": []})
    write_json(root / "control/inventory/r0_production_review_result.json", {})
    write_json(root / "control/inventory/r0_contract_taxonomy_remediation_result.json", {"unresolved_after": 0, "compatibility_shims_after": 0, "contracts_clean_enough_for_f0": True, "production_readiness_claimed": False, "public_launch_readiness_claimed": False})
    write_json(root / "control/inventory/r0_generated_artifact_remediation_result.json", {"generated_artifact_drift_resolved": True, "site_dist_clean": True, "full_unittest_discovery_pass": True, "architecture_boundary_checks_pass": True, "production_readiness_claimed": False, "public_launch_readiness_claimed": False})
    write_json(root / "control/inventory/legacy_runtime_leakage_remediation_result.json", {"new_unallowlisted_leaks": 0, "clean_r0_seams_still_clean": True, "production_readiness_claimed": False, "public_launch_readiness_claimed": False})
    run(["git", "add", "."], root)
    run(["git", "commit", "-m", "evidence"], root)
    dev_sha = run(["git", "rev-parse", "HEAD"], root)
    run(["git", "update-ref", "refs/remotes/origin/main", main_sha], root)
    run(["git", "update-ref", "refs/remotes/origin/dev", dev_sha], root)


class DevToMainR0MergeTests(unittest.TestCase):
    def test_merge_validator_fails_when_merge_report_missing(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_dev_to_main_r0_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_evidence_fixture(repo, report=False)
            result = validator.validate(repo, check_git=False)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("missing audit pack file" in error for error in result["errors"]))

    def test_merge_validator_rejects_force_push_performed_true(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_dev_to_main_r0_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_evidence_fixture(repo, merge_overrides={"force_push_performed": True})
            result = validator.validate(repo, check_git=False)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("force_push_performed" in error for error in result["errors"]))

    def test_merge_validator_rejects_production_readiness_claimed_true(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_dev_to_main_r0_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_evidence_fixture(repo, merge_overrides={"production_readiness_claimed": True})
            result = validator.validate(repo, check_git=False)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("production readiness" in error for error in result["errors"]))

    def test_merge_validator_rejects_public_launch_readiness_claimed_true(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_dev_to_main_r0_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_evidence_fixture(repo, merge_overrides={"public_launch_readiness_claimed": True})
            result = validator.validate(repo, check_git=False)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("public launch readiness" in error for error in result["errors"]))

    def test_merge_validator_requires_f0_next_task(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_dev_to_main_r0_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_evidence_fixture(repo, next_overrides={"recommended_next_task": ""})
            result = validator.validate(repo, check_git=False)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("F0 next task" in error for error in result["errors"]))

    def test_merge_plan_blocks_if_dev_does_not_contain_main(self):
        plan_module = load_module(PLAN_SCRIPT, "prepare_r0_dev_to_main_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan_git_fixture(repo)
            run(["git", "checkout", "main"], repo)
            write(repo / "main-only.txt")
            run(["git", "add", "main-only.txt"], repo)
            run(["git", "commit", "-m", "advance main"], repo)
            run(["git", "update-ref", "refs/remotes/origin/main", run(["git", "rev-parse", "HEAD"], repo)], repo)
            run(["git", "checkout", "dev"], repo)
            plan = plan_module.build_merge_plan(repo)
            self.assertFalse(plan["ready"])

    def test_merge_plan_blocks_if_working_tree_dirty(self):
        plan_module = load_module(PLAN_SCRIPT, "prepare_r0_dev_to_main_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan_git_fixture(repo)
            write(repo / "dirty.txt")
            plan = plan_module.build_merge_plan(repo)
            self.assertFalse(plan["ready"])

    def test_merge_plan_defaults_to_no_deployment(self):
        plan_module = load_module(PLAN_SCRIPT, "prepare_r0_dev_to_main_merge")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_plan_git_fixture(repo)
            plan = plan_module.build_merge_plan(repo)
            self.assertIn("deployment", "\n".join(plan["forbidden_operations"]))
            self.assertFalse(plan["branch_mutation_performed"])


if __name__ == "__main__":
    unittest.main()
