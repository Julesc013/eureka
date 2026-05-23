from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

REPORT_SCHEMA_VERSION = "track_a_11_projection_audit.v0"
MAP_SCHEMA_VERSION = "0.1.0"

SEARCH_PAGE_POLICY = "control/inventory/publication/search_page_view_model_policy.json"
ROUTE_MATRIX = "control/inventory/publication/route_view_representation_matrix.json"
REPRESENTATION_PROFILES = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_POLICY = "control/inventory/publication/semantic_renderer_parity_policy.json"
SEARCH_PAGE_SCHEMA = "contracts/view/pages/search_page.v0.json"

ARTIFACT_BINDINGS: tuple[dict[str, str], ...] = (
    {
        "artifact_path": "site/dist/search.html",
        "artifact_kind": "standard_static_html",
        "expected_representation_profile": "standard_html",
        "expected_route_family": "search",
        "expected_view_family": "SearchPageView",
    },
    {
        "artifact_path": "site/dist/lite/search.html",
        "artifact_kind": "lite_static_html",
        "expected_representation_profile": "lite_html",
        "expected_route_family": "lite_static",
        "expected_view_family": "SearchPageView",
    },
    {
        "artifact_path": "site/dist/text/search.txt",
        "artifact_kind": "text_static",
        "expected_representation_profile": "text",
        "expected_route_family": "text_static",
        "expected_view_family": "SearchPageView",
    },
    {
        "artifact_path": "site/dist/files/search.README.txt",
        "artifact_kind": "file_tree_static",
        "expected_representation_profile": "file_tree",
        "expected_route_family": "files_static",
        "expected_view_family": "SearchPageView",
    },
    {
        "artifact_path": "site/dist/data/search_handoff.json",
        "artifact_kind": "static_json_handoff",
        "expected_representation_profile": "api_json",
        "expected_route_family": "data_static",
        "expected_view_family": "SearchPageView",
    },
)

REQUIRED_BINDING_FIELDS = {
    "artifact_path",
    "artifact_kind",
    "exists",
    "expected_representation_profile",
    "expected_route_family",
    "expected_view_family",
    "current_status",
    "current_generation_source",
    "current_projection_status",
    "fields_present",
    "fields_missing",
    "semantic_risks",
    "refactor_needed",
    "notes",
}

PRODUCT_BOUNDARY = {
    "changed_product_behavior": False,
    "changed_public_routes": False,
    "changed_generated_site_artifacts": False,
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_installers": False,
    "enabled_execution": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "created_native_projects": False,
    "mutated_master_index": False,
    "claimed_rights_clearance": False,
    "claimed_malware_safety": False,
    "claimed_verified_installability": False,
    "claimed_exhaustive_global_search": False,
    "claimed_automatic_merge_or_promotion": False,
}

SEMANTIC_RULES: dict[str, tuple[str, ...]] = {
    "route_identity": ("search", "/search", "search.html"),
    "query_identity_or_search_handoff": ("search query", "query_parameter", "q=", "sample queries"),
    "public_runtime_posture": ("static handoff", "static search handoff", "static no-js search handoff", "search_handoff_status"),
    "local_index_only_or_hosted_unavailable_posture": (
        "local_index_only",
        "hosted public search is not configured",
        "hosted_backend_status",
        "not_deployed",
    ),
    "result_or_empty_state_meaning": ("sample queries", "default_result_limit", "public_index_document_count"),
    "source_evidence_posture": ("source placeholders", "source_inputs", "contains_external_observations"),
    "limitations": ("limitations", "does not run python", "static site does not run python"),
    "blocked_actions": ("disabled behavior", "disabled_behaviors", "no live probes"),
    "hosted_backend_unavailable_status": ("hosted_backend_status", "hosted public search is not configured", "not_deployed"),
    "live_probes_unavailable_status": ("no live probes", "live_probes_enabled"),
    "unsafe_capabilities_unavailable_status": (
        "no downloads",
        "downloads_enabled",
        "no uploads",
        "uploads_enabled",
        "no accounts",
        "accounts_enabled",
        "no telemetry",
        "telemetry_enabled",
        "telemetry disabled",
        "downloads, installs",
        "downloads, installs, uploads",
    ),
    "safe_next_action_or_handoff_instructions": (
        "local runtime instructions",
        "run_hosted_public_search.py --check-config",
        "available_for_local_prototype",
    ),
    "static_public_limitations": ("static", "static site", "static file", "does not run python"),
}

