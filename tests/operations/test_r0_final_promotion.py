from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = ROOT / "scripts" / "audit_r0_final_promotion.py"
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_r0_final_promotion.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    return completed.stdout.strip()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_git_fixture(root: Path, mutator=None) -> None:
    run(["git", "init", "-b", "main"], root)
    run(["git", "config", "user.email", "r0-test@example.invalid"], root)
    run(["git", "config", "user.name", "R0 Test"], root)
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    run(["git", "add", "README.md"], root)
    run(["git", "commit", "-m", "initial"], root)
    main_sha = run(["git", "rev-parse", "HEAD"], root)
    run(["git", "checkout", "-b", "dev"], root)
    write_passing_evidence(root)
    if mutator:
        mutator(root)
    run(["git", "add", "."], root)
    run(["git", "commit", "-m", "r0 evidence"], root)
    dev_sha = run(["git", "rev-parse", "HEAD"], root)
    run(["git", "update-ref", "refs/remotes/origin/main", main_sha], root)
    run(["git", "update-ref", "refs/remotes/origin/dev", dev_sha], root)


def write_passing_evidence(root: Path) -> None:
    write_json(
        root / "control/inventory/r0_final_closeout_result.json",
        {
            "schema_version": "r0_final_closeout_result.v0",
            "status": "pass_with_warnings",
            "task": "R0-11",
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
    write_json(root / "control/inventory/r0_final_blocker_register.json", {"schema_version": "r0_final_blocker_register.v0", "blockers": []})
    write_json(root / "control/inventory/r0_remaining_blockers.json", {"schema_version": "r0_remaining_blockers.v0", "blockers": []})
    write_json(
        root / "control/inventory/r0_final_warning_disposition.json",
        {
            "schema_version": "r0_final_warning_disposition.v0",
            "warnings": [
                {
                    "warning_id": "R0-FINAL-WARN-001",
                    "area": "architecture_leakage",
                    "warning": "legacy allowlist debt remains",
                    "disposition": "child_task_created",
                    "child_task": "R0-REMEDIATION-LEGACY-LEAKAGE-01",
                    "notes": [],
                }
            ],
        },
    )
    write_json(root / "control/inventory/r0_warning_disposition.json", {"schema_version": "r0_warning_disposition.v0", "warnings": []})
    write_json(
        root / "control/inventory/r0_production_review_result.json",
        {
            "schema_version": "r0_production_review_result.v0",
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
    write_json(
        root / "control/inventory/r0_contract_taxonomy_remediation_result.json",
        {
            "schema_version": "r0_contract_taxonomy_remediation_result.v0",
            "unresolved_after": 0,
            "compatibility_shims_after": 0,
            "contracts_clean_enough_for_f0": True,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
    )
    write_json(
        root / "control/inventory/r0_generated_artifact_remediation_result.json",
        {
            "schema_version": "r0_generated_artifact_remediation_result.v0",
            "generated_artifact_drift_resolved": True,
            "full_unittest_discovery_pass": True,
            "architecture_boundary_checks_pass": True,
            "generated_artifact_cleanliness_pass": True,
            "site_dist_clean": True,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
    )
    write_json(
        root / "control/inventory/legacy_runtime_leakage_remediation_result.json",
        {
            "schema_version": "legacy_runtime_leakage_remediation_result.v0",
            "status": "pass_with_warnings",
            "new_unallowlisted_leaks": 0,
            "clean_r0_seams_still_clean": True,
            "remaining_allowlist_count": 3,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
    )


def write_required_promotion_outputs(root: Path, audit_module, *, production_claim: bool = False, public_claim: bool = False) -> None:
    audit = audit_module.build_final_promotion(root)
    result = dict(audit["r0_final_promotion_review_result"])
    result["production_readiness_claimed"] = production_claim
    result["public_launch_readiness_claimed"] = public_claim
    write_json(root / "control/inventory/r0_final_promotion_review_result.json", result)
    write_json(root / "control/inventory/r0_final_promotion_readiness_matrix.json", audit["r0_final_promotion_readiness_matrix"])
    write_json(root / "control/inventory/r0_final_promotion_blockers.json", audit["r0_final_promotion_blockers"])
    write_json(root / "control/inventory/r0_final_promotion_warning_disposition.json", audit["r0_final_promotion_warning_disposition"])
    write_json(root / "control/inventory/r0_final_promotion_git_state.json", audit["r0_final_promotion_git_state"])
    write_json(root / "control/inventory/r0_final_promotion_next_task_decision.json", audit["r0_final_promotion_next_task_decision"])
    report = dict(audit["promotion_review_report"])
    report["production_readiness_claimed"] = production_claim
    report["public_launch_readiness_claimed"] = public_claim
    write_json(root / "control/audits/r0-final-promotion-review-v0/promotion_review_report.json", report)
    for rel in (
        "README.md",
        "git_state.md",
        "readiness_matrix.md",
        "blocker_report.md",
        "warning_disposition.md",
        "merge_plan.md",
        "f0_start_policy.md",
        "validation.md",
        "generated/sample_promotion_review_result.json",
        "generated/sample_git_state.json",
        "generated/sample_merge_plan.json",
        "generated/sample_summary.md",
    ):
        path = root / "control/audits/r0-final-promotion-review-v0" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


class R0FinalPromotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = load_module(AUDIT_SCRIPT, "audit_r0_final_promotion")

    def build(self, mutator=None):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo, mutator=mutator)
            return self.audit.build_final_promotion(repo)

    def test_promotion_audit_fails_if_working_tree_dirty(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            (repo / "README.md").write_text("dirty\n", encoding="utf-8")
            audit = self.audit.build_final_promotion(repo)
            self.assertFalse(audit["r0_final_promotion_review_result"]["working_tree_clean"])
            self.assertEqual("remain_blocked", audit["r0_final_promotion_review_result"]["dev_to_main_decision"])

    def test_promotion_audit_fails_if_dev_does_not_contain_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            run(["git", "checkout", "main"], repo)
            (repo / "main.txt").write_text("main advance\n", encoding="utf-8")
            run(["git", "add", "main.txt"], repo)
            run(["git", "commit", "-m", "advance main"], repo)
            run(["git", "update-ref", "refs/remotes/origin/main", run(["git", "rev-parse", "HEAD"], repo)], repo)
            run(["git", "checkout", "dev"], repo)
            audit = self.audit.build_final_promotion(repo)
            self.assertFalse(audit["r0_final_promotion_review_result"]["dev_contains_main"])
            self.assertEqual("remain_blocked", audit["r0_final_promotion_review_result"]["dev_to_main_decision"])

    def test_promotion_audit_fails_if_unittest_discovery_failing(self):
        def mutate(repo: Path) -> None:
            write_json(
                repo / "control/inventory/r0_final_closeout_result.json",
                {
                    "schema_version": "r0_final_closeout_result.v0",
                    "status": "blocked",
                    "task": "R0-11",
                    "f0_decision": "remediation_required",
                    "blockers_remaining": 0,
                    "warnings_fully_disposed": True,
                    "full_unittest_discovery_pass": False,
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

        audit = self.build(mutator=mutate)
        self.assertFalse(audit["r0_final_promotion_review_result"]["full_unittest_discovery_pass"])
        self.assertEqual("remain_blocked", audit["r0_final_promotion_review_result"]["dev_to_main_decision"])

    def test_promotion_audit_fails_if_generated_artifact_drift_remains(self):
        audit = self.build(
            mutator=lambda repo: write_json(
                repo / "control/inventory/r0_generated_artifact_remediation_result.json",
                {
                    "schema_version": "r0_generated_artifact_remediation_result.v0",
                    "generated_artifact_drift_resolved": False,
                    "full_unittest_discovery_pass": True,
                    "architecture_boundary_checks_pass": True,
                    "generated_artifact_cleanliness_pass": False,
                    "site_dist_clean": False,
                    "production_readiness_claimed": False,
                    "public_launch_readiness_claimed": False,
                },
            )
        )
        self.assertFalse(audit["r0_final_promotion_review_result"]["generated_artifact_cleanliness_pass"])
        self.assertEqual("remain_blocked", audit["r0_final_promotion_review_result"]["dev_to_main_decision"])

    def test_promotion_audit_fails_if_hard_blockers_remain(self):
        audit = self.build(
            mutator=lambda repo: write_json(
                repo / "control/inventory/r0_remaining_blockers.json",
                {"schema_version": "r0_remaining_blockers.v0", "blockers": [{"area": "contract_taxonomy", "finding": "x"}]},
            )
        )
        self.assertGreater(audit["r0_final_promotion_review_result"]["hard_blockers_remaining"], 0)
        self.assertEqual("remain_blocked", audit["r0_final_promotion_review_result"]["dev_to_main_decision"])

    def test_promotion_audit_passes_with_warning_only_debt_when_warnings_fully_disposed(self):
        audit = self.build()
        result = audit["r0_final_promotion_review_result"]
        self.assertEqual("pass_with_warnings", result["status"])
        self.assertTrue(result["warnings_fully_disposed"])
        self.assertEqual(0, result["hard_blockers_remaining"])
        self.assertEqual("promotion_plan_only", result["dev_to_main_decision"])

    def test_validator_rejects_production_readiness_claim(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_r0_final_promotion")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            write_required_promotion_outputs(repo, self.audit, production_claim=True)
            result = validator.validate(repo)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("production_readiness_claimed" in error for error in result["errors"]))

    def test_validator_rejects_public_launch_claim(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_r0_final_promotion")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            write_required_promotion_outputs(repo, self.audit, public_claim=True)
            result = validator.validate(repo)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("public_launch_readiness_claimed" in error for error in result["errors"]))

    def test_f0_next_task_is_explicit(self):
        audit = self.build()
        decision = audit["r0_final_promotion_next_task_decision"]
        self.assertIn(decision["f0_decision"], {"resume_f0", "remain_blocked", "remediation_required"})
        self.assertIn(decision["recommended_start_branch"], {"dev", "main"})
        self.assertTrue(decision["recommended_next_task"])


if __name__ == "__main__":
    unittest.main()
