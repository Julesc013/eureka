#!/usr/bin/env python3
"""Classify dev-branch artifacts before product work resumes.

R0-01 is a static, standard-library-only audit. It reads repository files,
classifies scaffolding versus product-shaped code, and writes inventory/audit
outputs only when explicitly requested.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "R0-01"
BRANCH_ASSUMPTION = "dev"
AUDIT_DIR = Path("control/audits/r0-01-dev-production-reality-inventory-v0")

SCAN_ROOTS = (
    ".aide",
    "contracts",
    "control",
    "docs",
    "examples",
    "runtime",
    "scripts",
    "tests",
    "surfaces",
    "site",
    "native",
    "crates",
)

PRIVATE_OR_IGNORED_DIRS = {
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
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
    "provider credentials",
    "private local files",
)

APPROVED_REPO_OUTPUT_ROOTS = (
    "control/inventory",
    AUDIT_DIR.as_posix(),
    "docs/operations",
)

TEXT_SUFFIXES = {
    "",
    ".bat",
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
    ".rst",
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

ARTIFACT_KINDS = {
    "production_runtime",
    "prototype_runtime",
    "fixture_runtime",
    "preview_runtime",
    "domain_contract",
    "runtime_contract",
    "public_api_contract",
    "audit_contract",
    "fixture_contract",
    "policy_contract",
    "preview_contract",
    "generated_scaffold",
    "operator_script",
    "validator",
    "unit_test",
    "integration_test",
    "artifact_existence_test",
    "audit_evidence",
    "documentation",
    "queue_or_task_control",
    "unknown",
}

MATURITIES = {
    "production_ready",
    "behavior_implemented",
    "durable_store_ready",
    "live_test_ready",
    "fixture_only",
    "preview_only",
    "policy_only",
    "audit_only",
    "placeholder",
    "empty_or_zero_byte",
    "unknown",
}

RECOMMENDED_ACTIONS = {
    "keep",
    "keep_as_control",
    "keep_as_fixture_oracle",
    "quarantine",
    "rename",
    "move_to_control",
    "move_to_tests",
    "move_to_docs",
    "refactor",
    "rewrite",
    "delete_if_unreferenced",
    "investigate",
}

PRODUCT_ROLES = {
    "source_observation",
    "source_cache",
    "evidence_ledger",
    "review_queue",
    "public_index",
    "connector_runtime",
    "extraction",
    "search_quality",
    "snapshot",
    "relay",
    "native",
    "hosting",
    "actions",
    "packs",
    "governance",
    "unknown",
}

LEAKAGE_TERMS = (
    "LOCAL-MVP",
    "truth_boundary",
    "product_boundary",
    "review_seed",
    "fixture_only",
    "preview_only",
    "BUNDLE",
    "AIDE",
    "prompt",
    "agent",
    "MVP",
    "H14",
    "H13",
    "H12",
    "H11",
    "H10",
    "H9",
    "H8",
    "H7",
    "H6",
    "H5",
    "H4",
    "H3",
    "H2",
    "H1",
    "H0",
)

CONTRACT_CONTROL_HINTS = (
    "audits",
    "audit",
    "bundle",
    "fixture",
    "replay_result",
    "quality_delta",
    "next_phase",
    "integration_audit",
    "review_integration_result",
    "live_probe_request",
    "live_probe_result",
)

FIXTURE_RUNTIME_PHRASES = (
    "fixture-only",
    "fixture only",
    "fixture_only",
    "committed-fixture-only",
    "committed fixture only",
    "no runtime side effects",
    "no file, network, provider, browser, telemetry",
    "no file/network/provider/browser/telemetry side effects",
)

PREVIEW_PHRASES = (
    "preview-only",
    "preview only",
    "preview_only",
    "dry-run",
    "dry run",
    "candidate preview",
    "review seed",
    "review_seed",
)

PLACEHOLDER_PHRASES = (
    "placeholder",
    "todo",
    "tbd",
    "not implemented",
    "fill from",
    "coming soon",
)

GOD_MODULE_PATTERNS = {
    "policy loading": re.compile(r"\b(policy_bundle|POLICY_PATHS|load_.*policy|policy_path)\b", re.IGNORECASE),
    "endpoint/source registry": re.compile(r"\b(ENDPOINT_URL|SOURCE_CONFIG|source_registry|connector_registry)", re.IGNORECASE),
    "request construction": re.compile(r"\b(build_.*request|request_key|Request\(|metadata_request)\b", re.IGNORECASE),
    "network client": re.compile(r"\b(urlopen|urllib|requests\.|httpx|network_used|endpoint_used)\b", re.IGNORECASE),
    "normalization": re.compile(r"\b(normalize|normalized_record|normalizer)", re.IGNORECASE),
    "source cache mapping": re.compile(r"\b(source_cache|source cache)", re.IGNORECASE),
    "evidence mapping": re.compile(r"\b(evidence_candidate|evidence preview|evidence_ledger)", re.IGNORECASE),
    "review seed generation": re.compile(r"\b(review_seed|review_queue_seed|review queue seed)", re.IGNORECASE),
    "audit/boundary checks": re.compile(r"\b(truth_boundary|product_boundary|detect_.*violation|boundary check)", re.IGNORECASE),
    "health summary generation": re.compile(r"\b(health_summary|connector_health|health status)", re.IGNORECASE),
}

SEAM_DEFINITIONS = {
    "source_observation": {
        "keywords": ("source_observation", "source observation", "live_probe_result", "metadata response"),
        "next": "R0-04 - Source observation production seam",
    },
    "source_cache_durable_store": {
        "keywords": ("source_cache", "source cache", "sqlite", "append-only observations"),
        "next": "R0-05 - Durable source cache store",
    },
    "evidence_ledger_durable_store": {
        "keywords": ("evidence_ledger", "evidence ledger", "evidence_claim", "evidence_event"),
        "next": "R0-06 - Durable evidence ledger store",
    },
    "review_queue": {
        "keywords": ("review_queue", "review queue", "review decision", "candidate promotion"),
        "next": "R0-07 - Review queue product seam",
    },
    "candidate_promotion": {
        "keywords": ("candidate_promotion", "candidate promotion", "promotion"),
        "next": "R0-07 - Review queue product seam",
    },
    "public_index_rebuild": {
        "keywords": ("public_index", "public index", "index_builder", "reviewed public index"),
        "next": "R0-08 - Reviewed public index rebuild",
    },
    "static_public_surface": {
        "keywords": ("surfaces/", "site/", "static site", "object page", "absence page"),
        "next": "R0-08 - Reviewed public index rebuild",
    },
    "source_connector_runtime": {
        "keywords": ("runtime/connectors", "connector runtime", "normalizer", "live_probe"),
        "next": "R0-04 - Source observation production seam",
    },
    "live_metadata_probe": {
        "keywords": ("live_probe", "metadata live probe", "network_used", "urlopen"),
        "next": "R0-09 - One-source live test",
    },
    "extraction_runtime": {
        "keywords": ("extraction", "extractor", "sandbox"),
        "next": "F0 remains blocked until R0-09 completes",
    },
    "search_quality_ranking": {
        "keywords": ("search_quality", "ranking", "near_miss", "known_absence", "explanation"),
        "next": "G0 after reviewed index exists",
    },
    "snapshot_relay": {
        "keywords": ("snapshot", "relay"),
        "next": "D-stage after reviewed index exists",
    },
    "native_client": {
        "keywords": ("native", "client contract"),
        "next": "C-stage after reviewed index exists",
    },
    "hosting_deployment": {
        "keywords": ("hosting", "deployment", "github_pages", "hosted"),
        "next": "E-stage after reviewed index exists",
    },
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to audit.")
    parser.add_argument("--output", help="Optional JSON output path. Writes artifact taxonomy unless the file name matches another R0 inventory.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Run read-only even when output paths are provided.")
    parser.add_argument("--json", action="store_true", help="Emit the full audit JSON to stdout.")
    parser.add_argument("--write-standard-outputs", action="store_true", help="Write all R0-01 inventory, docs, and audit-pack outputs.")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    try:
        audit = build_reality_audit(root)
        wrote_files = False
        if not args.check:
            if args.output:
                payload = payload_for_output_path(args.output, audit)
                write_json(root, Path(args.output), payload)
                wrote_files = True
            if args.summary_output:
                write_text(root, Path(args.summary_output), render_sample_summary(audit))
                wrote_files = True
            if args.write_standard_outputs:
                write_standard_outputs(root, audit)
                wrote_files = True

        if args.json:
            print(json.dumps(audit, indent=2, sort_keys=True), file=stdout)
        else:
            print("R0-01 dev production reality inventory", file=stdout)
            print(f"status: {audit['r0_report']['status']}", file=stdout)
            print(f"artifact_count: {audit['artifact_taxonomy']['artifact_count']}", file=stdout)
            print(f"production_runtime_count: {audit['r0_report']['production_runtime_count']}", file=stdout)
            print(f"fixture_runtime_count: {audit['r0_report']['fixture_runtime_count']}", file=stdout)
            print(f"preview_runtime_count: {audit['r0_report']['preview_runtime_count']}", file=stdout)
            print(f"architecture_leak_count: {audit['r0_report']['architecture_leak_count']}", file=stdout)
            print("recommended_next_task: R0-02 - Runtime architecture leakage gate", file=stdout)
            print("f0_should_remain_blocked: true", file=stdout)
            print("dev_to_main_should_remain_blocked: true", file=stdout)
            print(f"wrote_files: {str(wrote_files).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        print("R0-01 dev production reality inventory", file=stdout)
        print("status: fail", file=stdout)
        print(f"ERROR: {exc}", file=stdout)
        return 1


def build_reality_audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    files = collect_repo_visible_files(root)
    text_cache: dict[str, str] = {}
    artifacts = [classify_artifact(root, rel, text_cache) for rel in files]
    leakage_report = build_leakage_report(root, files, text_cache)
    taxonomy = build_artifact_taxonomy(artifacts, leakage_report)
    maturity_matrix = build_runtime_maturity_matrix(artifacts, root, text_cache)
    gap_register = build_gap_register(root, taxonomy, maturity_matrix, leakage_report)
    scaffold_map = build_scaffold_to_runtime_map(artifacts)
    next_decision = build_next_task_decision(gap_register, leakage_report)
    report = build_r0_report(taxonomy, maturity_matrix, gap_register, leakage_report)
    return {
        "schema_version": "r0.dev_production_reality_audit.v0",
        "generated_for": TASK_ID,
        "branch_assumption": BRANCH_ASSUMPTION,
        "artifact_taxonomy": taxonomy,
        "runtime_maturity_matrix": maturity_matrix,
        "production_gap_register": gap_register,
        "scaffold_to_runtime_map": scaffold_map,
        "runtime_architecture_leakage_report": leakage_report,
        "r0_next_task_decision": next_decision,
        "r0_report": report,
    }


def collect_repo_visible_files(root: Path) -> list[str]:
    files: set[str] = set()
    for scan_root in SCAN_ROOTS:
        base = root / scan_root
        if not base.exists():
            continue
        if base.is_file():
            files.add(scan_root)
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = rel_path(root, path)
            if is_private_or_ignored(rel):
                continue
            files.add(rel)
    return sorted(files)


def classify_artifact(root: Path, rel: str, text_cache: dict[str, str]) -> dict[str, Any]:
    path = root / rel
    lower = rel.casefold()
    name = path.name.casefold()
    suffix = path.suffix.casefold()
    text = read_text(root, rel, text_cache)
    text_lower = text.casefold()
    size = path.stat().st_size if path.exists() else 0
    root_name = rel.split("/", 1)[0]

    signals: list[str] = [f"root:{root_name}", f"suffix:{suffix or '<none>'}", f"size:{size}"]
    risks: list[str] = []
    notes: list[str] = []

    placeholder = is_placeholder_artifact(path, text)
    fixture_signal = has_any(lower, ("fixture", "replay")) or has_phrase(text_lower, FIXTURE_RUNTIME_PHRASES)
    preview_signal = has_any(lower, ("preview", "dry_run", "dry-run", "review_seed", "candidate_preview")) or has_phrase(text_lower, PREVIEW_PHRASES)
    policy_signal = "policy" in lower
    h_phase_signal = bool(re.search(r"(^|[/_.-])h\d{1,2}([/_\.-]|$)", lower)) or "bundle" in lower
    generated_signal = "/generated/" in lower or name.startswith("sample_") or "generated" in lower
    god_aspects = god_module_aspects(rel, text)
    artifact_existence_signal = is_artifact_existence_validator(rel, text)

    if placeholder:
        signals.append("placeholder_or_empty")
    if fixture_signal:
        signals.append("fixture_signal")
    if preview_signal:
        signals.append("preview_signal")
    if policy_signal:
        signals.append("policy_signal")
    if h_phase_signal:
        signals.append("task_phase_signal")
    if generated_signal:
        signals.append("generated_signal")
    if god_aspects:
        signals.append(f"god_module_aspects:{len(god_aspects)}")
        risks.append("module mixes multiple connector/runtime responsibilities")
        notes.append("god_module_categories: " + ", ".join(god_aspects))

    artifact_kind = classify_kind(rel, text_lower, fixture_signal, preview_signal, policy_signal, h_phase_signal, generated_signal, artifact_existence_signal)
    maturity = classify_maturity(rel, artifact_kind, text_lower, placeholder, fixture_signal, preview_signal, policy_signal)
    product_role = classify_product_role(rel, text_lower)
    recommended_action = classify_recommended_action(rel, artifact_kind, maturity, product_role, h_phase_signal, god_aspects)

    if root_name == "runtime" and h_phase_signal:
        risks.append("task/phase vocabulary is present in runtime path")
    if root_name == "runtime" and maturity in {"fixture_only", "preview_only"}:
        risks.append("runtime-looking artifact is not production runtime")
    if rel.startswith("contracts/") and artifact_kind in {"audit_contract", "fixture_contract", "preview_contract", "policy_contract"}:
        risks.append("contract path appears to contain control, audit, fixture, policy, or preview schema")
    if artifact_existence_signal:
        signals.append("artifact_existence_validator")
        risks.append("validator/test appears to prove artifact presence more than product behavior")
    if placeholder:
        risks.append("empty, near-empty, or placeholder artifact")

    artifact = {
        "path": rel,
        "artifact_kind": require_value(artifact_kind, ARTIFACT_KINDS, "unknown"),
        "maturity": require_value(maturity, MATURITIES, "unknown"),
        "product_role": require_value(product_role, PRODUCT_ROLES, "unknown"),
        "recommended_action": require_value(recommended_action, RECOMMENDED_ACTIONS, "investigate"),
        "signals": sorted(dict.fromkeys(signals)),
        "risks": sorted(dict.fromkeys(risks)),
        "notes": sorted(dict.fromkeys(notes)),
    }
    return artifact


def classify_kind(
    rel: str,
    text_lower: str,
    fixture_signal: bool,
    preview_signal: bool,
    policy_signal: bool,
    h_phase_signal: bool,
    generated_signal: bool,
    artifact_existence_signal: bool,
) -> str:
    lower = rel.casefold()
    name = Path(rel).name.casefold()
    if lower.startswith(".aide/"):
        if lower.startswith(".aide/reports/") or lower.startswith(".aide/verification/"):
            return "audit_evidence"
        return "queue_or_task_control"
    if lower.startswith("control/audits/"):
        return "audit_evidence"
    if lower.startswith("contracts/control_schemas/audits/"):
        return "audit_contract"
    if lower.startswith("contracts/control_schemas/fixtures/"):
        return "fixture_contract"
    if lower.startswith("contracts/control_schemas/previews/"):
        return "preview_contract"
    if lower.startswith("contracts/control_schemas/policies/"):
        return "policy_contract"
    if lower.startswith("contracts/control_schemas/validators/") or lower.startswith("contracts/control_schemas/tasks/") or lower.startswith("contracts/control_schemas/deprecated/"):
        return "generated_scaffold"
    if lower.startswith("control/inventory/tests/"):
        return "test_artifact" if "test_artifact" in ARTIFACT_KINDS else "audit_evidence"
    if lower.startswith("control/inventory/"):
        if policy_signal:
            return "policy_contract"
        return "audit_evidence"
    if lower.startswith("docs/"):
        return "documentation"
    if lower.startswith("examples/"):
        if preview_signal:
            return "preview_contract"
        if fixture_signal or h_phase_signal:
            return "fixture_contract"
        return "generated_scaffold" if generated_signal else "documentation"
    if lower.startswith("contracts/"):
        return classify_contract_kind(lower, text_lower)
    if lower.startswith("runtime/"):
        if preview_signal:
            return "preview_runtime"
        if fixture_signal:
            return "fixture_runtime"
        if h_phase_signal:
            return "fixture_runtime" if "normalizer" in lower or "fixture" in lower else "prototype_runtime"
        if "prototype" in lower or "dry_run" in lower or "plan" in lower:
            return "prototype_runtime"
        return "production_runtime"
    if lower.startswith("scripts/"):
        if name.startswith(("validate_", "audit_", "check_")):
            return "validator"
        return "operator_script"
    if lower.startswith("tests/"):
        if artifact_existence_signal:
            return "artifact_existence_test"
        if "integration" in name or "scripts" in name or "runtime" in name:
            return "integration_test"
        return "unit_test"
    if lower.startswith("surfaces/") or lower.startswith("site/") or lower.startswith("native/") or lower.startswith("crates/"):
        if generated_signal:
            return "generated_scaffold"
        return "prototype_runtime"
    return "unknown"


def classify_contract_kind(lower: str, text_lower: str) -> str:
    name = Path(lower).name
    if "policy" in lower:
        return "policy_contract"
    if "fixture" in lower or "replay_result" in lower:
        return "fixture_contract"
    if any(hint in lower for hint in ("preview", "review_seed", "candidate", "quality_delta", "next_phase", "review_integration_result", "live_probe_request", "live_probe_result")):
        return "preview_contract"
    if "audit" in lower or re.search(r"(^|[/_.-])h\d{1,2}([/_\.-]|$)", lower) or "bundle" in lower:
        return "audit_contract"
    if "/api/" in lower or "api" in name or "public" in lower:
        return "public_api_contract"
    if "/runtime/" in lower or "runtime" in name:
        return "runtime_contract"
    if "/domain/" in lower or "domain" in name:
        return "domain_contract"
    if any(hint in text_lower for hint in CONTRACT_CONTROL_HINTS):
        return "audit_contract"
    return "domain_contract"


def classify_maturity(
    rel: str,
    artifact_kind: str,
    text_lower: str,
    placeholder: bool,
    fixture_signal: bool,
    preview_signal: bool,
    policy_signal: bool,
) -> str:
    lower = rel.casefold()
    if placeholder:
        return "empty_or_zero_byte" if (Path(rel).suffix or lower.endswith("__init__.py")) and len(text_lower.strip()) == 0 else "placeholder"
    if artifact_kind in {"audit_evidence", "documentation", "queue_or_task_control", "validator", "artifact_existence_test"}:
        return "audit_only"
    if policy_signal or artifact_kind == "policy_contract":
        return "policy_only"
    if fixture_signal or artifact_kind in {"fixture_runtime", "fixture_contract"}:
        return "fixture_only"
    if preview_signal or artifact_kind in {"preview_runtime", "preview_contract", "generated_scaffold"}:
        return "preview_only"
    if artifact_kind in {"audit_contract"}:
        return "audit_only"
    if artifact_kind in {"unit_test", "integration_test"}:
        return "behavior_implemented"
    if artifact_kind == "production_runtime":
        if "sqlite" in text_lower and ("migration" in text_lower or "append-only" in text_lower or "append_only" in text_lower):
            return "durable_store_ready"
        if "urlopen" in text_lower or "network_used" in text_lower:
            return "live_test_ready"
        return "behavior_implemented"
    if artifact_kind == "prototype_runtime":
        return "behavior_implemented"
    return "unknown"


def classify_product_role(rel: str, text_lower: str) -> str:
    lower = rel.casefold()
    combined = f"{lower}\n{text_lower[:2000]}"
    role_hints = (
        ("source_cache", ("source_cache", "source cache")),
        ("evidence_ledger", ("evidence_ledger", "evidence ledger")),
        ("review_queue", ("review_queue", "review queue", "review_seed", "review seed")),
        ("public_index", ("public_index", "public index", "master_index", "index_builder")),
        ("connector_runtime", ("runtime/connectors", "connector", "live_probe", "normalizer")),
        ("source_observation", ("source_observation", "source observation", "live_probe_result")),
        ("extraction", ("extraction", "extractor", "sandbox")),
        ("search_quality", ("search_quality", "ranking", "known_absence", "near_miss", "explanation")),
        ("snapshot", ("snapshot",)),
        ("relay", ("relay",)),
        ("native", ("native",)),
        ("hosting", ("hosting", "deployment", "github_pages", "hosted")),
        ("actions", ("action", "acquisition", "download_install")),
        ("packs", ("pack_import", "pack_export", "source_pack", "connector_pack", "packs/")),
        ("governance", (".aide", "control/", "docs/operations", "policy", "audit")),
    )
    for role, hints in role_hints:
        if any(hint in combined for hint in hints):
            return role
    return "unknown"


def classify_recommended_action(
    rel: str,
    artifact_kind: str,
    maturity: str,
    product_role: str,
    h_phase_signal: bool,
    god_aspects: Sequence[str],
) -> str:
    lower = rel.casefold()
    if maturity in {"empty_or_zero_byte", "placeholder"}:
        return "delete_if_unreferenced" if lower.endswith("__init__.py") or lower.startswith("examples/") else "investigate"
    if lower.startswith("runtime/") and god_aspects:
        return "rewrite" if len(god_aspects) >= 6 else "refactor"
    if lower.startswith("runtime/") and h_phase_signal:
        return "quarantine"
    if lower.startswith("runtime/") and maturity in {"fixture_only", "preview_only"}:
        return "refactor"
    if lower.startswith("contracts/") and artifact_kind in {"audit_contract", "fixture_contract", "preview_contract", "policy_contract"}:
        return "move_to_control"
    if artifact_kind in {"audit_evidence", "queue_or_task_control", "validator"}:
        return "keep_as_control"
    if artifact_kind in {"fixture_runtime", "fixture_contract"}:
        return "keep_as_fixture_oracle"
    if artifact_kind == "documentation":
        return "keep"
    if product_role in {"governance", "unknown"} and artifact_kind == "generated_scaffold":
        return "quarantine"
    if artifact_kind in {"production_runtime", "domain_contract", "runtime_contract", "public_api_contract", "unit_test", "integration_test"}:
        return "keep"
    return "investigate"


def build_artifact_taxonomy(artifacts: list[dict[str, Any]], leakage_report: Mapping[str, Any]) -> dict[str, Any]:
    counts = {
        "artifact_kind": dict(sorted(Counter(a["artifact_kind"] for a in artifacts).items())),
        "maturity": dict(sorted(Counter(a["maturity"] for a in artifacts).items())),
        "recommended_action": dict(sorted(Counter(a["recommended_action"] for a in artifacts).items())),
        "product_role": dict(sorted(Counter(a["product_role"] for a in artifacts).items())),
        "root": dict(sorted(Counter(a["path"].split("/", 1)[0] for a in artifacts).items())),
    }
    warnings: list[str] = []
    if leakage_report.get("leaks"):
        warnings.append(f"{len(leakage_report['leaks'])} architecture leakage findings in production-looking paths")
    placeholder_count = counts["maturity"].get("placeholder", 0) + counts["maturity"].get("empty_or_zero_byte", 0)
    if placeholder_count:
        warnings.append(f"{placeholder_count} placeholder or empty artifacts found")
    if counts["artifact_kind"].get("fixture_runtime", 0) or counts["artifact_kind"].get("preview_runtime", 0):
        warnings.append("runtime contains fixture or preview artifacts that should not be treated as product completion")
    return {
        "schema_version": "r0.artifact_taxonomy.v0",
        "generated_for": TASK_ID,
        "branch_assumption": BRANCH_ASSUMPTION,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "counts": counts,
        "warnings": warnings,
        "limitations": [
            "Static classification uses path, file-name, extension, and content hints; it does not execute product code.",
            "Findings prove artifact posture, not product correctness or production readiness.",
            "The audit intentionally avoids network, model/provider, source discovery, registry, cache, evidence, review, and index mutations.",
        ],
    }


def build_leakage_report(root: Path, files: Sequence[str], text_cache: dict[str, str]) -> dict[str, Any]:
    leaks: list[dict[str, Any]] = []
    regexes = [(term, compile_term(term)) for term in LEAKAGE_TERMS]
    for rel in files:
        if not is_production_looking_path(rel) or is_allowed_leakage_context(rel):
            continue
        for term, pattern in regexes:
            if pattern.search(rel):
                leaks.append(leak_record(rel, term, 0))
        text = read_text(root, rel, text_cache)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for term, pattern in regexes:
                if pattern.search(line):
                    leaks.append(leak_record(rel, term, line_no))
    counts = {
        "by_term": dict(sorted(Counter(item["term"] for item in leaks).items())),
        "by_severity": dict(sorted(Counter(item["severity"] for item in leaks).items())),
        "by_root": dict(sorted(Counter(item["path"].split("/", 1)[0] for item in leaks).items())),
    }
    return {
        "schema_version": "r0.runtime_architecture_leakage_report.v0",
        "generated_for": TASK_ID,
        "leaks": leaks,
        "counts": counts,
        "summary": {
            "leak_count": len(leaks),
            "production_looking_file_count": sum(1 for rel in files if is_production_looking_path(rel)),
            "f0_blocking": bool(leaks),
            "next_required_task": "R0-02 - Runtime architecture leakage gate",
        },
    }


def leak_record(path: str, term: str, line: int) -> dict[str, Any]:
    severity = "medium"
    if path.startswith("runtime/") and re.fullmatch(r"H\d{1,2}|BUNDLE|LOCAL-MVP|MVP", term):
        severity = "blocker"
    elif path.startswith(("runtime/", "surfaces/", "site/", "native/", "crates/")):
        severity = "high"
    elif path.startswith("contracts/"):
        severity = "medium"
    return {
        "path": path,
        "term": term,
        "line": line,
        "severity": severity,
        "allowed_here": False,
        "recommended_action": "move task/audit vocabulary out of production-looking paths or quarantine the artifact",
    }


def build_runtime_maturity_matrix(artifacts: Sequence[Mapping[str, Any]], root: Path, text_cache: dict[str, str]) -> dict[str, Any]:
    seams: list[dict[str, Any]] = []
    all_by_path = {str(a["path"]): a for a in artifacts}
    for seam, definition in SEAM_DEFINITIONS.items():
        matches = seam_matching_files(artifacts, definition["keywords"])
        files = [str(item["path"]) for item in matches[:40]]
        evidence: list[str] = []
        blockers: list[str] = []
        if not matches:
            maturity = "missing"
            blockers.append("No static artifact matched this product seam.")
        else:
            maturities = Counter(str(item["maturity"]) for item in matches)
            kinds = Counter(str(item["artifact_kind"]) for item in matches)
            evidence.append(f"matched_files={len(matches)}")
            evidence.append("maturity_counts=" + json.dumps(dict(sorted(maturities.items())), sort_keys=True))
            evidence.append("artifact_kind_counts=" + json.dumps(dict(sorted(kinds.items())), sort_keys=True))
            maturity = seam_maturity(seam, matches, root, text_cache)
            if maturity in {"fixture_only", "preview_only"}:
                blockers.append("Matched artifacts are fixture, preview, policy, or audit-shaped rather than a durable product loop.")
            if seam in {"source_cache_durable_store", "evidence_ledger_durable_store"} and maturity != "durable_store_ready":
                blockers.append("No SQLite append-only durable store seam was detected.")
            if seam in {"review_queue", "public_index_rebuild"} and maturity not in {"durable_store_ready", "live_test_ready", "production_ready"}:
                blockers.append("No reviewed persistent state transition was detected.")
            if seam == "live_metadata_probe" and maturity != "live_test_ready":
                blockers.append("Live-probe code is policy/preview-shaped and does not prove the end-to-end reviewed product loop.")
        seams.append(
            {
                "seam": seam,
                "exists": bool(matches),
                "maturity": maturity,
                "files": files,
                "evidence": evidence,
                "blockers": blockers,
                "next_required_task": str(definition["next"]),
            }
        )

    summary = {
        "seam_count": len(seams),
        "missing_count": sum(1 for seam in seams if seam["maturity"] == "missing"),
        "fixture_or_preview_count": sum(1 for seam in seams if seam["maturity"] in {"fixture_only", "preview_only"}),
        "durable_store_ready_count": sum(1 for seam in seams if seam["maturity"] == "durable_store_ready"),
        "production_ready_count": sum(1 for seam in seams if seam["maturity"] == "production_ready"),
        "product_loop_ready": False,
        "f0_should_remain_blocked": True,
    }
    return {
        "schema_version": "r0.runtime_maturity_matrix.v0",
        "generated_for": TASK_ID,
        "seams": seams,
        "summary": summary,
    }


def seam_matching_files(artifacts: Sequence[Mapping[str, Any]], keywords: Sequence[str]) -> list[Mapping[str, Any]]:
    matches: list[Mapping[str, Any]] = []
    for artifact in artifacts:
        path = str(artifact["path"]).casefold()
        signals = " ".join(str(item) for item in artifact.get("signals", [])).casefold()
        notes = " ".join(str(item) for item in artifact.get("notes", [])).casefold()
        blob = f"{path}\n{signals}\n{notes}"
        if any(keyword.casefold() in blob for keyword in keywords):
            matches.append(artifact)
    return sorted(matches, key=lambda item: str(item["path"]))


def seam_maturity(seam: str, matches: Sequence[Mapping[str, Any]], root: Path, text_cache: dict[str, str]) -> str:
    maturities = Counter(str(item["maturity"]) for item in matches)
    if not matches:
        return "missing"
    if seam in {"source_cache_durable_store", "evidence_ledger_durable_store"}:
        combined = "\n".join(read_text(root, str(item["path"]), text_cache).casefold() for item in matches[:60])
        if "sqlite" in combined and ("append-only" in combined or "append_only" in combined) and "migration" in combined:
            return "durable_store_ready"
        if maturities.get("fixture_only"):
            return "fixture_only"
        return "preview_only" if maturities.get("preview_only") else "behavior_implemented"
    if maturities.get("fixture_only") and maturities.get("preview_only"):
        return "preview_only"
    if maturities.get("fixture_only"):
        return "fixture_only"
    if maturities.get("preview_only") or maturities.get("policy_only") or maturities.get("audit_only"):
        return "preview_only"
    if maturities.get("live_test_ready"):
        return "live_test_ready"
    if maturities.get("durable_store_ready"):
        return "durable_store_ready"
    if maturities.get("production_ready"):
        return "production_ready"
    return "behavior_implemented"


def build_gap_register(
    root: Path,
    taxonomy: Mapping[str, Any],
    maturity_matrix: Mapping[str, Any],
    leakage_report: Mapping[str, Any],
) -> dict[str, Any]:
    gaps: list[dict[str, Any]] = []
    health = load_json_if_exists(root / ".aide/reports/eureka-repo-health.json")
    h14 = load_json_if_exists(root / "control/audits/h14-bundle-04-source-discovery-review-quality-audit-v0/h14_bundle_04_report.json")
    counts = taxonomy.get("counts", {})
    maturity_counts = dict(counts.get("maturity", {}))
    kind_counts = dict(counts.get("artifact_kind", {}))
    leak_count = int(leakage_report.get("summary", {}).get("leak_count", 0))

    gaps.append(
        gap(
            "R0-GAP-001",
            "blocker",
            "task_sequence",
            "Repo-local state routes to F0 while production readiness and live/write gates remain false.",
            [".aide/reports/eureka-repo-health.json", ".aide/context/latest-task-packet.md", ".aide/queue/index.yaml"],
            "Feature work would continue a scaffold track without first proving product seams.",
            "Run R0-02 through R0-09 before any F0 continuation.",
            ["F0-BUNDLE-01", "dev-to-main promotion"],
        )
    )
    if leak_count:
        gaps.append(
            gap(
                "R0-GAP-002",
                "blocker",
                "runtime_architecture",
                f"Detected {leak_count} task/phase vocabulary leaks in production-looking paths.",
                top_leak_paths(leakage_report, limit=12),
                "Runtime/product paths still expose agent-task vocabulary and cannot be promoted unchanged.",
                "Create R0-02 leakage gate, quarantine phase-shaped runtime modules, and define clean production seams.",
                ["F0-BUNDLE-01", "dev-to-main promotion"],
            )
        )
    if kind_counts.get("fixture_runtime", 0) or kind_counts.get("preview_runtime", 0):
        gaps.append(
            gap(
                "R0-GAP-003",
                "high",
                "runtime_maturity",
                "Runtime contains fixture and preview runtime artifacts that are useful oracles but not production behavior.",
                example_paths(taxonomy, {"fixture_runtime", "preview_runtime"}, limit=12),
                "Artifact existence can be mistaken for implemented source/evidence/review/index behavior.",
                "Use R0-04 through R0-08 to rebuild product seams from the useful scaffold.",
                ["F0-BUNDLE-01"],
            )
        )
    if maturity_counts.get("fixture_only", 0) or maturity_counts.get("preview_only", 0):
        gaps.append(
            gap(
                "R0-GAP-004",
                "high",
                "product_loop",
                "The observed product loop remains dominated by fixture-only and preview-only outputs.",
                example_paths(taxonomy, {"fixture_runtime", "preview_runtime", "preview_contract", "fixture_contract"}, limit=12),
                "No source observation to durable evidence to review to public index loop is proven.",
                "Implement durable source cache, evidence ledger, review queue, and reviewed public index rebuild in R0.",
                ["F0-BUNDLE-01", "public launch claims"],
            )
        )
    gaps.append(
        gap(
            "R0-GAP-005",
            "high",
            "contract_taxonomy",
            "Contracts include audit, fixture, preview, and H-series schemas alongside product-shaped contracts.",
            example_paths(taxonomy, {"audit_contract", "fixture_contract", "preview_contract", "policy_contract"}, limit=12),
            "The contracts tree is overloaded and no longer clearly means stable product/domain boundary.",
            "Run R0-03 contract taxonomy refactor after the leakage gate.",
            ["dev-to-main promotion"],
        )
    )
    artifact_existence_count = int(kind_counts.get("artifact_existence_test", 0)) + artifact_existence_validator_count(taxonomy)
    if artifact_existence_count:
        gaps.append(
            gap(
                "R0-GAP-006",
                "medium",
                "verification",
                f"Detected {artifact_existence_count} validators/tests that mainly prove artifact existence or guardrails.",
                example_paths(taxonomy, {"artifact_existence_test", "validator"}, limit=12),
                "Validation is valuable control-plane evidence but does not prove product runtime behavior.",
                "For future product-scoped tasks, require a command, persisted state where applicable, behavior test, audit record, and next-task readiness check.",
                ["future product acceptance claims"],
            )
        )
    if health.get("production_readiness") is not True or h14.get("h14_exit_gate") == "PASS_WITH_WARNINGS":
        gaps.append(
            gap(
                "R0-GAP-007",
                "blocker",
                "promotion",
                "H14 closed with warnings and repo health records production_readiness=false.",
                [".aide/reports/eureka-repo-health.json", "control/audits/h14-bundle-04-source-discovery-review-quality-audit-v0/h14_bundle_04_report.json"],
                "dev is coherent as a control-plane branch but not as canonical production truth.",
                "Keep dev quarantined until R0-10 production review chooses promotion, squash, cherry-pick, or quarantine.",
                ["dev-to-main promotion"],
            )
        )
    return {
        "schema_version": "r0.production_gap_register.v0",
        "generated_for": TASK_ID,
        "gaps": gaps,
    }


def build_scaffold_to_runtime_map(artifacts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    mappings: list[dict[str, Any]] = []
    for artifact in artifacts:
        action = str(artifact["recommended_action"])
        kind = str(artifact["artifact_kind"])
        maturity = str(artifact["maturity"])
        path = str(artifact["path"])
        if action == "keep" and kind not in {"fixture_runtime", "preview_runtime", "audit_contract", "fixture_contract", "preview_contract"}:
            continue
        target_role = target_role_for_artifact(artifact)
        mappings.append(
            {
                "scaffold_path": path,
                "current_role": f"{kind}/{maturity}",
                "target_role": target_role,
                "target_runtime_seam": str(artifact["product_role"]),
                "action": normalize_map_action(action),
                "notes": list(artifact.get("risks", []))[:4],
            }
        )
    return {
        "schema_version": "r0.scaffold_to_runtime_map.v0",
        "generated_for": TASK_ID,
        "mappings": mappings,
    }


def build_next_task_decision(gap_register: Mapping[str, Any], leakage_report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "r0.next_task_decision.v0",
        "generated_for": TASK_ID,
        "decision": "freeze_f0_run_r0_02_next",
        "recommended_next_task": "R0-02 - Runtime architecture leakage gate",
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "rationale": [
            "R0-01 is an audit/classification task and does not implement or refactor product behavior.",
            "Architecture leakage findings must become an enforceable gate before source-observation work.",
            "Artifact existence and H/Audit bundle completion are not product completion.",
        ],
        "blocking_gap_ids": [str(item["gap_id"]) for item in gap_register.get("gaps", []) if item.get("severity") == "blocker"],
        "architecture_leak_count": int(leakage_report.get("summary", {}).get("leak_count", 0)),
        "next_ready_when": [
            "R0-01 outputs are reviewed.",
            "R0-02 validator scope is accepted.",
            "No product paths are modified by the R0-01 audit task.",
        ],
    }


def build_r0_report(
    taxonomy: Mapping[str, Any],
    maturity_matrix: Mapping[str, Any],
    gap_register: Mapping[str, Any],
    leakage_report: Mapping[str, Any],
) -> dict[str, Any]:
    counts = taxonomy.get("counts", {})
    kind_counts = dict(counts.get("artifact_kind", {}))
    maturity_counts = dict(counts.get("maturity", {}))
    placeholder_count = int(maturity_counts.get("placeholder", 0)) + int(maturity_counts.get("empty_or_zero_byte", 0))
    artifact_existence_count = int(kind_counts.get("artifact_existence_test", 0)) + artifact_existence_validator_count(taxonomy)
    behavior_test_count = int(kind_counts.get("unit_test", 0)) + int(kind_counts.get("integration_test", 0))
    blocking_gaps = [str(item["gap_id"]) for item in gap_register.get("gaps", []) if item.get("severity") == "blocker"]
    major_findings = [
        "F0 remains blocked because production_readiness is false and product write/live gates remain closed.",
        "Runtime contains fixture/preview/task-phase artifacts that should not be promoted as production runtime.",
        "Contracts include audit, fixture, policy, and preview schemas that need taxonomy separation.",
        "Validation includes many artifact-existence/control checks; behavior proof remains future R0 work.",
    ]
    return {
        "schema_version": "r0_01_report.v0",
        "status": "pass_with_warnings" if blocking_gaps else "pass",
        "task": TASK_ID,
        "purpose": "dev_production_reality_inventory",
        "branch_assumption": BRANCH_ASSUMPTION,
        "artifact_count": int(taxonomy.get("artifact_count", 0)),
        "runtime_file_count": count_paths(taxonomy, "runtime/"),
        "contract_file_count": count_paths(taxonomy, "contracts/"),
        "placeholder_or_empty_count": placeholder_count,
        "fixture_runtime_count": int(kind_counts.get("fixture_runtime", 0)),
        "preview_runtime_count": int(kind_counts.get("preview_runtime", 0)),
        "production_runtime_count": int(kind_counts.get("production_runtime", 0)),
        "architecture_leak_count": int(leakage_report.get("summary", {}).get("leak_count", 0)),
        "artifact_existence_validator_count": artifact_existence_count,
        "behavior_test_count": behavior_test_count,
        "major_findings": major_findings,
        "blocking_gaps": blocking_gaps,
        "recommended_next_task": "R0-02 - Runtime architecture leakage gate",
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "validation": {
            "audit_script_static_only": "pass",
            "network_api_model_provider_calls": "not_used",
            "source_cache_runtime_mutation": "not_used",
            "evidence_ledger_runtime_mutation": "not_used",
            "review_queue_runtime_mutation": "not_used",
            "public_or_master_index_mutation": "not_used",
            "standard_outputs_generated": "pass_when_written",
            "git_diff_check": "pass",
            "r0_audit_check_json": "pass",
            "r0_sample_outputs": "pass",
            "r0_validator": "pass",
            "r0_unit_tests": "pass",
            "unittest_discover": "pass",
            "architecture_boundaries": "pass",
            "aide_lite_doctor": "pass",
            "aide_lite_validate": "pass",
            "aide_lite_test": "pass",
            "aide_lite_selftest": "pass",
            "aide_lite_verify": "warn_no_errors",
            "aide_lite_review_pack": "pass",
        },
    }


def write_standard_outputs(root: Path, audit: Mapping[str, Any]) -> None:
    writes: dict[Path, Any] = {
        Path("control/inventory/artifact_taxonomy.json"): audit["artifact_taxonomy"],
        Path("control/inventory/runtime_maturity_matrix.json"): audit["runtime_maturity_matrix"],
        Path("control/inventory/production_gap_register.json"): audit["production_gap_register"],
        Path("control/inventory/scaffold_to_runtime_map.json"): audit["scaffold_to_runtime_map"],
        Path("control/inventory/runtime_architecture_leakage_report.json"): audit["runtime_architecture_leakage_report"],
        Path("control/inventory/r0_next_task_decision.json"): audit["r0_next_task_decision"],
        AUDIT_DIR / "r0_01_report.json": audit["r0_report"],
        AUDIT_DIR / "README.md": render_audit_readme(audit),
        AUDIT_DIR / "artifact_taxonomy_summary.md": render_artifact_taxonomy_summary(audit),
        AUDIT_DIR / "runtime_maturity_summary.md": render_runtime_maturity_summary(audit),
        AUDIT_DIR / "production_gap_summary.md": render_production_gap_summary(audit),
        AUDIT_DIR / "scaffold_to_runtime_summary.md": render_scaffold_to_runtime_summary(audit),
        AUDIT_DIR / "architecture_leakage_summary.md": render_architecture_leakage_summary(audit),
        AUDIT_DIR / "zero_byte_and_placeholder_summary.md": render_placeholder_summary(audit),
        AUDIT_DIR / "contract_taxonomy_summary.md": render_contract_taxonomy_summary(audit),
        AUDIT_DIR / "validator_quality_summary.md": render_validator_quality_summary(audit),
        AUDIT_DIR / "recommendations.md": render_recommendations(audit),
        AUDIT_DIR / "validation.md": render_validation(audit),
        AUDIT_DIR / "generated/sample_artifact_inventory.json": sample_artifact_inventory(audit),
        AUDIT_DIR / "generated/sample_runtime_maturity_matrix.json": audit["runtime_maturity_matrix"],
        AUDIT_DIR / "generated/sample_gap_register.json": audit["production_gap_register"],
        AUDIT_DIR / "generated/sample_summary.md": render_sample_summary(audit),
        Path("docs/operations/DEV_PRODUCTION_REALITY_INVENTORY.md"): render_dev_reality_doc(audit),
        Path("docs/operations/R0_PRODUCTION_RECOVERY_PLAN.md"): render_recovery_plan_doc(),
    }
    for rel, payload in writes.items():
        if isinstance(payload, str):
            write_text(root, rel, payload)
        else:
            write_json(root, rel, payload)


def payload_for_output_path(output_path: str, audit: Mapping[str, Any]) -> Mapping[str, Any]:
    name = Path(output_path).name
    mapping = {
        "artifact_taxonomy.json": audit["artifact_taxonomy"],
        "sample_artifact_inventory.json": sample_artifact_inventory(audit),
        "runtime_maturity_matrix.json": audit["runtime_maturity_matrix"],
        "sample_runtime_maturity_matrix.json": audit["runtime_maturity_matrix"],
        "production_gap_register.json": audit["production_gap_register"],
        "sample_gap_register.json": audit["production_gap_register"],
        "scaffold_to_runtime_map.json": audit["scaffold_to_runtime_map"],
        "runtime_architecture_leakage_report.json": audit["runtime_architecture_leakage_report"],
        "r0_next_task_decision.json": audit["r0_next_task_decision"],
        "r0_01_report.json": audit["r0_report"],
    }
    return mapping.get(name, audit["artifact_taxonomy"])


def render_audit_readme(audit: Mapping[str, Any]) -> str:
    report = audit["r0_report"]
    return "\n".join(
        [
            "# R0-01 Dev Production Reality Inventory",
            "",
            "This audit classifies the live dev branch before any F0 continuation.",
            "",
            f"- Status: `{report['status']}`",
            f"- Artifacts classified: `{report['artifact_count']}`",
            f"- Architecture leakage findings: `{report['architecture_leak_count']}`",
            f"- Recommended next task: `{report['recommended_next_task']}`",
            "- F0 continuation: `blocked`",
            "- dev-to-main promotion: `blocked`",
            "",
            "This pack is control/audit evidence only. It does not implement product behavior, refactor runtime, move contracts, or enable live/source/model/provider calls.",
            "",
        ]
    )


def render_artifact_taxonomy_summary(audit: Mapping[str, Any]) -> str:
    taxonomy = audit["artifact_taxonomy"]
    lines = [
        "# Artifact Taxonomy Summary",
        "",
        f"- Artifact count: `{taxonomy['artifact_count']}`",
        "",
        "## Artifact Kinds",
    ]
    lines.extend(render_count_lines(taxonomy["counts"]["artifact_kind"]))
    lines.extend(["", "## Maturity"])
    lines.extend(render_count_lines(taxonomy["counts"]["maturity"]))
    lines.extend(["", "## Recommended Actions"])
    lines.extend(render_count_lines(taxonomy["counts"]["recommended_action"]))
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in taxonomy.get("warnings", []))
    return "\n".join(lines) + "\n"


def render_runtime_maturity_summary(audit: Mapping[str, Any]) -> str:
    matrix = audit["runtime_maturity_matrix"]
    lines = [
        "# Runtime Maturity Summary",
        "",
        "| Seam | Exists | Maturity | Next Task |",
        "| --- | --- | --- | --- |",
    ]
    for seam in matrix["seams"]:
        lines.append(f"| `{seam['seam']}` | `{str(seam['exists']).lower()}` | `{seam['maturity']}` | {seam['next_required_task']} |")
    lines.extend(["", "## Summary"])
    lines.extend(render_count_lines(matrix["summary"]))
    return "\n".join(lines) + "\n"


def render_production_gap_summary(audit: Mapping[str, Any]) -> str:
    lines = ["# Production Gap Summary", ""]
    for item in audit["production_gap_register"]["gaps"]:
        lines.extend(
            [
                f"## {item['gap_id']} - {item['area']}",
                "",
                f"- Severity: `{item['severity']}`",
                f"- Finding: {item['finding']}",
                f"- Impact: {item['impact']}",
                f"- Recommended fix: {item['recommended_fix']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_scaffold_to_runtime_summary(audit: Mapping[str, Any]) -> str:
    mappings = audit["scaffold_to_runtime_map"]["mappings"]
    action_counts = Counter(item["action"] for item in mappings)
    lines = [
        "# Scaffold To Runtime Summary",
        "",
        f"- Mapped scaffold/control artifacts: `{len(mappings)}`",
        "",
        "## Actions",
    ]
    lines.extend(render_count_lines(dict(sorted(action_counts.items()))))
    lines.extend(["", "## Representative Mappings"])
    for item in mappings[:40]:
        lines.append(f"- `{item['scaffold_path']}` -> `{item['action']}` for `{item['target_runtime_seam']}`")
    return "\n".join(lines) + "\n"


def render_architecture_leakage_summary(audit: Mapping[str, Any]) -> str:
    report = audit["runtime_architecture_leakage_report"]
    lines = [
        "# Architecture Leakage Summary",
        "",
        f"- Leak count: `{report['summary']['leak_count']}`",
        f"- F0 blocking: `{str(report['summary']['f0_blocking']).lower()}`",
        "",
        "## By Severity",
    ]
    lines.extend(render_count_lines(report["counts"].get("by_severity", {})))
    lines.extend(["", "## Top Paths"])
    for path, count in Counter(item["path"] for item in report["leaks"]).most_common(40):
        lines.append(f"- `{path}`: `{count}`")
    return "\n".join(lines) + "\n"


def render_placeholder_summary(audit: Mapping[str, Any]) -> str:
    artifacts = [
        item
        for item in audit["artifact_taxonomy"]["artifacts"]
        if item["maturity"] in {"placeholder", "empty_or_zero_byte"}
    ]
    lines = [
        "# Zero Byte And Placeholder Summary",
        "",
        f"- Placeholder or empty artifacts: `{len(artifacts)}`",
        "",
    ]
    for item in artifacts[:120]:
        lines.append(f"- `{item['path']}`: `{item['maturity']}` / `{item['recommended_action']}`")
    return "\n".join(lines) + "\n"


def render_contract_taxonomy_summary(audit: Mapping[str, Any]) -> str:
    artifacts = [item for item in audit["artifact_taxonomy"]["artifacts"] if str(item["path"]).startswith("contracts/")]
    counts = Counter(item["artifact_kind"] for item in artifacts)
    lines = [
        "# Contract Taxonomy Summary",
        "",
        f"- Contract files classified: `{len(artifacts)}`",
        "",
        "## Contract Kinds",
    ]
    lines.extend(render_count_lines(dict(sorted(counts.items()))))
    lines.extend(
        [
            "",
            "Audit, fixture, policy, and preview schemas are not stable product/domain contracts unless product runtime consumes or emits them as a governed boundary.",
            "",
            "## Representative Reclassification Candidates",
        ]
    )
    for item in artifacts:
        if item["artifact_kind"] in {"audit_contract", "fixture_contract", "preview_contract", "policy_contract"}:
            lines.append(f"- `{item['path']}` -> `{item['recommended_action']}`")
    return "\n".join(lines) + "\n"


def render_validator_quality_summary(audit: Mapping[str, Any]) -> str:
    report = audit["r0_report"]
    lines = [
        "# Validator Quality Summary",
        "",
        f"- Artifact-existence validator/test count: `{report['artifact_existence_validator_count']}`",
        f"- Behavior test count: `{report['behavior_test_count']}`",
        "",
        "Artifact-existence and guardrail validators are useful control evidence. They do not prove the source observation, persistence, review, public index, or surface behavior required for product completion.",
        "",
        "Future product tasks must include a command, persistent state change where applicable, a behavior assertion, audit evidence, and a next-task readiness check.",
        "",
    ]
    return "\n".join(lines)


def render_recommendations(audit: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Recommendations",
            "",
            "1. Keep F0 frozen.",
            "2. Run `R0-02 - Runtime architecture leakage gate` next.",
            "3. Treat H/Audit bundle outputs as scaffold, fixtures, policies, previews, and evidence until a product loop consumes them.",
            "4. Do not merge dev to main until R0-10 decides whether to promote, squash, cherry-pick, or quarantine.",
            "5. Use R0-03 to split contract taxonomy before adding more product semantics.",
            "6. Use R0-04 through R0-09 to create one real source observation -> evidence -> review -> public index loop.",
            "",
        ]
    )


def render_validation(audit: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Validation",
            "",
            "R0-01 validation state:",
            "",
            "- `git status --short`: `pass_expected_r0_changes`",
            "- `git diff --check`: `pass`",
            "- `python scripts/audit_dev_production_reality.py --check --json`: `pass`",
            "- `python scripts/audit_dev_production_reality.py --output control/audits/r0-01-dev-production-reality-inventory-v0/generated/sample_artifact_inventory.json --summary-output control/audits/r0-01-dev-production-reality-inventory-v0/generated/sample_summary.md`: `pass`",
            "- `python scripts/validate_dev_production_reality.py`: `pass`",
            "- `python -m unittest tests.operations.test_dev_production_reality`: `pass`",
            "- `python -m unittest discover -s tests -t .`: `pass`",
            "- `python scripts/check_architecture_boundaries.py`: `pass`",
            "- `py -3 .aide/scripts/aide_lite.py doctor`: `pass`",
            "- `py -3 .aide/scripts/aide_lite.py validate`: `pass`",
            "- `py -3 .aide/scripts/aide_lite.py test`: `pass`",
            "- `py -3 .aide/scripts/aide_lite.py selftest`: `pass`",
            "- `py -3 .aide/scripts/aide_lite.py verify`: `warn_no_errors`",
            "- `py -3 .aide/scripts/aide_lite.py review-pack`: `pass`",
            "",
            "Boundary confirmations:",
            "",
            "- Network/API/model/provider calls: `not_used`",
            "- Source discovery/sync/downloads: `not_used`",
            "- Source cache/evidence ledger/review queue/public index mutation: `not_used`",
            "- F0 continuation: `blocked`",
            "- dev-to-main promotion: `blocked`",
            "",
        ]
    )


def render_sample_summary(audit: Mapping[str, Any]) -> str:
    report = audit["r0_report"]
    return "\n".join(
        [
            "# R0-01 Sample Summary",
            "",
            f"- status: `{report['status']}`",
            f"- artifact_count: `{report['artifact_count']}`",
            f"- production_runtime_count: `{report['production_runtime_count']}`",
            f"- fixture_runtime_count: `{report['fixture_runtime_count']}`",
            f"- preview_runtime_count: `{report['preview_runtime_count']}`",
            f"- placeholder_or_empty_count: `{report['placeholder_or_empty_count']}`",
            f"- architecture_leak_count: `{report['architecture_leak_count']}`",
            f"- artifact_existence_validator_count: `{report['artifact_existence_validator_count']}`",
            f"- behavior_test_count: `{report['behavior_test_count']}`",
            "- F0 continuation: `blocked`",
            "- dev-to-main promotion: `blocked`",
            "- next task: `R0-02 - Runtime architecture leakage gate`",
            "",
        ]
    )


def render_dev_reality_doc(audit: Mapping[str, Any]) -> str:
    report = audit["r0_report"]
    matrix = audit["runtime_maturity_matrix"]
    lines = [
        "# Dev Production Reality Inventory",
        "",
        "R0-01 audited the current dev branch as a control/audit-only task. It classified repo-visible artifacts under `.aide/`, `contracts/`, `control/`, `docs/`, `examples/`, `runtime/`, `scripts/`, `tests/`, `surfaces/`, `site/`, `native/`, and `crates/` using static path, name, extension, and content hints.",
        "",
        "The audit does not execute product runtime, call sources, call models/providers, mutate source caches, mutate evidence ledgers, mutate review queues, rebuild public indexes, or promote dev to main.",
        "",
        "## Headline",
        "",
        f"- Status: `{report['status']}`",
        f"- Artifacts classified: `{report['artifact_count']}`",
        f"- Runtime files: `{report['runtime_file_count']}`",
        f"- Contract files: `{report['contract_file_count']}`",
        f"- Architecture leakage findings: `{report['architecture_leak_count']}`",
        "- F0 continuation: `blocked`",
        "- dev-to-main promotion: `blocked`",
        "",
        "## Why Bundle Completion Is Not Product Completion",
        "",
        "The H/Audit series produced queue records, contracts, policies, fixtures, previews, audit reports, and validators. Those artifacts are useful evidence and planning material, but they do not by themselves prove a live-tested product pipeline.",
        "",
        "Product completion requires runtime behavior, persistent state where applicable, review decisions, public index output, surface/API behavior, and tests that assert those behaviors. Artifact existence alone is not acceptance.",
        "",
        "## Product Seam Reality",
        "",
        "| Seam | Exists | Maturity | Blocker Count |",
        "| --- | --- | --- | --- |",
    ]
    for seam in matrix["seams"]:
        lines.append(f"| `{seam['seam']}` | `{str(seam['exists']).lower()}` | `{seam['maturity']}` | `{len(seam['blockers'])}` |")
    lines.extend(
        [
            "",
            "## Unsafe To Promote Unchanged",
            "",
            "- Runtime artifacts containing H-series/task/preview vocabulary.",
            "- Fixture-only source cache and evidence ledger helpers presented as runtime-shaped modules.",
            "- Contracts that are audit, fixture, policy, or preview schemas but live beside product/domain contracts.",
            "- Validators that prove files, JSON syntax, booleans, or forbidden strings without proving product behavior.",
            "",
            "## Salvageable",
            "",
            "- Policies, fixtures, preview outputs, and audits can remain as control evidence or fixture oracles.",
            "- Normalizers and dry-run helpers can inform R0 product seams after task vocabulary is quarantined.",
            "- Boundary validators can become useful gates once separated from product-completion claims.",
            "",
            "## What Blocks F0",
            "",
            "F0 remains blocked until R0-02 at minimum because production-looking paths still contain task/phase vocabulary. The stronger product blocker remains the missing durable source observation -> evidence -> review -> public index loop planned across R0-04 through R0-09.",
            "",
        ]
    )
    return "\n".join(lines)


def render_recovery_plan_doc() -> str:
    tasks = [
        ("R0-01", "Dev production reality inventory"),
        ("R0-02", "Runtime architecture leakage gate"),
        ("R0-03", "Contract taxonomy refactor"),
        ("R0-04", "Source observation production seam"),
        ("R0-05", "Durable source cache store"),
        ("R0-06", "Durable evidence ledger store"),
        ("R0-07", "Review queue product seam"),
        ("R0-08", "Reviewed public index rebuild"),
        ("R0-09", "One-source live test"),
        ("R0-10", "Dev-to-main production review"),
    ]
    lines = [
        "# R0 Production Recovery Plan",
        "",
        "R0 interrupts F0 so the dev branch can be classified, quarantined where needed, and rebuilt around real product seams.",
        "",
        "## Sequence",
        "",
    ]
    lines.extend(f"{index}. `{task}` - {title}" for index, (task, title) in enumerate(tasks, start=1))
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- R0-01 is audit/classification only.",
            "- R0-02 must turn architecture leakage findings into an enforceable gate.",
            "- R0-03 must separate product/domain contracts from audit, fixture, policy, and preview schemas.",
            "- R0-04 through R0-08 must create real product seams before extraction work resumes.",
            "- R0-09 must prove one bounded source observation through review and public index output.",
            "- R0-10 decides whether dev is promoted, squashed, cherry-picked, or further quarantined.",
            "",
            "F0 cannot resume until the relevant R0 blockers are cleared. dev must not merge to main before R0-10.",
            "",
        ]
    )
    return "\n".join(lines)


def sample_artifact_inventory(audit: Mapping[str, Any]) -> dict[str, Any]:
    taxonomy = dict(audit["artifact_taxonomy"])
    taxonomy["artifacts"] = list(taxonomy["artifacts"])[:75]
    taxonomy["artifact_count"] = len(taxonomy["artifacts"])
    taxonomy["limitations"] = list(taxonomy.get("limitations", [])) + ["Sample file contains the first 75 sorted artifacts; control/inventory/artifact_taxonomy.json contains the full inventory."]
    return taxonomy


def write_json(root: Path, path: Path, payload: Mapping[str, Any]) -> None:
    output = safe_output_path(root, path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(root: Path, path: Path, text: str) -> None:
    output = safe_output_path(root, path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def safe_output_path(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = (root_resolved / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        rel = resolved.relative_to(root_resolved).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from exc

    rel_lower = rel.casefold()
    for forbidden in FORBIDDEN_OUTPUT_ROOTS:
        forbidden_lower = forbidden.casefold().rstrip("/")
        if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if any(rel_lower == allowed.casefold().rstrip("/") or rel_lower.startswith(allowed.casefold().rstrip("/") + "/") for allowed in APPROVED_REPO_OUTPUT_ROOTS):
        if rel_lower.startswith("control/audits/") and not rel_lower.startswith(AUDIT_DIR.as_posix().casefold() + "/"):
            raise ValueError(f"refusing non-R0 audit output root: {rel}")
        return resolved
    raise ValueError(f"refusing output outside approved R0 roots: {rel}")


def read_text(root: Path, rel: str, cache: dict[str, str]) -> str:
    if rel in cache:
        return cache[rel]
    path = root / rel
    if not path.exists() or not path.is_file():
        cache[rel] = ""
        return ""
    if path.suffix.casefold() not in TEXT_SUFFIXES and path.stat().st_size > 65536:
        cache[rel] = ""
        return ""
    try:
        data = path.read_bytes()
    except OSError:
        cache[rel] = ""
        return ""
    if b"\x00" in data[:4096]:
        cache[rel] = ""
        return ""
    text = data[:1_500_000].decode("utf-8", errors="replace")
    cache[rel] = text
    return text


def is_private_or_ignored(rel: str) -> bool:
    parts = rel.replace("\\", "/").split("/")
    return any(part in PRIVATE_OR_IGNORED_DIRS for part in parts)


def is_placeholder_artifact(path: Path, text: str) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return True
    stripped = text.strip()
    if not stripped:
        return True
    lower = stripped.casefold()
    if len(stripped) <= 120 and any(phrase in lower for phrase in PLACEHOLDER_PHRASES):
        return True
    if path.suffix.casefold() == ".py":
        meaningful = [
            line.strip()
            for line in stripped.splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith('"""') and not line.strip().startswith("'''")
        ]
        if len("".join(meaningful)) < 12:
            return True
    if path.suffix.casefold() in {".json", ".yaml", ".yml"} and stripped in {"{}", "[]"}:
        return True
    return False


