#!/usr/bin/env python3
"""Validate Compatibility-Aware Ranking Assessment v0 examples."""

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence, TextIO


import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FINGERPRINT_RE = re.compile(r"(machine[-_ ]?fingerprint|hardware[-_ ]?fingerprint)", re.IGNORECASE)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def iter_values(value: Any):
    if isinstance(value, Mapping):
        for item in value.values():
            yield from iter_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_values(item)
    else:
        yield value


def check_public_safe(value: Any, errors: list[str], *, allow_fingerprint_words: bool = False) -> None:
    for item in iter_values(value):
        if not isinstance(item, str):
            continue
        if PRIVATE_PATH_RE.search(item):
            errors.append(f"private path-like value found: {item}")
        if SECRET_RE.search(item):
            errors.append(f"secret-like value found: {item}")
        if IP_RE.search(item):
            errors.append(f"IP address-like value found: {item}")
        if ACCOUNT_RE.search(item):
            errors.append(f"account identifier-like value found: {item}")
        if not allow_fingerprint_words and FINGERPRINT_RE.search(item):
            errors.append(f"local machine fingerprint-like value found: {item}")


def check_false_map(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false")


def check_true(data: Mapping[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if data.get(field) is not True:
        errors.append(f"{prefix}.{field} must be true")


def check_checksums(root: Path, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.exists():
        errors.append(f"missing checksum file: {checksum_path}")
        return
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, name = line.split(None, 1)
        target = root / name.strip()
        if not target.exists():
            errors.append(f"checksum target missing: {target}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"checksum mismatch for {target}")


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "compatibility_aware_ranking"
TOP_LEVEL_REQUIRED = {'emulator_vm_launch_enabled', 'hardware_peripheral_driver_requirements', 'live_source_called', 'result_suppressed', 'malware_safety_claimed', 'architecture_cpu_abi_api_matching', 'target_profile_ref', 'candidate_index_mutated', 'evidence_ledger_mutated', 'external_calls_performed', 'dependency_safety_claimed', 'action_safety_installability_caution', 'downloads_enabled', 'privacy', 'executable_inspected', 'user_profile_signal_used', 'compatibility_ranking_assessment_id', 'model_call_performed', 'no_mutation_guarantees', 'package_manager_invoked', 'compatibility_truth_claimed', 'emulator_vm_reconstruction_feasibility', 'candidate_promotion_performed', 'incompatibility_and_unknown_gaps', 'created_by_tool', 'schema_version', 'tie_breaks', 'persistent_compatibility_ranking_store_implemented', 'compatibility_ranking_applied_to_live_search', 'installability_claimed', 'no_runtime_guarantees', 'source_cache_mutated', 'ad_signal_used', 'ranking_scope', 'public_index_mutated', 'compatibility_ranking_assessment_kind', 'compatibility_evidence_strength', 'public_projection', 'limitations', 'platform_os_version_matching', 'popularity_signal_used', 'notes', 'hidden_suppression_performed', 'compatibility_explanation_ref', 'runtime_compatibility_ranking_implemented', 'execution_enabled', 'source_provenance_candidate_caution', 'installs_enabled', 'rights_clearance_claimed', 'no_ranking_change_guarantees', 'runtime_dependency_requirements', 'telemetry_exported', 'ranked_items', 'status', 'local_index_mutated', 'master_index_mutated', 'compatibility_factors', 'public_search_order_changed', 'rights_risk'}
HARD_FALSE_FIELDS = {
    "runtime_compatibility_ranking_implemented", "persistent_compatibility_ranking_store_implemented",
    "compatibility_ranking_applied_to_live_search", "public_search_order_changed", "result_suppressed",
    "hidden_suppression_performed", "candidate_promotion_performed", "installability_claimed",
    "compatibility_truth_claimed", "dependency_safety_claimed", "emulator_vm_launch_enabled",
    "package_manager_invoked", "executable_inspected", "downloads_enabled", "installs_enabled",
    "execution_enabled", "master_index_mutated", "public_index_mutated", "local_index_mutated",
    "source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "live_source_called",
    "external_calls_performed", "telemetry_exported", "popularity_signal_used", "user_profile_signal_used",
    "ad_signal_used", "model_call_performed", "rights_clearance_claimed", "malware_safety_claimed",
}
STATUSES = {"draft_example", "dry_run_validated", "synthetic_example", "public_safe_example", "review_required", "compatibility_policy_candidate", "runtime_future", "rejected_by_policy"}
FACTOR_TYPES = {"platform_os_match", "os_version_match", "architecture_match", "cpu_feature_match", "abi_match", "API_match", "runtime_dependency_match", "library_dependency_match", "package_dependency_match", "hardware_requirement_match", "peripheral_requirement_match", "driver_requirement_match", "emulator_vm_feasibility", "compatibility_evidence_strength", "incompatibility_evidence", "unknown_gap", "action_safety", "rights_risk_caution", "unknown"}
WEIGHT_POLICIES = {"descriptive_only", "future_weighted", "not_weighted_v0"}


def validate_assessment(path: Path, *, example_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        page = load_json(path)
    except Exception as exc:
        return [f"{display_path(path, REPO_ROOT)} failed to parse: {exc}"]
    if not isinstance(page, Mapping):
        return [f"{display_path(path, REPO_ROOT)} must be an object"]
    missing = sorted(TOP_LEVEL_REQUIRED - set(page))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    if page.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    if page.get("compatibility_ranking_assessment_kind") != "compatibility_aware_ranking_assessment":
        errors.append("compatibility_ranking_assessment_kind must be compatibility_aware_ranking_assessment")
    if page.get("status") not in STATUSES:
        errors.append("status is not allowed")
    check_false_map(page, HARD_FALSE_FIELDS, "assessment", errors)
    items = page.get("ranked_items")
    if not isinstance(items, list) or len(items) < 2:
        errors.append("ranked_items must contain at least two items")
    else:
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                errors.append(f"ranked_items[{index}] must be an object")
            elif item.get("rank_changed_now") is not False:
                errors.append(f"ranked_items[{index}].rank_changed_now must be false")
    factors = page.get("compatibility_factors")
    if not isinstance(factors, list) or not factors:
        errors.append("compatibility_factors must be a non-empty list")
    else:
        for index, factor in enumerate(factors):
            if not isinstance(factor, Mapping):
                errors.append(f"compatibility_factors[{index}] must be an object")
                continue
            if factor.get("factor_type") not in FACTOR_TYPES:
                errors.append(f"compatibility_factors[{index}].factor_type is not allowed")
            if factor.get("weight_policy") not in WEIGHT_POLICIES:
                errors.append(f"compatibility_factors[{index}].weight_policy is not allowed")
            if factor.get("score_applied_now") is not False:
                errors.append(f"compatibility_factors[{index}].score_applied_now must be false")
    platform = page.get("platform_os_version_matching")
    if not isinstance(platform, Mapping) or platform.get("platform_match_not_truth") is not True:
        errors.append("platform_os_version_matching.platform_match_not_truth must be true")
    runtime = page.get("runtime_dependency_requirements")
    if not isinstance(runtime, Mapping):
        errors.append("runtime_dependency_requirements must be an object")
    else:
        check_false_map(runtime, {"dependency_resolution_performed", "dependency_safety_claimed", "installability_claimed"}, "runtime_dependency_requirements", errors)
    compat_evidence = page.get("compatibility_evidence_strength")
    if not isinstance(compat_evidence, Mapping) or compat_evidence.get("compatibility_evidence_not_truth") is not True:
        errors.append("compatibility_evidence_strength.compatibility_evidence_not_truth must be true")
    gaps = page.get("incompatibility_and_unknown_gaps")
    if not isinstance(gaps, Mapping) or gaps.get("absence_of_evidence_is_not_incompatibility") is not True:
        errors.append("incompatibility_and_unknown_gaps.absence_of_evidence_is_not_incompatibility must be true")
    caution = page.get("source_provenance_candidate_caution")
    if not isinstance(caution, Mapping):
        errors.append("source_provenance_candidate_caution must be an object")
    else:
        if caution.get("source_trust_claimed") is not False:
            errors.append("source_provenance_candidate_caution.source_trust_claimed must be false")
        check_true(caution, "candidate_confidence_not_truth", "source_provenance_candidate_caution", errors)
        check_true(caution, "provenance_not_truth", "source_provenance_candidate_caution", errors)
    action = page.get("action_safety_installability_caution")
    if not isinstance(action, Mapping):
        errors.append("action_safety_installability_caution must be an object")
    else:
        check_false_map(action, {"downloads_enabled", "installs_enabled", "execution_enabled", "package_manager_invoked", "emulator_launch_enabled", "VM_launch_enabled", "installability_claimed"}, "action_safety_installability_caution", errors)
        check_true(action, "installability_evidence_required", "action_safety_installability_caution", errors)
    rights = page.get("rights_risk")
    if not isinstance(rights, Mapping):
        errors.append("rights_risk must be an object")
    else:
        check_false_map(rights, {"rights_clearance_claimed", "malware_safety_claimed", "dependency_safety_claimed", "rights_risk_score_applied_now"}, "rights_risk", errors)
    tie = page.get("tie_breaks")
    if not isinstance(tie, Mapping):
        errors.append("tie_breaks must be an object")
    else:
        check_false_map(tie, {"random_tie_break_allowed", "tie_break_applied_now"}, "tie_breaks", errors)
    check_public_safe(page, errors)
    if example_root is not None:
        check_checksums(example_root, errors)
    return errors


def example_paths() -> list[tuple[Path, Path]]:
    return [(p, p.parent) for p in sorted(EXAMPLES_ROOT.glob("*/COMPATIBILITY_AWARE_RANKING_ASSESSMENT.json"))]


def validate_all_examples() -> tuple[list[Path], list[str]]:
    paths = example_paths()
    errors: list[str] = []
    for path, root in paths:
        errors.extend(validate_assessment(path, example_root=root))
    return [path for path, _ in paths], errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assessment")
    parser.add_argument("--assessment-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    if args.all_examples:
        paths, errors = validate_all_examples()
    elif args.assessment:
        path = Path(args.assessment)
        root = Path(args.assessment_root) if args.assessment_root else None
        paths, errors = [path], validate_assessment(path, example_root=root)
    else:
        paths, errors = [], ["choose --assessment or --all-examples"]
    status = "invalid" if errors else "valid"
    if args.json:
        print(json.dumps({"status": status, "example_count": len(paths), "validated_paths": [display_path(p, REPO_ROOT) for p in paths], "errors": errors}, indent=2), file=stdout)
    else:
        print(f"status: {status}", file=stdout)
        print(f"example_count: {len(paths)}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
