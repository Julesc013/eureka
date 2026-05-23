#!/usr/bin/env python3
"""Plan the R0-03 contract taxonomy refactor without moving files."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "R0-03A"
AUDIT_DIR = Path("control/audits/r0-03a-contract-taxonomy-refactor-plan-v0")
TAXONOMY_POLICY = Path("control/policies/contract_taxonomy_policy.json")
MIGRATION_POLICY = Path("control/policies/contract_migration_policy.json")
SCHEMA_ROOTS = (Path("contracts"), Path("contracts/schema/control"))

TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".ps1",
    ".py",
    ".rs",
    ".schema",
    ".sh",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

IGNORED_DIRS = {
    ".git",
    ".aide.local",
    ".local",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}

FORBIDDEN_OUTPUT_ROOTS = (
    ".git",
    ".env",
    "contracts",
    "runtime",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
)

APPROVED_REPO_OUTPUT_ROOTS = (
    "control/inventory",
    AUDIT_DIR.as_posix(),
    "docs/architecture",
    "docs/operations",
    "control/policies",
)

CONTRACT_CLASSES = {
    "product_domain_contract",
    "product_runtime_contract",
    "public_api_contract",
    "snapshot_contract",
    "native_contract",
    "durable_store_contract",
    "connector_interface_contract",
    "source_policy_contract",
    "control_schema",
    "audit_schema",
    "fixture_schema",
    "preview_schema",
    "validator_schema",
    "task_queue_schema",
    "generated_scaffold_schema",
    "deprecated_schema",
    "unknown",
}

TARGET_ROOTS = {
    "product_domain_contract": "contracts/domain/",
    "product_runtime_contract": "contracts/runtime/",
    "public_api_contract": "contracts/api/",
    "snapshot_contract": "contracts/snapshot/",
    "native_contract": "contracts/native/",
    "durable_store_contract": "contracts/stores/",
    "connector_interface_contract": "contracts/connectors/",
    "source_policy_contract": "contracts/connectors/",
    "control_schema": "contracts/schema/control/policies/",
    "audit_schema": "contracts/schema/control/audits/",
    "fixture_schema": "contracts/schema/control/fixtures/",
    "preview_schema": "contracts/schema/control/previews/",
    "validator_schema": "contracts/schema/control/validators/",
    "task_queue_schema": "contracts/schema/control/tasks/",
    "generated_scaffold_schema": "contracts/schema/control/deprecated/",
    "deprecated_schema": "contracts/schema/control/deprecated/",
    "unknown": "contracts/schema/control/deprecated/",
}

FORBIDDEN_PRODUCT_SIGNALS = (
    "h0",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "h7",
    "h8",
    "h9",
    "h10",
    "h11",
    "h12",
    "h13",
    "h14",
    "bundle",
    "quality_delta",
    "next_phase",
    "integration_audit",
    "review_integration_result",
    "fixture_replay",
    "prompt",
    "aide",
    "local_mvp",
    "truth_boundary",
    "product_boundary",
)

PHASE_PREFIX_RE = re.compile(r"^(h(?:[0-9]|1[0-4]))[_-](.+)$", re.IGNORECASE)
VERSION_SUFFIX_RE = re.compile(r"\.v\d+(?:\.[^.]+)?$")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--migration-output")
    parser.add_argument("--reference-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-standard-outputs", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    for output in (args.output, args.migration_output, args.reference_output, args.summary_output):
        if output:
            check_output_path(root, Path(output), errors)
    audit = build_contract_taxonomy_audit(root, policy_errors=errors)

    if args.output and not errors:
        write_json(Path(args.output), audit["contract_taxonomy_inventory"])
    if args.migration_output and not errors:
        write_json(Path(args.migration_output), audit["contract_migration_plan"])
    if args.reference_output and not errors:
        write_json(Path(args.reference_output), audit["contract_reference_graph"])
    if args.summary_output and not errors:
        write_text(Path(args.summary_output), render_summary(audit))
    if args.write_standard_outputs and not errors:
        write_standard_outputs(root, audit)

    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True), file=stdout)
    else:
        print(render_console_summary(audit), file=stdout)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=stderr)
        return 1
    return 0


def build_contract_taxonomy_audit(root: Path = REPO_ROOT, policy_errors: Sequence[str] | None = None) -> dict[str, Any]:
    errors = list(policy_errors or [])
    taxonomy_policy = load_json_if_exists(root / TAXONOMY_POLICY, errors)
    migration_policy = load_json_if_exists(root / MIGRATION_POLICY, errors)
    contract_paths = list(iter_contract_files(root))
    reference_graph = build_reference_graph(root, contract_paths)
    references_by_contract: dict[str, list[str]] = defaultdict(list)
    for edge in reference_graph["edges"]:
        references_by_contract[edge["to_path"]].append(edge["from_path"])

    contracts: list[dict[str, Any]] = []
    for path in contract_paths:
        rel = path.relative_to(root).as_posix()
        classification = classify_contract(path, root)
        target_root = TARGET_ROOTS[classification["contract_class"]]
        target_path = propose_target_path(rel, classification["contract_class"], target_root)
        action = recommend_action(rel, target_path, classification)
        refs = sorted(set(references_by_contract.get(rel, [])))
        risks = risks_for(rel, classification, action, refs)
        contracts.append(
            {
                "path": rel,
                "current_root": current_root(rel),
                "contract_class": classification["contract_class"],
                "maturity": classification["maturity"],
                "target_root": target_root,
                "target_path": target_path,
                "recommended_action": action,
                "signals": classification["signals"],
                "references": refs,
                "risks": risks,
                "notes": classification["notes"],
            }
        )

    inventory = build_inventory(contracts, errors)
    migration_plan = build_migration_plan(contracts, reference_graph, migration_policy)
    risk_register = build_risk_register(contracts, migration_plan)
    execution_plan = build_execution_plan(migration_plan, reference_graph)
    report = build_report(inventory, migration_plan, reference_graph, risk_register, execution_plan)
    return {
        "schema_version": "contract_taxonomy_audit.v0",
        "task": TASK_ID,
        "planning_only": True,
        "policy_errors": errors,
        "taxonomy_policy_id": taxonomy_policy.get("policy_id"),
        "migration_policy_id": migration_policy.get("policy_id"),
        "contract_taxonomy_inventory": inventory,
        "contract_migration_plan": migration_plan,
        "contract_reference_graph": reference_graph,
        "contract_risk_register": risk_register,
        "r0_03b_execution_plan": execution_plan,
        "r0_03a_report": report,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "contracts_moved": False,
        "runtime_modified": False,
    }


def load_json_if_exists(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing policy: {path.as_posix()}")
    except json.JSONDecodeError as exc:
        errors.append(f"malformed policy JSON {path.as_posix()}: {exc}")
    return {}


def iter_contract_files(root: Path) -> Iterable[Path]:
    files: dict[str, Path] = {}
    for schema_root in SCHEMA_ROOTS:
        base = root / schema_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and not any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
                if path.name in {".gitkeep", "README.md"}:
                    continue
                files[path.relative_to(root).as_posix()] = path
    return [files[key] for key in sorted(files)]


def classify_contract(path: Path, root: Path) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    lowered = rel.casefold()
    name = path.name.casefold()
    content = read_text(path)
    content_lower = content.casefold()
    size = path.stat().st_size
    signals: list[str] = [f"suffix:{path.suffix.lower() or '<none>'}", f"size:{size}"]
    notes: list[str] = []
    maturity = "stable_boundary_candidate"

    if size == 0:
        signals.append("zero_byte")
        maturity = "empty_or_zero_byte"
    elif is_near_empty(content):
        signals.append("near_empty")
        maturity = "placeholder"
    if "placeholder" in lowered or "placeholder" in content_lower:
        signals.append("placeholder_signal")
        maturity = "placeholder"
    if any(signal in lowered or signal in content_lower for signal in ("truth_boundary", "product_boundary")):
        signals.append("boundary_assertion_signal")
    if has_forbidden_product_signal(lowered):
        signals.append("task_or_bundle_named")

    contract_class = classify_by_path_and_name(rel, name, content_lower, signals)
    if path.suffix.lower() not in {".json", ".yaml", ".yml", ".schema"}:
        if path.name.casefold() == "readme.md":
            contract_class = "unknown"
            maturity = "documentation_only"
            signals.append("readme_under_contracts")
            notes.append("README is contract-adjacent documentation, not a schema contract.")
        else:
            contract_class = "unknown"
            signals.append("non_schema_file")
    if contract_class in {"audit_schema", "fixture_schema", "preview_schema", "task_queue_schema", "generated_scaffold_schema", "deprecated_schema"}:
        if maturity == "stable_boundary_candidate":
            maturity = "control_schema_candidate"
    if contract_class in product_classes() and has_forbidden_product_signal(lowered):
        signals.append("forbidden_product_contract_signal")
        notes.append("Product-looking contract has task, bundle, or audit vocabulary and should be reclassified or renamed.")
    return {"contract_class": contract_class, "maturity": maturity, "signals": sorted(set(signals)), "notes": notes}


def classify_by_path_and_name(rel: str, name: str, content_lower: str, signals: list[str]) -> str:
    lowered = rel.casefold()
    if lowered.startswith("contracts/schema/control/audits/"):
        signals.append("control_schema_audit_path")
        return "audit_schema"
    if lowered.startswith("contracts/schema/control/fixtures/"):
        signals.append("control_schema_fixture_path")
        return "fixture_schema"
    if lowered.startswith("contracts/schema/control/previews/"):
        signals.append("control_schema_preview_path")
        return "preview_schema"
    if lowered.startswith("contracts/schema/control/policies/"):
        signals.append("control_schema_policy_path")
        return "control_schema"
    if lowered.startswith("contracts/schema/control/validators/"):
        signals.append("control_schema_validator_path")
        return "validator_schema"
    if lowered.startswith("contracts/schema/control/tasks/"):
        signals.append("control_schema_task_path")
        return "task_queue_schema"
    if lowered.startswith("contracts/schema/control/deprecated/"):
        signals.append("control_schema_deprecated_path")
        return "deprecated_schema"
    if lowered.startswith("contracts/api/") or lowered.startswith("contracts/gateway/public_api/"):
        signals.append("public_api_path")
        return "public_api_contract"
    if lowered.startswith("contracts/surface/pages/") or lowered.startswith("contracts/search/") or lowered.startswith("contracts/view/pages/") or lowered.startswith("contracts/surface/ui/"):
        signals.append("public_surface_contract_path")
        return "public_api_contract"
    if any(lowered.startswith(prefix) for prefix in ("contracts/evidence/ledger/", "contracts/source/cache/", "contracts/index/master/", "contracts/stores/")):
        signals.append("durable_store_path")
        return "durable_store_contract"
    if any(token in name for token in ("next_phase", "next_task", "queue", "task_decision", "decision_option")):
        signals.append("task_queue_signal")
        return "task_queue_schema"
    if lowered.startswith("contracts/audits/"):
        signals.append("contracts_audits_path")
        if "next" in name or "task" in name:
            return "task_queue_schema"
        return "audit_schema"
    if any(token in name for token in ("fixture_replay", "replay_result", "fixture")):
        signals.append("fixture_schema_signal")
        return "fixture_schema"
    if any(token in name for token in ("quality_delta", "integration_audit", "postmortem", "readiness_audit", "smoke_report", "audit", "signoff", "operator_review", "review_integration_result", "report")):
        signals.append("audit_schema_signal")
        return "audit_schema"
    if lowered.startswith("contracts/runtime/") and name in {"evidence_candidate.v0.json"}:
        signals.append("runtime_contract_path")
        signals.append("candidate_named_product_contract_exception")
        return "product_runtime_contract"
    if any(token in name for token in ("preview", "candidate", "output_bundle", "normalized_record")):
        signals.append("preview_schema_signal")
        return "preview_schema"
    if "live_probe_result" in name and PHASE_PREFIX_RE.match(name):
        signals.append("task_specific_live_probe_result")
        return "preview_schema"
    if "live_probe_request" in name and PHASE_PREFIX_RE.match(name):
        signals.append("task_specific_live_probe_request")
        return "preview_schema"
    if "validator" in name:
        signals.append("validator_schema_signal")
        return "validator_schema"
    if any(token in name for token in ("deprecated", "legacy", "obsolete")):
        signals.append("deprecated_signal")
        return "deprecated_schema"
    if lowered.startswith("contracts/domain/") or lowered.startswith("contracts/identity/") or lowered.startswith("contracts/representation/"):
        signals.append("domain_contract_path")
        return "product_domain_contract"
    if lowered.startswith("contracts/runtime/") or lowered.startswith("contracts/extraction/") or lowered.startswith("contracts/query/"):
        signals.append("runtime_contract_path")
        return "product_runtime_contract"
    if lowered.startswith("contracts/snapshot") or lowered.startswith("contracts/snapshots/") or lowered.startswith("contracts/relay/"):
        signals.append("snapshot_contract_path")
        return "snapshot_contract"
    if lowered.startswith("contracts/native/"):
        signals.append("native_contract_path")
        return "native_contract"
    if any(lowered.startswith(prefix) for prefix in ("contracts/source/registry/", "contracts/source/sync/", "contracts/source/records/", "contracts/archive/")):
        signals.append("source_policy_path")
        return "source_policy_contract"
    if lowered.startswith("contracts/connectors/"):
        if has_forbidden_product_signal(lowered):
            signals.append("connector_task_scaffold")
            if "policy" in name or "approval" in name:
                return "control_schema"
            return "preview_schema"
        signals.append("connector_interface_path")
        return "connector_interface_contract"
    if lowered.startswith("contracts/hosting/") or lowered.startswith("contracts/node/") or lowered.startswith("contracts/pack/") or lowered.startswith("contracts/command/actions/"):
        if any(token in name for token in ("policy", "manifest", "profile", "config", "envelope")):
            signals.append("policy_or_manifest_contract_path")
            return "source_policy_contract"
        signals.append("control_or_hosting_schema_path")
        return "control_schema"
    if "\"type\"" in content_lower or "$schema" in content_lower:
        signals.append("json_schema_like")
        return "product_domain_contract"
    return "unknown"


def product_classes() -> set[str]:
    return {
        "product_domain_contract",
        "product_runtime_contract",
        "public_api_contract",
        "snapshot_contract",
        "native_contract",
        "durable_store_contract",
        "connector_interface_contract",
        "source_policy_contract",
    }


def has_forbidden_product_signal(text: str) -> bool:
    return any(re.search(rf"(?<![a-z0-9]){re.escape(signal)}(?![a-z0-9])", text, re.IGNORECASE) for signal in FORBIDDEN_PRODUCT_SIGNALS)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def is_near_empty(content: str) -> bool:
    stripped = content.strip()
    return stripped in {"", "{}", "[]"} or len(stripped) < 12


def current_root(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "control" and parts[1] == "schemas":
        return "/".join(parts[:3]) + "/"
    if len(parts) >= 2:
        return "/".join(parts[:2]) + "/"
    return parts[0] + "/"


def propose_target_path(rel: str, contract_class: str, target_root: str) -> str:
    if rel.startswith(target_root):
        return rel
    if contract_class in product_classes():
        if rel.startswith(target_root):
            return rel
        return target_root + "/".join(rel.split("/")[2:])
    file_name = rel.split("/")[-1]
    subdir = rel.split("/")[1] if "/" in rel else "root"
    renamed = normalized_control_filename(file_name)
    phase = phase_prefix(file_name)
    if phase:
        return f"{target_root}{phase}/{subdir}/{renamed}"
    return f"{target_root}{subdir}/{renamed}"


def normalized_control_filename(file_name: str) -> str:
    match = PHASE_PREFIX_RE.match(file_name)
    if match:
        return match.group(2)
    return file_name


def phase_prefix(file_name: str) -> str:
    match = PHASE_PREFIX_RE.match(file_name)
    return match.group(1).lower() if match else ""


def recommend_action(rel: str, target_path: str, classification: Mapping[str, Any]) -> str:
    contract_class = str(classification["contract_class"])
    signals = set(classification.get("signals", []))
    if "zero_byte" in signals or "near_empty" in signals:
        return "delete_later_if_unreferenced"
    if contract_class == "unknown":
        return "investigate"
    if contract_class in {"generated_scaffold_schema", "deprecated_schema"}:
        return "quarantine"
    if rel == target_path:
        if "forbidden_product_contract_signal" in signals:
            return "rename"
        return "keep"
    if normalized_control_filename(rel.split("/")[-1]) != rel.split("/")[-1]:
        return "move_and_rename"
    return "move"


def risks_for(rel: str, classification: Mapping[str, Any], action: str, refs: Sequence[str]) -> list[str]:
    risks: list[str] = []
    if action in {"move", "rename", "move_and_rename"} and refs:
        risks.append("references_require_update")
    if action in {"move", "move_and_rename"}:
        risks.append("compatibility_shim_required")
    if classification["contract_class"] == "unknown":
        risks.append("classification_uncertain")
    if "forbidden_product_contract_signal" in classification.get("signals", []):
        risks.append("task_vocabulary_in_product_contract")
    if action == "delete_later_if_unreferenced":
        risks.append("delete_only_after_reference_audit")
    return risks


def build_inventory(contracts: Sequence[Mapping[str, Any]], warnings: Sequence[str]) -> dict[str, Any]:
    counts = {
        "contract_class": dict(sorted(Counter(str(item["contract_class"]) for item in contracts).items())),
        "recommended_action": dict(sorted(Counter(str(item["recommended_action"]) for item in contracts).items())),
        "maturity": dict(sorted(Counter(str(item["maturity"]) for item in contracts).items())),
    }
    return {
        "schema_version": "contract_taxonomy_inventory.v0",
        "generated_for": TASK_ID,
        "contract_count": len(contracts),
        "contracts": list(contracts),
        "counts": counts,
        "warnings": list(warnings),
        "limitations": [
            "Static classification only; R0-03A does not move or delete files.",
            "Reference graph is path-literal based and may miss dynamically constructed paths.",
            "Runtime consumption is inferred from static references only.",
        ],
    }


def build_migration_plan(contracts: Sequence[Mapping[str, Any]], reference_graph: Mapping[str, Any], migration_policy: Mapping[str, Any]) -> dict[str, Any]:
    move_actions = {"move", "rename", "move_and_rename", "deprecate", "quarantine", "investigate"}
    moves = []
    do_not_move = []
    do_not_delete = []
    blocked_items = []
    edges_by_target = defaultdict(list)
    for edge in reference_graph["edges"]:
        edges_by_target[edge["to_path"]].append(edge)
    for item in contracts:
        action = str(item["recommended_action"])
        if action in move_actions:
            risk = risk_level(item, action)
            moves.append(
                {
                    "source_path": item["path"],
                    "target_path": item["target_path"],
                    "action": action,
                    "contract_class_before": item["contract_class"],
                    "contract_class_after": item["contract_class"],
                    "rationale": rationale_for(item, action),
                    "references_to_update": sorted({edge["from_path"] for edge in edges_by_target.get(item["path"], [])}),
                    "compatibility_shim_required": action in {"move", "rename", "move_and_rename", "deprecate", "quarantine"},
                    "risk": risk,
                    "validation": validation_for(item, action),
                }
            )
        elif action == "delete_later_if_unreferenced":
            do_not_delete.append({"path": item["path"], "reason": "Deletion is forbidden in R0-03A and must be preceded by quarantine/reference audit."})
        else:
            do_not_move.append({"path": item["path"], "reason": "Already fits R0-03A target taxonomy or requires no move."})
        if action == "investigate":
            blocked_items.append({"path": item["path"], "reason": "Unknown classification must be reviewed before execution."})
    return {
        "schema_version": "contract_migration_plan.v0",
        "generated_for": TASK_ID,
        "migration_allowed_now": False,
        "r0_03b_ready": True,
        "moves": moves,
        "do_not_move": do_not_move,
        "do_not_delete": do_not_delete,
        "blocked_items": blocked_items,
        "policy": {
            "planning_only_current": migration_policy.get("planning_only_current", True),
            "compatibility_shims_required": migration_policy.get("compatibility_shims_required", True),
            "deletion_allowed_current": migration_policy.get("deletion_allowed_current", False),
        },
    }


def risk_level(item: Mapping[str, Any], action: str) -> str:
    refs = item.get("references", [])
    if action == "investigate":
        return "high"
    if len(refs) > 20:
        return "high"
    if action in {"move_and_rename", "rename"}:
        return "high" if refs else "medium"
    if action in {"move", "quarantine", "deprecate"}:
        return "medium" if refs else "low"
    return "low"


def rationale_for(item: Mapping[str, Any], action: str) -> str:
    if action == "investigate":
        return "Contract-like artifact could not be safely classified by static rules."
    if action == "quarantine":
        return "Artifact is generated, deprecated, or unsafe to keep as a product contract without review."
    if action == "rename":
        return "Artifact stays in a product root but must remove task/bundle vocabulary."
    if action == "move_and_rename":
        return "Artifact belongs under contracts/schema/control and should drop task-phase prefix from the filename."
    if action == "move":
        return "Artifact is a control/audit/fixture/preview schema or belongs under a different product target root."
    return "No migration action required."


def validation_for(item: Mapping[str, Any], action: str) -> list[str]:
    commands = [
        "python scripts/validate_contract_taxonomy_plan.py",
        "python scripts/validate_runtime_architecture_leakage.py",
        "python -m unittest tests.operations.test_contract_taxonomy_plan",
    ]
    if action in {"move", "rename", "move_and_rename", "quarantine", "deprecate"}:
        commands.append("python -m unittest discover -s tests -t .")
    return commands


def build_reference_graph(root: Path, contract_paths: Sequence[Path]) -> dict[str, Any]:
    contract_rels = [path.relative_to(root).as_posix() for path in contract_paths]
    contract_set = set(contract_rels)
    basename_map: dict[str, list[str]] = defaultdict(list)
    for rel in contract_rels:
        basename_map[Path(rel).name].append(rel)
    scan_roots = ("contracts", "contracts/schema/control", "control/audits", "examples", "scripts", "tests", "runtime")
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for path in iter_reference_files(root, scan_roots):
        from_rel = path.relative_to(root).as_posix()
        text = read_text(path)
        candidates = set(find_contract_path_literals(text))
        for basename, rels in basename_map.items():
            if basename in text:
                candidates.update(rels)
        for candidate in candidates:
            normalized = candidate.replace("\\", "/").lstrip("./")
            if normalized not in contract_set:
                continue
            edge_kind = edge_kind_for(from_rel, text)
            key = (from_rel, normalized, edge_kind)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append({"from_path": from_rel, "to_path": normalized, "edge_kind": edge_kind})
    nodes = [{"path": rel, "node_kind": "contract"} for rel in contract_rels]
    ref_nodes = sorted({edge["from_path"] for edge in edges if edge["from_path"] not in contract_set})
    nodes.extend({"path": rel, "node_kind": "reference_source"} for rel in ref_nodes)
    return {
        "schema_version": "contract_reference_graph.v0",
        "generated_for": TASK_ID,
        "nodes": nodes,
        "edges": sorted(edges, key=lambda item: (item["to_path"], item["from_path"], item["edge_kind"])),
    }


def iter_reference_files(root: Path, scan_roots: Sequence[str]) -> Iterable[Path]:
    files: list[Path] = []
    for scan_root in scan_roots:
        base = root / scan_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            files.append(path)
    return files


def find_contract_path_literals(text: str) -> Iterable[str]:
    pattern = re.compile(r"(?:contracts|control[/\\]schemas)[/\\][A-Za-z0-9_./\\-]+")
    for match in pattern.finditer(text):
        yield match.group(0).strip("`'\"),.;:")


def edge_kind_for(from_rel: str, text: str) -> str:
    lowered = from_rel.casefold()
    text_lower = text.casefold()
    if lowered.startswith("tests/"):
        return "validates"
    if lowered.startswith("examples/"):
        return "example_of"
    if "import " in text_lower or "from " in text_lower:
        return "imports"
    if lowered.endswith(".md"):
        return "documents"
    if "validate" in lowered:
        return "validates"
    return "references"


def build_risk_register(contracts: Sequence[Mapping[str, Any]], migration_plan: Mapping[str, Any]) -> dict[str, Any]:
    risks: list[dict[str, Any]] = []
    index = 1
    for item in contracts:
        action = item["recommended_action"]
        if action == "keep" and not item.get("risks"):
            continue
        severity = "low"
        if action in {"move_and_rename", "rename", "investigate"}:
            severity = "high"
        elif action in {"move", "quarantine", "delete_later_if_unreferenced"}:
            severity = "medium"
        risks.append(
            {
                "risk_id": f"R0-CONTRACT-RISK-{index:03d}",
                "severity": severity,
                "path": item["path"],
                "finding": f"{item['contract_class']} recommends {action}",
                "impact": impact_for(item),
                "recommended_fix": fix_for(item),
                "blocks": ["F0-BUNDLE-01", "DEV-TO-MAIN-PRODUCTION-REVIEW"],
            }
        )
        index += 1
    return {"schema_version": "contract_risk_register.v0", "generated_for": TASK_ID, "risks": risks}


def impact_for(item: Mapping[str, Any]) -> str:
    if item["contract_class"] in product_classes() and "task_vocabulary_in_product_contract" in item.get("risks", []):
        return "Task vocabulary can leak into product API or runtime semantics."
    if item["recommended_action"] in {"move", "move_and_rename"}:
        return "References and validators can break if R0-03B moves the file without updates."
    if item["recommended_action"] == "investigate":
        return "Execution cannot safely move or keep this artifact without human review."
    return "Low direct product impact, but classification should remain explicit."


def fix_for(item: Mapping[str, Any]) -> str:
    if item["recommended_action"] == "investigate":
        return "Review manually and assign a concrete target class before moving."
    if item["recommended_action"] == "delete_later_if_unreferenced":
        return "Quarantine first, prove no references remain, then delete in a later task."
    return f"Apply R0-03B plan: {item['recommended_action']} to {item['target_path']} and update references."


def build_execution_plan(migration_plan: Mapping[str, Any], reference_graph: Mapping[str, Any]) -> dict[str, Any]:
    moves = migration_plan["moves"]
    ref_updates = sorted({edge["from_path"] for edge in reference_graph["edges"]})
    task_size = "one_shot" if len(moves) <= 40 and len(ref_updates) <= 20 else "two_shot_required"
    batches = [
        {
            "batch_id": "R0-03B-1",
            "purpose": "Create contracts/schema/control target roots and move audit, fixture, preview, task, validator, deprecated, and generated scaffold schemas.",
            "moves": [move for move in moves if str(move["target_path"]).startswith("contracts/schema/control/")],
            "reference_updates": [],
            "validation_commands": [
                "python scripts/audit_contract_taxonomy.py --check --json",
                "python scripts/validate_contract_taxonomy_plan.py",
                "python scripts/validate_runtime_architecture_leakage.py",
            ],
        },
        {
            "batch_id": "R0-03B-2",
            "purpose": "Update references and validators that point at moved schemas.",
            "moves": [],
            "reference_updates": ref_updates,
            "validation_commands": [
                "python -m unittest tests.operations.test_contract_taxonomy_plan",
                "python -m unittest discover -s tests -t .",
            ],
        },
        {
            "batch_id": "R0-03B-3",
            "purpose": "Clean up product contract placement and compatibility aliases after control schemas move.",
            "moves": [move for move in moves if str(move["target_path"]).startswith("contracts/")],
            "reference_updates": ref_updates,
            "validation_commands": [
                "python scripts/check_architecture_boundaries.py",
                "python scripts/validate_runtime_architecture_leakage.py",
                "python scripts/validate_contract_taxonomy_plan.py",
            ],
        },
    ]
    return {
        "schema_version": "r0_03b_execution_plan.v0",
        "ready": True,
        "recommended_next_task": "R0-03B — Contract taxonomy refactor execution",
        "max_expected_changed_files": len(moves) + len(ref_updates),
        "task_size": task_size,
        "execution_batches": batches,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def build_report(
    inventory: Mapping[str, Any],
    migration_plan: Mapping[str, Any],
    reference_graph: Mapping[str, Any],
    risk_register: Mapping[str, Any],
    execution_plan: Mapping[str, Any],
) -> dict[str, Any]:
    counts = inventory["counts"]["contract_class"]
    action_counts = inventory["counts"]["recommended_action"]
    product_count = sum(counts.get(item, 0) for item in product_classes())
    control_count = sum(counts.get(item, 0) for item in ("control_schema", "validator_schema", "task_queue_schema", "generated_scaffold_schema", "deprecated_schema"))
    status = "pass_with_warnings" if migration_plan["moves"] or counts.get("unknown", 0) else "pass"
    return {
        "schema_version": "r0_03a_report.v0",
        "status": status,
        "task": TASK_ID,
        "purpose": "contract_taxonomy_refactor_plan",
        "planning_only": True,
        "contracts_moved": False,
        "runtime_modified": False,
        "contract_count": inventory["contract_count"],
        "product_contract_count": product_count,
        "control_schema_count": control_count,
        "audit_schema_count": counts.get("audit_schema", 0),
        "fixture_schema_count": counts.get("fixture_schema", 0),
        "preview_schema_count": counts.get("preview_schema", 0),
        "unknown_count": counts.get("unknown", 0),
        "move_candidate_count": action_counts.get("move", 0) + action_counts.get("move_and_rename", 0),
        "rename_candidate_count": action_counts.get("rename", 0) + action_counts.get("move_and_rename", 0),
        "quarantine_candidate_count": action_counts.get("quarantine", 0),
        "delete_later_candidate_count": action_counts.get("delete_later_if_unreferenced", 0),
        "reference_edge_count": len(reference_graph["edges"]),
        "r0_03b_ready": execution_plan["ready"],
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03B — Contract taxonomy refactor execution",
        "validation": {},
    }


def check_output_path(root: Path, output: Path, errors: list[str]) -> None:
    candidate = output if output.is_absolute() else root / output
    try:
        resolved = candidate.resolve()
    except OSError:
        resolved = candidate.absolute()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError:
        return
    for forbidden in FORBIDDEN_OUTPUT_ROOTS:
        if relative == forbidden or relative.startswith(forbidden.rstrip("/") + "/"):
            errors.append(f"refusing forbidden output root: {relative}")
            return
    if not any(relative == prefix or relative.startswith(prefix.rstrip("/") + "/") for prefix in APPROVED_REPO_OUTPUT_ROOTS):
        errors.append(f"refusing repo output outside approved R0-03A paths: {relative}")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def write_standard_outputs(root: Path, audit: Mapping[str, Any]) -> None:
    outputs = {
        "control/inventory/contract_taxonomy_inventory.json": audit["contract_taxonomy_inventory"],
        "control/inventory/contract_migration_plan.json": audit["contract_migration_plan"],
        "control/inventory/contract_reference_graph.json": audit["contract_reference_graph"],
        "control/inventory/contract_risk_register.json": audit["contract_risk_register"],
        "control/inventory/r0_03b_execution_plan.json": audit["r0_03b_execution_plan"],
        f"{AUDIT_DIR.as_posix()}/r0_03a_report.json": audit["r0_03a_report"],
        f"{AUDIT_DIR.as_posix()}/generated/sample_contract_taxonomy_inventory.json": audit["contract_taxonomy_inventory"],
        f"{AUDIT_DIR.as_posix()}/generated/sample_contract_migration_plan.json": audit["contract_migration_plan"],
        f"{AUDIT_DIR.as_posix()}/generated/sample_contract_reference_graph.json": audit["contract_reference_graph"],
    }
    for rel, payload in outputs.items():
        write_json(root / rel, payload)
    markdown_outputs = {
        f"{AUDIT_DIR.as_posix()}/README.md": "# R0-03A Contract Taxonomy Refactor Plan\n\nPlanning-only audit pack for contract taxonomy refactor preparation.\n",
        f"{AUDIT_DIR.as_posix()}/contract_taxonomy_summary.md": render_summary(audit),
        f"{AUDIT_DIR.as_posix()}/product_contract_summary.md": render_class_summary(audit, product_classes(), "Product Contract Summary"),
        f"{AUDIT_DIR.as_posix()}/control_schema_summary.md": render_class_summary(audit, {"control_schema", "validator_schema", "task_queue_schema", "generated_scaffold_schema", "deprecated_schema"}, "Control Schema Summary"),
        f"{AUDIT_DIR.as_posix()}/fixture_schema_summary.md": render_class_summary(audit, {"fixture_schema"}, "Fixture Schema Summary"),
        f"{AUDIT_DIR.as_posix()}/audit_schema_summary.md": render_class_summary(audit, {"audit_schema"}, "Audit Schema Summary"),
        f"{AUDIT_DIR.as_posix()}/preview_schema_summary.md": render_class_summary(audit, {"preview_schema"}, "Preview Schema Summary"),
        f"{AUDIT_DIR.as_posix()}/migration_plan_summary.md": render_migration_summary(audit),
        f"{AUDIT_DIR.as_posix()}/reference_graph_summary.md": render_reference_summary(audit),
        f"{AUDIT_DIR.as_posix()}/risk_register.md": render_risk_summary(audit),
        f"{AUDIT_DIR.as_posix()}/r0_03b_execution_plan.md": render_execution_summary(audit),
        f"{AUDIT_DIR.as_posix()}/validation.md": "# Validation\n\nValidation commands are recorded after R0-03A checks run.\n",
        f"{AUDIT_DIR.as_posix()}/generated/sample_summary.md": render_summary(audit),
    }
    for rel, payload in markdown_outputs.items():
        write_text(root / rel, payload)


def render_console_summary(audit: Mapping[str, Any]) -> str:
    report = audit["r0_03a_report"]
    return "\n".join(
        [
            "R0-03A contract taxonomy refactor plan",
            f"status: {report['status']}",
            f"contract_count: {report['contract_count']}",
            f"product_contract_count: {report['product_contract_count']}",
            f"audit_schema_count: {report['audit_schema_count']}",
            f"fixture_schema_count: {report['fixture_schema_count']}",
            f"preview_schema_count: {report['preview_schema_count']}",
            f"move_candidate_count: {report['move_candidate_count']}",
            "planning_only: true",
            "contracts_moved: false",
            "runtime_modified: false",
            "f0_should_remain_blocked: true",
            "dev_to_main_should_remain_blocked: true",
        ]
    )


def render_summary(audit: Mapping[str, Any]) -> str:
    report = audit["r0_03a_report"]
    inventory = audit["contract_taxonomy_inventory"]
    lines = [
        "# Contract Taxonomy Summary",
        "",
        f"- status: {report['status']}",
        f"- contract count: {report['contract_count']}",
        f"- product contracts: {report['product_contract_count']}",
        f"- control schemas: {report['control_schema_count']}",
        f"- audit schemas: {report['audit_schema_count']}",
        f"- fixture schemas: {report['fixture_schema_count']}",
        f"- preview schemas: {report['preview_schema_count']}",
        f"- unknown: {report['unknown_count']}",
        f"- move candidates: {report['move_candidate_count']}",
        f"- reference edges: {report['reference_edge_count']}",
        "- planning only: true",
        "- F0 remains blocked: true",
        "- dev-to-main remains blocked: true",
        "",
        "## Contract Classes",
        "",
    ]
    for key, count in inventory["counts"]["contract_class"].items():
        lines.append(f"- {key}: {count}")
    return "\n".join(lines) + "\n"


def render_class_summary(audit: Mapping[str, Any], classes: set[str], title: str) -> str:
    contracts = [item for item in audit["contract_taxonomy_inventory"]["contracts"] if item["contract_class"] in classes]
    lines = [f"# {title}", "", f"count: {len(contracts)}", ""]
    for item in contracts[:200]:
        lines.append(f"- {item['path']} -> {item['target_path']} ({item['recommended_action']})")
    if len(contracts) > 200:
        lines.append(f"- ... {len(contracts) - 200} additional entries in JSON inventory.")
    return "\n".join(lines) + "\n"


def render_migration_summary(audit: Mapping[str, Any]) -> str:
    plan = audit["contract_migration_plan"]
    lines = ["# Migration Plan Summary", "", f"migration allowed now: {str(plan['migration_allowed_now']).lower()}", f"R0-03B ready: {str(plan['r0_03b_ready']).lower()}", f"move records: {len(plan['moves'])}", ""]
    for item in plan["moves"][:200]:
        lines.append(f"- {item['action']}: {item['source_path']} -> {item['target_path']} ({item['risk']})")
    if len(plan["moves"]) > 200:
        lines.append(f"- ... {len(plan['moves']) - 200} additional move records in JSON plan.")
    return "\n".join(lines) + "\n"


def render_reference_summary(audit: Mapping[str, Any]) -> str:
    graph = audit["contract_reference_graph"]
    top_targets = Counter(edge["to_path"] for edge in graph["edges"]).most_common(20)
    lines = ["# Reference Graph Summary", "", f"nodes: {len(graph['nodes'])}", f"edges: {len(graph['edges'])}", "", "## Top Referenced Contracts", ""]
    for path, count in top_targets:
        lines.append(f"- {path}: {count}")
    return "\n".join(lines) + "\n"


def render_risk_summary(audit: Mapping[str, Any]) -> str:
    risks = audit["contract_risk_register"]["risks"]
    lines = ["# Risk Register", "", f"risk count: {len(risks)}", ""]
    for risk in risks[:200]:
        lines.append(f"- {risk['risk_id']} {risk['severity']}: {risk['path']} - {risk['finding']}")
    if len(risks) > 200:
        lines.append(f"- ... {len(risks) - 200} additional risks in JSON register.")
    return "\n".join(lines) + "\n"


def render_execution_summary(audit: Mapping[str, Any]) -> str:
    plan = audit["r0_03b_execution_plan"]
    lines = ["# R0-03B Execution Plan", "", f"ready: {str(plan['ready']).lower()}", f"task size: {plan['task_size']}", f"max expected changed files: {plan['max_expected_changed_files']}", ""]
    for batch in plan["execution_batches"]:
        lines.append(f"## {batch['batch_id']}")
        lines.append("")
        lines.append(batch["purpose"])
        lines.append("")
        lines.append(f"- moves: {len(batch['moves'])}")
        lines.append(f"- reference updates: {len(batch['reference_updates'])}")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