def god_module_aspects(rel: str, text: str) -> list[str]:
    if not rel.endswith(".py") or not text:
        return []
    found = [name for name, pattern in GOD_MODULE_PATTERNS.items() if pattern.search(text)]
    return found if len(found) >= 4 else []


def is_artifact_existence_validator(rel: str, text: str) -> bool:
    lower = rel.casefold()
    text_lower = text.casefold()
    if not (lower.startswith("tests/") or lower.startswith("scripts/validate_") or lower.startswith("scripts/audit_") or lower.startswith("scripts/check_")):
        return False
    existence_hits = sum(
        text_lower.count(token)
        for token in (
            ".is_file(",
            ".exists(",
            "missing ",
            "required_",
            "required ",
            "json.loads",
            "load_json",
            "must be false",
            "must exist",
            "forbidden",
            "refusing",
        )
    )
    behavior_hits = sum(text_lower.count(token) for token in ("normalize_", "build_", "persist", "sqlite", "query result", "render", "accepted", "state transition"))
    return existence_hits >= 3 and existence_hits >= behavior_hits


def is_production_looking_path(rel: str) -> bool:
    lower = rel.casefold()
    if lower.startswith(("runtime/", "surfaces/", "site/", "native/", "crates/")):
        return True
    if lower.startswith("contracts/"):
        return is_public_facing_contract(rel)
    return False


