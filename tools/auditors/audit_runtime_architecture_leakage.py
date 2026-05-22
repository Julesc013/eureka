#!/usr/bin/env python3
"""Audit task/control vocabulary leakage in production-looking paths.

R0-02 is a static, standard-library-only gate. It reads text files, applies a
repo-local policy and temporary allowlist, and reports whether task, prompt, or
audit vocabulary is present in product-shaped paths.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "R0-02"
DEFAULT_POLICY = Path("control/policies/runtime_architecture_leakage_policy.json")
DEFAULT_ALLOWLIST = Path("control/policies/runtime_architecture_leakage_allowlist.json")
AUDIT_DIR = Path("control/audits/r0-02-runtime-architecture-leakage-gate-v0")

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
    ".rs",
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
)

APPROVED_REPO_OUTPUT_ROOTS = (
    "control/inventory",
    AUDIT_DIR.as_posix(),
    "docs/architecture",
    "docs/operations",
    "control/policies",
)

REPLACEMENTS = {
    "H0": "domain role name",
    "H1": "source_observation",
    "H2": "source_observation",
    "H3": "source_observation",
    "H4": "source_observation",
    "H5": "source_observation",
    "H6": "source_observation",
    "H7": "source_observation",
    "H8": "source_observation",
    "H9": "source_observation",
    "H10": "source_observation",
    "H11": "source_observation",
    "H12": "source_observation",
    "H13": "source_observation",
    "H14": "source_observation",
    "BUNDLE": "domain capability name",
    "IA-BUNDLE": "internet_archive_source",
    "F-BUNDLE": "extraction_runtime",
    "G-BUNDLE": "search_quality",
    "MVP": "product capability stage",
    "LOCAL-MVP": "local_runtime",
    "AIDE": "control plane reference outside product paths",
    "prompt": "operator instruction outside product paths",
    "agent": "worker or operator outside product paths",
    "human_obs": "manual_observation",
    "fixture_only": "fixture helper outside product paths",
    "preview_only": "candidate preview outside product paths",
    "truth_boundary": "evidence_acceptance_policy",
    "product_boundary": "runtime_capability_boundary",
    "review_seed": "review_item",
    "next_phase": "next_required_task outside product paths",
    "quality_delta": "quality_metric_delta outside product paths",
    "integration_audit": "integration_report outside product paths",
}

BANNED_IMPORT_MARKERS = (
    "import urllib",
    "from urllib",
    "import requests",
    "import httpx",
    "import aiohttp",
    "import socket",
    "import ftplib",
    "import smtplib",
    "import webbrowser",
    "import selenium",
    "import playwright",
    "import openai",
    "import anthropic",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--write-standard-outputs", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    policy_path = resolve_input_path(root, args.policy)
    allowlist_path = resolve_input_path(root, args.allowlist)
    errors: list[str] = []
    try:
        policy = load_json(policy_path)
        allowlist = load_json(allowlist_path)
        validate_policy(policy, errors)
        validate_allowlist(allowlist, errors)
    except OSError as exc:
        errors.append(f"failed to read policy or allowlist: {exc}")
        policy = {}
        allowlist = {"entries": []}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed policy or allowlist JSON: {exc}")
        policy = {}
        allowlist = {"entries": []}

    if args.output:
        check_output_path(root, Path(args.output), errors)
    if args.summary_output:
        check_output_path(root, Path(args.summary_output), errors)

    audit = build_leakage_audit(root, policy, allowlist, policy_errors=errors)

    wrote_files = False
    if args.output and not errors:
        write_json(Path(args.output), audit["gate_report"])
        wrote_files = True
    if args.summary_output and not errors:
        write_text(Path(args.summary_output), render_scan_markdown(audit))
        wrote_files = True
    if args.write_standard_outputs and not errors:
        write_standard_outputs(root, audit)
        wrote_files = True
    audit["wrote_files"] = wrote_files

    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True), file=stdout)
    else:
        print(render_console_summary(audit), file=stdout)

    failure_reasons = list(audit["policy_errors"])
    if audit["summary"]["new_violation_count"]:
        failure_reasons.append("new unallowlisted production-path leakage found")
    if args.enforce and audit["summary"]["expired_allowlist_count"]:
        failure_reasons.append("expired allowlist entries found")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"ERROR: {reason}", file=stderr)
        return 1
    return 0


def resolve_input_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("schema_version") != "runtime_architecture_leakage_policy.v0":
        errors.append("policy schema_version must be runtime_architecture_leakage_policy.v0")
    if policy.get("status") != "active":
        errors.append("policy status must be active")
    for key in ("production_paths", "control_paths", "test_fixture_paths", "forbidden_terms", "forbidden_regexes"):
        if not isinstance(policy.get(key), list):
            errors.append(f"policy {key} must be a list")
    required_production = {
        "runtime/**",
        "surfaces/**",
        "site/**",
        "native/**",
        "crates/**",
        "contracts/domain/**",
        "contracts/runtime/**",
        "contracts/api/**",
        "contracts/snapshot/**",
        "contracts/native/**",
    }
    missing = required_production - set(policy.get("production_paths", []))
    if missing:
        errors.append(f"policy production_paths missing required paths: {sorted(missing)}")
    required_terms = {
        "H0",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "H7",
        "H8",
        "H9",
        "H10",
        "H11",
        "H12",
        "H13",
        "H14",
        "BUNDLE",
        "IA-BUNDLE",
        "F-BUNDLE",
        "G-BUNDLE",
        "MVP",
        "LOCAL-MVP",
        "AIDE",
        "prompt",
        "agent",
        "human_obs",
        "fixture_only",
        "preview_only",
        "truth_boundary",
        "product_boundary",
        "review_seed",
        "next_phase",
        "quality_delta",
        "integration_audit",
    }
    missing_terms = required_terms - set(policy.get("forbidden_terms", []))
    if missing_terms:
        errors.append(f"policy forbidden_terms missing required terms: {sorted(missing_terms)}")
    for item in policy.get("forbidden_regexes", []):
        pattern = item.get("pattern") if isinstance(item, Mapping) else str(item)
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"invalid forbidden_regex {pattern!r}: {exc}")


def validate_allowlist(allowlist: Mapping[str, Any], errors: list[str]) -> None:
    if allowlist.get("schema_version") != "runtime_architecture_leakage_allowlist.v0":
        errors.append("allowlist schema_version must be runtime_architecture_leakage_allowlist.v0")
    if not isinstance(allowlist.get("entries"), list):
        errors.append("allowlist entries must be a list")
        return
    required = {"path", "term", "reason", "expires_after_task", "owner", "replacement", "severity_after_expiry"}
    for index, entry in enumerate(allowlist.get("entries", [])[:25]):
        if not isinstance(entry, Mapping):
            errors.append(f"allowlist entry {index} must be an object")
            continue
        missing = required - set(entry)
        if missing:
            errors.append(f"allowlist entry {index} missing fields: {sorted(missing)}")


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
        errors.append(f"refusing repo output outside approved R0-02 paths: {relative}")


def build_leakage_audit(
    root: Path = REPO_ROOT,
    policy: Mapping[str, Any] | None = None,
    allowlist: Mapping[str, Any] | None = None,
    policy_errors: Sequence[str] | None = None,
    current_task: str = TASK_ID,
) -> dict[str, Any]:
    policy = policy or load_json(root / DEFAULT_POLICY)
    allowlist = allowlist or load_json(root / DEFAULT_ALLOWLIST)
    policy_errors = list(policy_errors or [])
    allowlist_entries = [entry for entry in allowlist.get("entries", []) if isinstance(entry, Mapping)]
    allowlist_index = build_allowlist_index(allowlist_entries)
    production_paths = tuple(str(item) for item in policy.get("production_paths", []))
    control_paths = tuple(str(item) for item in policy.get("control_paths", []))
    test_fixture_paths = tuple(str(item) for item in policy.get("test_fixture_paths", []))
    term_patterns = compile_term_patterns(policy.get("forbidden_terms", []))
    regex_patterns = compile_regex_patterns(policy.get("forbidden_regexes", []), policy_errors)

    findings: list[dict[str, Any]] = []
    allowed_usage_counts: Counter[str] = Counter()
    scanned_production_files: set[str] = set()
    scanned_control_files: set[str] = set()

    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        path_class = classify_path(rel, production_paths, control_paths, test_fixture_paths)
        if path_class == "outside_scope":
            continue
        if path_class == "production":
            scanned_production_files.add(rel)
        else:
            scanned_control_files.add(rel)

        file_hash = file_sha256(path)
        for match in scan_text(rel, rel, 0, term_patterns, regex_patterns, file_hash):
            if path_class == "production":
                findings.append(build_finding(match, path_class, allowlist_index, current_task))
            else:
                allowed_usage_counts[path_class] += 1

        for line_number, line in enumerate(read_text_lines(path), start=1):
            for match in scan_text(rel, line, line_number, term_patterns, regex_patterns, file_hash):
                if path_class == "production":
                    findings.append(build_finding(match, path_class, allowlist_index, current_task))
                else:
                    allowed_usage_counts[path_class] += 1

    findings = deduplicate_findings(findings)
    summary = summarize_findings(findings, scanned_production_files, scanned_control_files, allowed_usage_counts, allowlist_entries, current_task)
    gate_report = build_gate_report(summary, findings)
    blockers = build_blockers(findings)
    remediation = build_remediation_plan(findings)
    return {
        "schema_version": "runtime_architecture_leakage_scan.v0",
        "task": TASK_ID,
        "policy_id": policy.get("policy_id"),
        "allowlist_id": allowlist.get("allowlist_id"),
        "enforcement_mode": policy.get("enforcement_mode"),
        "scan_scope": sorted(set(policy.get("production_paths", []) + policy.get("control_paths", []))),
        "policy_errors": policy_errors,
        "summary": summary,
        "gate_report": gate_report,
        "blockers": blockers,
        "remediation_plan": remediation,
        "findings": findings,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": gate_report["recommended_next_task"],
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "runtime_modules_imported": False,
    }


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORED_DIRS for part in rel_parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
        except OSError:
            continue
        yield path


def read_text_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            return []
    except OSError:
        return []


def file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def match_path_pattern(rel: str, pattern: str) -> bool:
    normalized = rel.replace("\\", "/")
    pattern = pattern.replace("\\", "/")
    if pattern.endswith("/**") and not any(char in pattern[:-3] for char in "*?["):
        prefix = pattern[:-3]
        return normalized == prefix.rstrip("/") or normalized.startswith(prefix)
    return fnmatch.fnmatchcase(normalized, pattern)


def classify_path(rel: str, production_paths: Sequence[str], control_paths: Sequence[str], test_fixture_paths: Sequence[str]) -> str:
    if any(match_path_pattern(rel, pattern) for pattern in test_fixture_paths):
        return "allowed_test_fixture_usage"
    if any(match_path_pattern(rel, pattern) for pattern in control_paths):
        return "allowed_control_usage"
    if any(match_path_pattern(rel, pattern) for pattern in production_paths):
        return "production"
    return "outside_scope"


def compile_term_patterns(terms: Sequence[Any]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for term in sorted({str(term) for term in terms}, key=len, reverse=True):
        flags = 0 if is_case_sensitive_forbidden_term(term) else re.IGNORECASE
        pattern = re.compile(rf"(?<![A-Za-z0-9])({re.escape(term)})(?![A-Za-z0-9])", flags)
        patterns.append({"term": "forbidden_term", "pattern": pattern, "source": "term", "canonical_term": term})
    return patterns


def is_case_sensitive_forbidden_term(term: str) -> bool:
    return term in {"BUNDLE", "IA-BUNDLE", "F-BUNDLE", "G-BUNDLE", "MVP", "LOCAL-MVP", "AIDE"}


def compile_regex_patterns(regexes: Sequence[Any], errors: list[str]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for item in regexes:
        if isinstance(item, Mapping):
            term = str(item.get("id", item.get("pattern", "regex")))
            pattern = str(item.get("pattern", ""))
            replacement = str(item.get("recommended_replacement", "Replace task vocabulary with domain vocabulary."))
        else:
            term = "forbidden_regex"
            pattern = str(item)
            replacement = "Replace task vocabulary with domain vocabulary."
        try:
            patterns.append({"term": term, "pattern": re.compile(pattern), "source": "regex", "replacement": replacement})
        except re.error as exc:
            errors.append(f"invalid forbidden_regex {pattern!r}: {exc}")
    return patterns


def scan_text(
    rel: str,
    text: str,
    line_number: int,
    term_patterns: Sequence[Mapping[str, Any]],
    regex_patterns: Sequence[Mapping[str, Any]],
    file_hash: str,
) -> Iterable[dict[str, Any]]:
    seen: set[tuple[str, int, int]] = set()
    for item in term_patterns:
        for match in item["pattern"].finditer(text):
            term = canonical_term(match.group(1))
            key = (term, line_number, match.start() + 1)
            if key in seen:
                continue
            seen.add(key)
            yield make_match(rel, term, text, line_number, match.start() + 1, "term", file_hash)
    for item in regex_patterns:
        term = str(item["term"])
        for match in item["pattern"].finditer(text):
            key = (term, line_number, match.start() + 1)
            if key in seen:
                continue
            seen.add(key)
            payload = make_match(rel, term, text, line_number, match.start() + 1, "regex", file_hash)
            payload["recommended_replacement"] = str(item.get("replacement", "Replace task vocabulary with domain vocabulary."))
            yield payload


def make_match(rel: str, term: str, text: str, line_number: int, column: int, source: str, file_hash: str) -> dict[str, Any]:
    snippet = compact_context(text)
    return {
        "path": rel,
        "line": line_number,
        "column": column,
        "term": canonical_term(term),
        "raw_term": term,
        "match_source": source,
        "context": snippet,
        "context_sha256": hashlib.sha256(snippet.encode("utf-8")).hexdigest(),
        "file_sha256": file_hash,
    }


def canonical_term(term: str) -> str:
    for known in REPLACEMENTS:
        if term.casefold() == known.casefold():
            return known
    return term


def compact_context(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())[:240]


def build_allowlist_index(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    exact: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    glob_entries: list[Mapping[str, Any]] = []
    for entry in entries:
        path = str(entry.get("path", ""))
        term = str(entry.get("term", "")).casefold()
        if "*" in path or "?" in path or term == "*":
            glob_entries.append(entry)
            continue
        exact.setdefault((path, term), []).append(entry)
    return {"exact": exact, "glob": glob_entries}


def build_finding(match: Mapping[str, Any], path_class: str, allowlist_index: Mapping[str, Any], current_task: str) -> dict[str, Any]:
    classification = "new_violation"
    allowlist_entry = find_allowlist_entry(match, allowlist_index)
    expired = False
    if allowlist_entry:
        expired = is_expired_allowlist_entry(allowlist_entry, current_task)
        classification = "existing_known_violation"
    if is_false_positive_candidate(match):
        classification = "false_positive_candidate"
    severity = severity_for(match)
    recommendation = recommendation_for(match)
    return {
        "path": match["path"],
        "line": match["line"],
        "column": match["column"],
        "term": match["term"],
        "raw_term": match.get("raw_term", match["term"]),
        "match_source": match.get("match_source", "term"),
        "context": match["context"],
        "context_sha256": match["context_sha256"],
        "file_sha256": match.get("file_sha256", ""),
        "path_class": path_class,
        "classification": classification,
        "allowlisted": bool(allowlist_entry),
        "allowlist_expired": expired,
        "severity": severity,
        "recommended_replacement": match.get("recommended_replacement") or recommendation,
        "recommended_action": "refactor or quarantine task vocabulary before production promotion",
    }


def find_allowlist_entry(match: Mapping[str, Any], allowlist_index: Mapping[str, Any]) -> Mapping[str, Any] | None:
    path = str(match.get("path"))
    term = str(match.get("term")).casefold()
    candidates = list(allowlist_index.get("exact", {}).get((path, term), []))
    candidates.extend(allowlist_index.get("glob", []))
    for entry in candidates:
        if str(entry.get("path")) != str(match.get("path")) and not fnmatch.fnmatchcase(str(match.get("path")), str(entry.get("path"))):
            continue
        if str(entry.get("term")).casefold() != str(match.get("term")).casefold() and str(entry.get("term")) != "*":
            continue
        line = entry.get("line")
        if line is not None and int(line) != int(match.get("line", -1)):
            continue
        column = entry.get("column")
        if column is not None and int(column) != int(match.get("column", -1)):
            continue
        context_hash = entry.get("context_sha256")
        if context_hash and str(context_hash) != str(match.get("context_sha256")):
            continue
        file_hash = entry.get("file_sha256")
        if file_hash and str(file_hash) != str(match.get("file_sha256")):
            continue
        return entry
    return None


def is_expired_allowlist_entry(entry: Mapping[str, Any], current_task: str) -> bool:
    expires = str(entry.get("expires_after_task", "")).strip()
    if not expires or expires == "never":
        return False
    return task_order(expires) < task_order(current_task)


def task_order(task_id: str) -> int:
    match = re.search(r"R(\d+)-(\d+)", task_id)
    if not match:
        return 10_000
    return int(match.group(1)) * 100 + int(match.group(2))


def is_false_positive_candidate(match: Mapping[str, Any]) -> bool:
    term = str(match.get("term", "")).casefold()
    context = str(match.get("context", "")).casefold()
    if term in {"h1", "h2", "h3", "h4", "h5", "h6"} and f"<{term}" in context:
        return True
    if term == "bundle" and any(
        marker in context
        for marker in (
            "local bundle",
            "local-bundle",
            "local_bundle",
            "support bundle",
            "bundle fixture",
            "bundle recorded fixture",
            "software bundle",
            "fixture bundle",
        )
    ):
        return True
    if term == "agent" and any(marker in context for marker in ("user-agent", "user_agent", "agentless", "browser agent string")):
        return True
    path = str(match.get("path", "")).replace("\\", "/").casefold()
    if term == "agent" and (
        path.startswith("runtime/agent_research/")
        or any(
            marker in context
            for marker in (
                "agent research",
                "agent_research",
                "agent-research",
                "agent_task",
                "agent-task",
                "agent-tasks",
                "agent_tasks",
                "agent task",
                "agent token",
                "agent-token",
                "agentresearch",
            )
        )
    ):
        return True
    return False


def severity_for(match: Mapping[str, Any]) -> str:
    path = str(match.get("path", ""))
    term = str(match.get("term", ""))
    if term.startswith("H") or term in {"BUNDLE", "IA-BUNDLE", "F-BUNDLE", "G-BUNDLE", "MVP", "LOCAL-MVP", "phase_bundle_identifier", "phase_named_runtime_symbol"}:
        return "blocker" if not path.startswith("contracts/") else "medium"
    if term in {"truth_boundary", "product_boundary", "review_seed", "fixture_only", "preview_only"}:
        return "high" if not path.startswith("contracts/") else "medium"
    if term in {"AIDE", "prompt", "agent", "human_obs", "next_phase", "quality_delta", "integration_audit"}:
        return "high" if not path.startswith("contracts/") else "medium"
    return "low"


def recommendation_for(match: Mapping[str, Any]) -> str:
    term = str(match.get("term", ""))
    return f"Replace {term} with {REPLACEMENTS.get(term, 'domain vocabulary')} or move the artifact to control/test scope."


def deduplicate_findings(findings: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, int, int, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for finding in findings:
        key = (
            str(finding.get("path")),
            int(finding.get("line", -1)),
            int(finding.get("column", -1)),
            str(finding.get("term")),
            str(finding.get("match_source")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(dict(finding))
    return unique


def summarize_findings(
    findings: Sequence[Mapping[str, Any]],
    production_files: set[str],
    control_files: set[str],
    allowed_usage_counts: Counter[str],
    allowlist_entries: Sequence[Mapping[str, Any]],
    current_task: str,
) -> dict[str, Any]:
    new_findings = [item for item in findings if item.get("classification") == "new_violation"]
    known_findings = [item for item in findings if item.get("classification") == "existing_known_violation"]
    expired_entries = [entry for entry in allowlist_entries if is_expired_allowlist_entry(entry, current_task)]
    severity_counts = Counter(str(item.get("severity", "low")) for item in new_findings)
    known_severity_counts = Counter(str(item.get("severity", "low")) for item in known_findings)
    return {
        "production_path_count": len(production_files),
        "control_path_count": len(control_files),
        "known_allowlisted_violation_count": len(known_findings),
        "new_violation_count": len(new_findings),
        "false_positive_candidate_count": sum(1 for item in findings if item.get("classification") == "false_positive_candidate"),
        "expired_allowlist_count": len(expired_entries),
        "blocker_count": severity_counts.get("blocker", 0),
        "high_count": severity_counts.get("high", 0),
        "medium_count": severity_counts.get("medium", 0),
        "low_count": severity_counts.get("low", 0),
        "known_blocker_count": known_severity_counts.get("blocker", 0),
        "known_high_count": known_severity_counts.get("high", 0),
        "known_medium_count": known_severity_counts.get("medium", 0),
        "known_low_count": known_severity_counts.get("low", 0),
        "top_terms": top_counter(Counter(str(item.get("term")) for item in findings)),
        "top_paths": top_counter(Counter(str(item.get("path")) for item in findings)),
        "allowed_usage_counts": dict(sorted(allowed_usage_counts.items())),
    }


def top_counter(counter: Counter[str], limit: int = 10) -> list[dict[str, Any]]:
    return [{"value": key, "count": count} for key, count in counter.most_common(limit)]


def build_gate_report(summary: Mapping[str, Any], findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    status = "pass_with_warnings" if summary.get("known_allowlisted_violation_count") else "pass"
    if summary.get("new_violation_count"):
        status = "fail"
    return {
        "schema_version": "runtime_architecture_leakage_gate_report.v0",
        "task": TASK_ID,
        "status": status,
        "scan_scope": [
            "runtime/**",
            "surfaces/**",
            "site/**",
            "native/**",
            "crates/**",
            "contracts/**",
        ],
        "production_path_count": summary.get("production_path_count", 0),
        "control_path_count": summary.get("control_path_count", 0),
        "known_allowlisted_violation_count": summary.get("known_allowlisted_violation_count", 0),
        "new_violation_count": summary.get("new_violation_count", 0),
        "expired_allowlist_count": summary.get("expired_allowlist_count", 0),
        "blocker_count": summary.get("blocker_count", 0),
        "high_count": summary.get("high_count", 0),
        "medium_count": summary.get("medium_count", 0),
        "low_count": summary.get("low_count", 0),
        "top_terms": summary.get("top_terms", []),
        "top_paths": summary.get("top_paths", []),
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03 — Contract taxonomy refactor",
    }


def build_blockers(findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    blockers = []
    for index, finding in enumerate((item for item in findings if item.get("classification") == "new_violation"), start=1):
        blockers.append(
            {
                "blocker_id": f"R0-LEAK-BLOCKER-{index:03d}",
                "path": finding["path"],
                "term": finding["term"],
                "severity": finding["severity"],
                "reason": "Unallowlisted task/control vocabulary appears in a production-looking path.",
                "recommended_fix": finding["recommended_replacement"],
                "blocks": ["F0-BUNDLE-01", "DEV-TO-MAIN-PRODUCTION-REVIEW"],
            }
        )
    return {"schema_version": "runtime_architecture_leakage_blockers.v0", "blockers": blockers}


def build_remediation_plan(findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    known = [item for item in findings if item.get("classification") == "existing_known_violation"]
    top_paths = [item["value"] for item in top_counter(Counter(str(item.get("path")) for item in known), limit=8)]
    return {
        "schema_version": "runtime_architecture_leakage_remediation_plan.v0",
        "recommended_sequence": [
            "R0-03 — Contract taxonomy refactor",
            "R0-04 — Source observation production seam",
            "R0-05 — Durable source cache store",
        ],
        "renames": [
            {
                "from": "task/phase-named runtime symbols",
                "to": "domain role names such as source_observation, evidence_ledger, review_queue, and connector_health",
                "task": "R0-04",
            }
        ],
        "moves": [
            {
                "from": "audit, fixture, or preview contracts under production contract paths",
                "to": "control/audit_schemas, control/fixture_schemas, or control/preview_schemas",
                "task": "R0-03",
            }
        ],
        "quarantines": [{"path": path, "task": "R0-03 or R0-04"} for path in top_paths],
        "rewrites": [
            {
                "scope": "runtime connector modules with H-series names or truth/product boundary symbols",
                "task": "R0-04",
            }
        ],
        "do_not_do": [
            "do not rename or move runtime paths inside R0-02",
            "do not silently bless known leaks forever",
            "do not resume F0 until at least the R0-02 gate is active and downstream remediation is scheduled",
            "do not promote dev to main while production-path task vocabulary remains unresolved",
        ],
    }


def build_r0_report(audit: Mapping[str, Any]) -> dict[str, Any]:
    gate = audit["gate_report"]
    summary = audit["summary"]
    return {
        "schema_version": "r0_02_report.v0",
        "status": gate["status"],
        "task": TASK_ID,
        "purpose": "runtime_architecture_leakage_gate",
        "policy_added": True,
        "allowlist_added": True,
        "audit_script_added": True,
        "validator_added": True,
        "tests_added": True,
        "docs_added": True,
        "production_paths_modified": False,
        "runtime_refactor_performed": False,
        "contract_moves_performed": False,
        "known_allowlisted_violation_count": summary["known_allowlisted_violation_count"],
        "new_violation_count": summary["new_violation_count"],
        "expired_allowlist_count": summary["expired_allowlist_count"],
        "blocker_count": summary["blocker_count"],
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03 — Contract taxonomy refactor",
        "validation": {
            "audit_script_check_mode": "pending",
            "validator": "pending",
            "unit_tests": "pending",
            "full_unittest_discovery": "pending",
            "architecture_boundaries": "pending",
        },
    }


def render_console_summary(audit: Mapping[str, Any]) -> str:
    summary = audit["summary"]
    lines = [
        "R0-02 runtime architecture leakage gate",
        f"status: {audit['gate_report']['status']}",
        f"production_path_count: {summary['production_path_count']}",
        f"known_allowlisted_violation_count: {summary['known_allowlisted_violation_count']}",
        f"new_violation_count: {summary['new_violation_count']}",
        f"expired_allowlist_count: {summary['expired_allowlist_count']}",
        f"wrote_files: {str(audit.get('wrote_files', False)).lower()}",
        "f0_should_remain_blocked: true",
        "dev_to_main_should_remain_blocked: true",
    ]
    for finding in audit.get("findings", [])[:10]:
        lines.append(
            f"{finding['classification']}: {finding['path']}:{finding['line']}:{finding['column']} "
            f"{finding['term']} {finding['severity']}"
        )
    return "\n".join(lines)


def render_scan_markdown(audit: Mapping[str, Any]) -> str:
    summary = audit["summary"]
    lines = [
        "# R0-02 Runtime Architecture Leakage Gate",
        "",
        f"- status: {audit['gate_report']['status']}",
        f"- production paths scanned: {summary['production_path_count']}",
        f"- known allowlisted violations: {summary['known_allowlisted_violation_count']}",
        f"- new violations: {summary['new_violation_count']}",
        f"- expired allowlist entries: {summary['expired_allowlist_count']}",
        f"- F0 remains blocked: {str(audit['f0_should_remain_blocked']).lower()}",
        f"- dev-to-main remains blocked: {str(audit['dev_to_main_should_remain_blocked']).lower()}",
        "",
        "## Top Terms",
        "",
    ]
    for item in summary.get("top_terms", []):
        lines.append(f"- {item['value']}: {item['count']}")
    lines.extend(["", "## New Violations", ""])
    new_findings = [item for item in audit.get("findings", []) if item.get("classification") == "new_violation"]
    if not new_findings:
        lines.append("- none")
    for item in new_findings[:25]:
        lines.append(f"- {item['path']}:{item['line']}:{item['column']} {item['term']} ({item['severity']})")
    lines.extend(["", "## Known Temporary Debt", ""])
    for item in [entry for entry in audit.get("findings", []) if entry.get("classification") == "existing_known_violation"][:25]:
        lines.append(f"- {item['path']}:{item['line']}:{item['column']} {item['term']} ({item['severity']})")
    return "\n".join(lines) + "\n"


def render_known_violations_markdown(audit: Mapping[str, Any]) -> str:
    known = [item for item in audit.get("findings", []) if item.get("classification") == "existing_known_violation"]
    lines = ["# Known Temporary Violations", "", f"Known allowlisted violations: {len(known)}", ""]
    for item in known[:200]:
        lines.append(f"- {item['path']}:{item['line']}:{item['column']} `{item['term']}` -> {item['recommended_replacement']}")
    if len(known) > 200:
        lines.append(f"- ... {len(known) - 200} additional allowlisted findings are in the JSON reports.")
    return "\n".join(lines) + "\n"


def render_policy_summary(policy: Mapping[str, Any], allowlist: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Leakage Policy Summary",
            "",
            f"- policy id: {policy.get('policy_id')}",
            f"- enforcement mode: {policy.get('enforcement_mode')}",
            f"- production path patterns: {len(policy.get('production_paths', []))}",
            f"- control path patterns: {len(policy.get('control_paths', []))}",
            f"- forbidden terms: {len(policy.get('forbidden_terms', []))}",
            f"- forbidden regexes: {len(policy.get('forbidden_regexes', []))}",
            f"- allowlist entries: {len(allowlist.get('entries', []))}",
            "",
        ]
    )


def render_validation_markdown(audit: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Validation",
            "",
            "- audit script check mode: pending",
            "- validator: pending",
            "- operation tests: pending",
            "- full unittest discovery: pending",
            "- architecture boundary check: pending",
            "",
            "R0-02 validation records are updated after the required commands are run.",
            "",
            f"F0 remains blocked: {str(audit['f0_should_remain_blocked']).lower()}",
            f"dev-to-main remains blocked: {str(audit['dev_to_main_should_remain_blocked']).lower()}",
            "",
        ]
    )


def write_standard_outputs(root: Path, audit: Mapping[str, Any]) -> None:
    policy = load_json(root / DEFAULT_POLICY)
    allowlist = load_json(root / DEFAULT_ALLOWLIST)
    outputs: dict[str, Any] = {
        "control/inventory/runtime_architecture_leakage_gate_report.json": audit["gate_report"],
        "control/inventory/runtime_architecture_leakage_blockers.json": audit["blockers"],
        "control/inventory/runtime_architecture_leakage_remediation_plan.json": audit["remediation_plan"],
        f"{AUDIT_DIR.as_posix()}/r0_02_report.json": build_r0_report(audit),
        f"{AUDIT_DIR.as_posix()}/generated/sample_leakage_gate_report.json": audit["gate_report"],
    }
    for rel, payload in outputs.items():
        write_json(root / rel, payload)
    markdown_outputs = {
        f"{AUDIT_DIR.as_posix()}/README.md": "# R0-02 Runtime Architecture Leakage Gate\n\nThis audit pack records the static leakage gate added by R0-02.\n\n",
        f"{AUDIT_DIR.as_posix()}/leakage_policy_summary.md": render_policy_summary(policy, allowlist),
        f"{AUDIT_DIR.as_posix()}/allowlist_summary.md": render_allowlist_summary(allowlist),
        f"{AUDIT_DIR.as_posix()}/production_path_scan_summary.md": render_scan_markdown(audit),
        f"{AUDIT_DIR.as_posix()}/known_violations.md": render_known_violations_markdown(audit),
        f"{AUDIT_DIR.as_posix()}/remediation_plan.md": render_remediation_markdown(audit["remediation_plan"]),
        f"{AUDIT_DIR.as_posix()}/validation.md": render_validation_markdown(audit),
        f"{AUDIT_DIR.as_posix()}/generated/sample_leakage_summary.md": render_scan_markdown(audit),
    }
    for rel, text in markdown_outputs.items():
        write_text(root / rel, text)


def render_allowlist_summary(allowlist: Mapping[str, Any]) -> str:
    entries = [entry for entry in allowlist.get("entries", []) if isinstance(entry, Mapping)]
    by_expiry = Counter(str(entry.get("expires_after_task", "unknown")) for entry in entries)
    lines = ["# Allowlist Summary", "", f"entries: {len(entries)}", ""]
    for key, count in by_expiry.most_common():
        lines.append(f"- expires after {key}: {count}")
    lines.extend(["", "The allowlist is exact-match remediation debt, not a permanent waiver.\n"])
    return "\n".join(lines)


def render_remediation_markdown(plan: Mapping[str, Any]) -> str:
    lines = ["# Remediation Plan", "", "## Recommended Sequence", ""]
    for item in plan.get("recommended_sequence", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Do Not Do", ""])
    for item in plan.get("do_not_do", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