BOUNDARY_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "enabled_hosting": (
        re.compile(r"\bhosted backend (?:is )?(?:active|live|enabled|configured|verified|deployed)\b", re.IGNORECASE),
        re.compile(r"\bhosted public search (?:is )?(?:active|live|enabled|configured|verified|deployed)\b", re.IGNORECASE),
    ),
    "enabled_live_probes": (re.compile(r"\blive probes? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_source_sync": (re.compile(r"\bsource sync (?:is )?enabled\b", re.IGNORECASE),),
    "enabled_source_connectors": (re.compile(r"\bsource connectors? (?:are )?(?:active|enabled)\b", re.IGNORECASE),),
    "enabled_downloads": (re.compile(r"\b(?:direct )?downloads? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_installers": (re.compile(r"\binstallers? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_execution": (re.compile(r"\bexecution (?:is )?enabled\b", re.IGNORECASE),),
    "enabled_uploads": (re.compile(r"\buploads? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_accounts": (re.compile(r"\baccounts? (?:are )?enabled\b", re.IGNORECASE),),
    "enabled_telemetry": (re.compile(r"\btelemetry (?:is )?enabled\b", re.IGNORECASE),),
    "created_native_projects": (re.compile(r"\bnative runtime (?:is )?active\b", re.IGNORECASE),),
    "mutated_master_index": (re.compile(r"\bmaster[- ]index mutation (?:is )?(?:enabled|allowed|performed)\b", re.IGNORECASE),),
    "claimed_rights_clearance": (re.compile(r"\brights clearance (?:is )?(?:granted|verified|claimed)\b", re.IGNORECASE),),
    "claimed_malware_safety": (re.compile(r"\bmalware safety (?:is )?(?:verified|claimed)\b", re.IGNORECASE),),
    "claimed_verified_installability": (re.compile(r"\bverified installability\b", re.IGNORECASE),),
    "claimed_exhaustive_global_search": (re.compile(r"\bexhaustive global search\b", re.IGNORECASE),),
    "claimed_automatic_merge_or_promotion": (
        re.compile(r"\bautomatic (?:merge|dedup|promotion) (?:is )?(?:enabled|allowed)\b", re.IGNORECASE),
    ),
}

BOOLEAN_BOUNDARY_FIELDS = {
    "accounts_enabled": "enabled_accounts",
    "arbitrary_url_fetch_enabled": "enabled_source_connectors",
    "contains_live_backend": "enabled_hosting",
    "contains_live_probes": "enabled_live_probes",
    "crawling_enabled": "enabled_source_connectors",
    "deployment_performed": "enabled_hosting",
    "deployment_success_claimed": "enabled_hosting",
    "direct_download_enabled": "enabled_downloads",
    "downloads_enabled": "enabled_downloads",
    "execution_enabled": "enabled_execution",
    "hosted_backend_claim": "enabled_hosting",
    "hosted_backend_url_configured": "enabled_hosting",
    "hosted_backend_url_verified": "enabled_hosting",
    "hosted_form_enabled": "enabled_hosting",
    "installs_enabled": "enabled_installers",
    "live_probes_enabled": "enabled_live_probes",
    "malware_safety_claimed": "claimed_malware_safety",
    "master_index_mutation_allowed": "mutated_master_index",
    "native_runtime_active": "created_native_projects",
    "rights_clearance_claimed": "claimed_rights_clearance",
    "scraping_enabled": "enabled_source_connectors",
    "source_connectors_active": "enabled_source_connectors",
    "source_sync_enabled": "enabled_source_sync",
    "telemetry_enabled": "enabled_telemetry",
    "uploads_enabled": "enabled_uploads",
    "verified_installability_claimed": "claimed_verified_installability",
}

FUTURE_REFACTOR_TARGETS = [
    "TRACK-A-12 - Static SearchPage projection fixture and generator plan",
    "Create a canonical SearchPageView fixture for the current static handoff.",
    "Project the fixture into standard HTML, lite HTML, text, file-tree note, and static JSON handoff surfaces.",
    "Compare generated projections against current committed artifacts before any replacement.",
    "Preserve no-JS/static behavior and avoid hosted/live/download/upload/account/telemetry claims.",
    "Keep route identity stable; do not create profile-specific route splits.",
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit static SearchPage artifacts against SearchPageView semantics.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--check", action="store_true", help="Fail if critical product-boundary violations are found.")
    parser.add_argument("--json-output", help="Write deterministic JSON report to this explicit path.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    report = build_projection_audit(root)
    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output = stdout or sys.stdout
    output.write(_format_human(report))

    if args.check and report["critical_boundary_violations"]:
        return 1
    return 0


def build_projection_audit(
    repo_root: Path = REPO_ROOT,
    artifact_bindings: Sequence[Mapping[str, str]] = ARTIFACT_BINDINGS,
) -> dict[str, Any]:
    root = repo_root.resolve()
    load_warnings: list[str] = []
    search_policy = _load_json(root / SEARCH_PAGE_POLICY, load_warnings)
    route_matrix = _load_json(root / ROUTE_MATRIX, load_warnings)
    representations = _load_json(root / REPRESENTATION_PROFILES, load_warnings)
    semantic_policy = _load_json(root / SEMANTIC_PARITY_POLICY, load_warnings)

    representation_ids = _representation_ids(representations)
    route_ids = _route_ids(route_matrix)
    semantic_ids = _semantic_policy_ids(semantic_policy)

    bindings: list[dict[str, Any]] = []
    critical: list[str] = []
    warnings: list[str] = list(load_warnings)
    for binding in artifact_bindings:
        audited = audit_artifact(root, binding)
        bindings.append(audited)
        critical.extend(audited.pop("_critical_boundary_violations"))
        warnings.extend(audited.pop("_warnings"))

        profile = audited["expected_representation_profile"]
        if profile not in representation_ids:
            critical.append(f"{audited['artifact_path']}: unknown expected representation profile {profile}")
        route = audited["expected_route_family"]
        if route not in route_ids:
            critical.append(f"{audited['artifact_path']}: unknown expected route family {route}")

    policy_parity = _mapping(search_policy).get("required_semantic_parity_policy")
    if isinstance(policy_parity, str) and policy_parity not in semantic_ids:
        critical.append(f"{SEARCH_PAGE_POLICY}: unknown required semantic parity policy {policy_parity}")

    semantic_alignment = summarize_semantic_alignment(bindings)
    known_gaps = build_known_gaps(bindings, semantic_alignment)

    status = "fail" if critical else "warn" if warnings or known_gaps else "pass"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": status,
        "track": "A",
        "task": "TRACK-A-11",
        "audited_view_family": "SearchPageView",
        "source_view_schema": SEARCH_PAGE_SCHEMA,
        "audited_artifacts": [binding["artifact_path"] for binding in bindings],
        "artifact_bindings": bindings,
        "semantic_alignment": semantic_alignment,
        "known_alignment": [
            "All required SearchPage-related static artifact paths are present.",
            "Current artifacts visibly preserve static handoff and hosted-unavailable posture.",
            "Current artifacts visibly preserve disabled live-probe, download, upload, account, and telemetry posture.",
            "search_handoff.json structurally records local_index_only mode and false capability booleans.",
        ],
        "known_gaps": known_gaps,
        "critical_boundary_violations": sorted(set(critical)),
        "warnings": sorted(set(warnings)),
        "future_refactor_targets": FUTURE_REFACTOR_TARGETS,
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "no_goals_preserved": [
            "no site/dist regeneration",
            "no runtime behavior change",
            "no public route activation",
            "no hosted backend claim",
            "no live probes",
            "no downloads/installers/execution",
            "no uploads/accounts/telemetry",
            "no renderer refactor",
        ],
        "inputs": {
            "search_page_policy": SEARCH_PAGE_POLICY,
            "route_matrix": ROUTE_MATRIX,
            "representation_profiles": REPRESENTATION_PROFILES,
            "semantic_parity_policy": SEMANTIC_PARITY_POLICY,
        },
        "next_task": "TRACK-A-12 - Static SearchPage projection fixture and generator plan",
    }


def audit_artifact(repo_root: Path, binding: Mapping[str, str]) -> dict[str, Any]:
    path = str(binding["artifact_path"])
    target = repo_root / path
    base = {
        "artifact_path": path,
        "artifact_kind": str(binding["artifact_kind"]),
        "exists": target.is_file(),
        "expected_representation_profile": str(binding["expected_representation_profile"]),
        "expected_route_family": str(binding["expected_route_family"]),
        "expected_view_family": str(binding["expected_view_family"]),
        "current_status": "present" if target.is_file() else "missing",
        "current_generation_source": "not_machine_verified",
        "current_projection_status": "static_artifact_not_traced_to_canonical_search_page_view",
        "fields_present": [],
        "fields_missing": sorted(SEMANTIC_RULES),
        "semantic_risks": [],
        "refactor_needed": True,
        "notes": [],
        "_critical_boundary_violations": [],
        "_warnings": [],
    }
    if not target.is_file():
        base["notes"].append("Artifact is missing; audit records absence and does not create it.")
        base["_warnings"].append(f"{path}: artifact missing")
        return base

    text = target.read_text(encoding="utf-8")
    payload: Any | None = None
    if path.endswith(".json"):
        try:
            payload = json.loads(text)
            generated_by = _mapping(payload).get("generated_by")
            if isinstance(generated_by, str):
                base["current_generation_source"] = generated_by
        except json.JSONDecodeError as exc:
            base["_warnings"].append(f"{path}: JSON could not be parsed at line {exc.lineno}")

    present = sorted(category for category, needles in SEMANTIC_RULES.items() if _contains_any(text, needles))
    base["fields_present"] = present
    base["fields_missing"] = sorted(set(SEMANTIC_RULES) - set(present))
    base["semantic_risks"] = semantic_risks_for_artifact(path, base["fields_missing"], payload)
    base["notes"] = notes_for_artifact(path, payload)
    base["_critical_boundary_violations"] = detect_critical_boundary_violations(text, path, payload)
    base["_warnings"] = projection_warnings_for_artifact(path, binding, payload)
    return base


def summarize_semantic_alignment(bindings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    existing = [binding for binding in bindings if binding.get("exists") is True]
    existing_count = len(existing)
    for category in sorted(SEMANTIC_RULES):
        artifacts = sorted(
            str(binding["artifact_path"])
            for binding in existing
            if category in set(_string_items(binding.get("fields_present")))
        )
        if not artifacts:
            status = "missing"
        elif len(artifacts) == existing_count:
            status = "aligned"
        else:
            status = "partially_aligned"
        summary[category] = {
            "status": status,
            "artifacts": artifacts,
            "machine_verified": status != "missing",
            "notes": [
                "Conservative substring and JSON-field audit only; future A12 should compare against a canonical fixture."
            ],
        }
    return summary


def build_known_gaps(bindings: Sequence[Mapping[str, Any]], semantic_alignment: Mapping[str, Any]) -> list[str]:
    gaps = {
        "Current static artifacts are not generated from or traced to a canonical SearchPageView fixture.",
        "No artifact embeds a canonical SearchPageView view_model_id.",
        "A future generator should compare standard, lite, text, file-tree, and JSON projections against one fixture.",
    }
    for binding in bindings:
        if binding.get("fields_missing"):
            gaps.add(f"{binding['artifact_path']}: missing or not machine-verified fields {binding['fields_missing']}")
        for risk in _string_items(binding.get("semantic_risks")):
            gaps.add(f"{binding['artifact_path']}: {risk}")
    for category, alignment in semantic_alignment.items():
        if _mapping(alignment).get("status") != "aligned":
            gaps.add(f"{category}: {_mapping(alignment).get('status')} across audited artifacts")
    return sorted(gaps)


def detect_critical_boundary_violations(text: str, artifact_path: str, payload: Any | None = None) -> list[str]:
    violations: list[str] = []
    for boundary, patterns in BOUNDARY_PATTERNS.items():
        for pattern in patterns:
            if _has_unsafe_match(text, pattern):
                violations.append(f"{artifact_path}: {boundary} claim matched {pattern.pattern}")
                break
    if payload is not None:
        violations.extend(_json_boundary_violations(payload, artifact_path))
    return sorted(set(violations))


def _has_unsafe_match(text: str, pattern: re.Pattern[str]) -> bool:
    for match in pattern.finditer(text):
        if not _match_is_negated(text, match):
            return True
    return False


def _match_is_negated(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 32):match.start()].lower()
    matched = text[match.start():match.end()].lower()
    return (
        prefix.endswith("no ")
        or prefix.endswith("not ")
        or " no " in prefix[-12:]
        or " not " in prefix[-16:]
        or "does not " in prefix[-24:]
        or "not " in matched
    )


def semantic_risks_for_artifact(path: str, missing: Sequence[str], payload: Any | None) -> list[str]:
    risks = ["not yet traced to canonical SearchPageView fixture"]
    if missing:
        risks.append("some SearchPageView semantic categories are missing or not machine-verified")
    if path.endswith(".html") or path.endswith(".txt"):
        risks.append("semantic extraction is conservative text matching, not renderer parity proof")
    if payload is not None:
        static_routes = _mapping(payload).get("static_routes")
        if isinstance(static_routes, Sequence) and not isinstance(static_routes, (str, bytes)):
            profiles = sorted(
                str(item["profile"])
                for item in static_routes
                if isinstance(item, Mapping) and isinstance(item.get("profile"), str)
            )
            if "api_client" in profiles or "standard_web" in profiles:
                risks.append("legacy handoff profile labels need mapping to Track A representation profiles")
    return sorted(set(risks))


def notes_for_artifact(path: str, payload: Any | None) -> list[str]:
    notes = ["Read-only audit; artifact content was not changed."]
    if path.endswith(".json") and isinstance(payload, Mapping):
        if payload.get("no_hosted_search_claim") is True:
            notes.append("JSON handoff explicitly records no hosted search claim.")
        if _mapping(payload.get("disabled_behaviors")):
            notes.append("JSON handoff includes disabled behavior booleans.")
    return notes


def projection_warnings_for_artifact(path: str, binding: Mapping[str, str], payload: Any | None) -> list[str]:
    warnings: list[str] = []
    if isinstance(payload, Mapping):
        for route in payload.get("static_routes", []):
            if not isinstance(route, Mapping) or route.get("output_path") != path:
                continue
            profile = route.get("profile")
            expected = binding.get("expected_representation_profile")
            if isinstance(profile, str) and profile != expected:
                warnings.append(f"{path}: current handoff profile {profile!r} maps to expected Track A profile {expected!r}")
    return warnings


def _json_boundary_violations(value: Any, artifact_path: str, path: str = "$") -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            boundary = BOOLEAN_BOUNDARY_FIELDS.get(str(key))
            if boundary and child is True:
                violations.append(f"{artifact_path}: {child_path} implies {boundary}")
            violations.extend(_json_boundary_violations(child, artifact_path, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            violations.extend(_json_boundary_violations(child, artifact_path, f"{path}[{index}]"))
    return violations


def _contains_any(text: str, needles: Sequence[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def _load_json(path: Path, warnings: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        warnings.append(f"{path.as_posix()}: missing input JSON")
    except json.JSONDecodeError as exc:
        warnings.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}")
    return None


def _representation_ids(payload: Any) -> set[str]:
    profiles = _mapping(payload).get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)):
        return set()
    return {
        str(profile["representation_profile_id"])
        for profile in profiles
        if isinstance(profile, Mapping) and isinstance(profile.get("representation_profile_id"), str)
    }


def _route_ids(payload: Any) -> set[str]:
    routes = _mapping(payload).get("route_families")
    if not isinstance(routes, Sequence) or isinstance(routes, (str, bytes)):
        return set()
    return {
        str(route["route_family_id"])
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("route_family_id"), str)
    }


def _semantic_policy_ids(payload: Any) -> set[str]:
    policies = _mapping(payload).get("policies")
    if not isinstance(policies, Sequence) or isinstance(policies, (str, bytes)):
        return set()
    return {
        str(policy["parity_policy_id"])
        for policy in policies
        if isinstance(policy, Mapping) and isinstance(policy.get("parity_policy_id"), str)
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _format_human(report: Mapping[str, Any]) -> str:
    lines = [
        "Static SearchPage projection audit",
        f"status: {report['status']}",
        f"audited_view_family: {report['audited_view_family']}",
        f"artifact_count: {len(report['artifact_bindings'])}",
        f"critical_boundary_violations: {len(report['critical_boundary_violations'])}",
        f"warnings: {len(report['warnings'])}",
        f"known_gaps: {len(report['known_gaps'])}",
    ]
    for binding in report["artifact_bindings"]:
        lines.append(
            f"- {binding['artifact_path']}: {binding['current_status']}; "
            f"profile={binding['expected_representation_profile']}; "
            f"fields_present={len(binding['fields_present'])}; fields_missing={len(binding['fields_missing'])}"
        )
    if report["critical_boundary_violations"]:
        lines.append("critical_boundary_violations:")
        lines.extend(f"- {item}" for item in report["critical_boundary_violations"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {item}" for item in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