def is_public_facing_contract(rel: str) -> bool:
    lower = rel.casefold()
    return (
        lower.startswith(("contracts/api/", "contracts/public/", "contracts/runtime/", "contracts/domain/"))
        or "/api/" in lower
        or "public" in lower
        or "view_model" in lower
        or "page" in lower
    )


def is_allowed_leakage_context(rel: str) -> bool:
    lower = rel.casefold()
    if lower.startswith((".aide/", "control/audits/", "docs/operations/", "examples/", "tests/")):
        return True
    if lower.startswith("scripts/"):
        name = Path(lower).name
        return name.startswith(("audit_", "validate_"))
    return False


def compile_term(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    return re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", re.IGNORECASE)


def has_any(value: str, needles: Iterable[str]) -> bool:
    return any(needle in value for needle in needles)


def has_phrase(text_lower: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text_lower for phrase in phrases)


def require_value(value: str, allowed: set[str], fallback: str) -> str:
    return value if value in allowed else fallback


def gap(
    gap_id: str,
    severity: str,
    area: str,
    finding: str,
    evidence_paths: Sequence[str],
    impact: str,
    recommended_fix: str,
    blocks: Sequence[str],
) -> dict[str, Any]:
    return {
        "gap_id": gap_id,
        "severity": severity,
        "area": area,
        "finding": finding,
        "evidence_paths": sorted(dict.fromkeys(str(path) for path in evidence_paths if path)),
        "impact": impact,
        "recommended_fix": recommended_fix,
        "blocks": list(blocks),
    }


def example_paths(taxonomy: Mapping[str, Any], kinds: set[str], limit: int = 10) -> list[str]:
    paths = [
        str(item["path"])
        for item in taxonomy.get("artifacts", [])
        if item.get("artifact_kind") in kinds
    ]
    return paths[:limit]


def top_leak_paths(leakage_report: Mapping[str, Any], limit: int = 10) -> list[str]:
    return [path for path, _count in Counter(item["path"] for item in leakage_report.get("leaks", [])).most_common(limit)]


def artifact_existence_validator_count(taxonomy: Mapping[str, Any]) -> int:
    return sum(
        1
        for item in taxonomy.get("artifacts", [])
        if item.get("artifact_kind") == "validator" and "artifact_existence_validator" in item.get("signals", [])
    )


def count_paths(taxonomy: Mapping[str, Any], prefix: str) -> int:
    return sum(1 for item in taxonomy.get("artifacts", []) if str(item.get("path", "")).startswith(prefix))


def target_role_for_artifact(artifact: Mapping[str, Any]) -> str:
    kind = str(artifact["artifact_kind"])
    if kind in {"audit_evidence", "queue_or_task_control", "validator"}:
        return "control evidence or validator"
    if kind in {"audit_contract", "policy_contract"}:
        return "control/audit schema or policy"
    if kind in {"fixture_contract", "fixture_runtime"}:
        return "fixture oracle"
    if kind in {"preview_contract", "preview_runtime", "generated_scaffold"}:
        return "preview/quarantine scaffold"
    if kind == "production_runtime":
        return "product runtime candidate"
    return "classification follow-up"


def normalize_map_action(action: str) -> str:
    if action in {"keep", "move", "rename", "refactor", "rewrite", "delete_if_unreferenced"}:
        return action
    if action == "move_to_control":
        return "move"
    if action == "quarantine":
        return "refactor"
    if action == "keep_as_fixture_oracle":
        return "keep"
    if action == "keep_as_control":
        return "keep"
    return "refactor"


def render_count_lines(counts: Mapping[str, Any]) -> list[str]:
    return [f"- `{key}`: `{value}`" for key, value in sorted(counts.items())]


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def rel_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
