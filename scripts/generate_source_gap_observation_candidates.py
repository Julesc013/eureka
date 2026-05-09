"""Generate repo-local source gap observation candidates.

The generator is deliberately local and deterministic. It reads committed
policy, source inventory, eval, and candidate example files. It does not call
networks, browsers, APIs, models, providers, or external commands. Files are
written only when explicit output paths are supplied.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "control/inventory/observations/obs_agent_source_gap_candidate_policy.json"
PRIORITY_MODEL_PATH = "control/inventory/observations/obs_agent_source_gap_priority_model.json"
OBS01_MANIFEST_PATH = "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json"
SOURCE_SUMMARY_PATH = "site/dist/data/source_summary.json"
SOURCE_ACCESS_MODES_PATH = "control/inventory/observations/observation_source_access_modes.json"
EXTERNAL_SYSTEMS_PATH = "evals/search_usefulness/external_baselines/systems.json"
QUERY_PACK_PATH = "evals/search_usefulness/queries/search_usefulness_v0.json"
BATCH_MANIFEST_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/batch_manifest.json"
PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SOURCE_POLICY_DOC_PATH = "docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md"
LOCAL_EVAL_DOC_PATH = "docs/operations/OBS_AGENT_LOCAL_EVAL_FAILURE_MINING.md"
SOURCE_PAGE_VIEW_DOC_PATH = "docs/reference/SOURCE_PAGE_VIEW_MODEL_CONTRACT.md"
SOURCE_PACK_DOC_PATH = "docs/reference/SOURCE_PACK_CONTRACT.md"
SOURCE_CACHE_DOC_PATH = "docs/reference/SOURCE_CACHE_CONTRACT.md"
EVIDENCE_LEDGER_DOC_PATH = "docs/reference/EVIDENCE_LEDGER_CONTRACT.md"

SOURCE_INVENTORY_PATHS = (
    "control/inventory/sources/internet-archive-placeholder.source.json",
    "control/inventory/sources/internet-archive-recorded-fixtures.source.json",
    "control/inventory/sources/wayback-memento-placeholder.source.json",
    "control/inventory/sources/wayback-memento-recorded-fixtures.source.json",
    "control/inventory/sources/github-releases-recorded-fixtures.source.json",
    "control/inventory/sources/package-registry-recorded-fixtures.source.json",
    "control/inventory/sources/review-description-recorded-fixtures.source.json",
)

APPROVAL_AUDIT_PATHS = (
    "control/audits/internet-archive-metadata-connector-approval-v0",
    "control/audits/wayback-cdx-memento-connector-approval-v0",
    "control/audits/github-releases-connector-approval-v0",
    "control/audits/pypi-metadata-connector-approval-v0",
    "control/audits/npm-metadata-connector-approval-v0",
)

EXAMPLE_PATHS = (
    "examples/observation_candidates/source_gap_internet_archive_metadata_candidate_v0.json",
    "examples/observation_candidates/source_gap_wayback_metadata_candidate_v0.json",
    "examples/observation_candidates/source_gap_github_releases_candidate_v0.json",
    "examples/observation_candidates/source_gap_package_registry_candidate_v0.json",
    "examples/observation_candidates/source_gap_manual_only_forum_candidate_v0.json",
    "examples/observation_candidates/source_gap_policy_blocked_candidate_v0.json",
)

PRIMARY_INPUT_PATHS = (
    POLICY_PATH,
    PRIORITY_MODEL_PATH,
    OBS01_MANIFEST_PATH,
    SOURCE_SUMMARY_PATH,
    SOURCE_ACCESS_MODES_PATH,
    EXTERNAL_SYSTEMS_PATH,
    QUERY_PACK_PATH,
    BATCH_MANIFEST_PATH,
    PENDING_BATCH_PATH,
    SOURCE_POLICY_DOC_PATH,
    LOCAL_EVAL_DOC_PATH,
    SOURCE_PAGE_VIEW_DOC_PATH,
    SOURCE_PACK_DOC_PATH,
    SOURCE_CACHE_DOC_PATH,
    EVIDENCE_LEDGER_DOC_PATH,
    *SOURCE_INVENTORY_PATHS,
    *APPROVAL_AUDIT_PATHS,
    *EXAMPLE_PATHS,
)

PRODUCT_BOUNDARY = {
    "performed_observations": False,
    "automated_external_search": False,
    "scraped_external_systems": False,
    "crawled_external_systems": False,
    "called_external_apis": False,
    "opened_browsers": False,
    "fabricated_results": False,
    "marked_pending_as_observed": False,
    "changed_product_behavior": False,
    "changed_public_routes": False,
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "mutated_master_index": False,
    "approved_source_access": False,
    "modified_track_b_files": False,
}

ALLOWED_SOURCE_ACCESS_MODES = {
    "repo_local_only",
    "manual_human_only",
    "permission_needed",
    "no_autonomous_access",
    "approved_api_future",
    "approved_metadata_probe_future",
    "approved_static_dump_future",
    "restricted_demand_signal_only",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate OBS source gap candidates without external access.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate generation can produce a safe source-gap manifest.")
    parser.add_argument("--json-output", help="Explicit path for generated source gap manifest JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated Markdown summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output = stdout or sys.stdout

    if args.list_inputs:
        for path in list_input_paths(root):
            output.write(f"{path}\n")
        return 0

    manifest = build_source_gap_manifest(root)
    errors = validate_generated_manifest(manifest)

    if args.check:
        if errors:
            output.write("generate_source_gap_observation_candidates: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("generate_source_gap_observation_candidates: pass\n")
        output.write(f"source_gap_candidate_count: {manifest['source_gap_candidate_count']}\n")

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_summary(manifest))

    if not args.check and not args.json_output and not args.markdown_output:
        output.write(format_plain_summary(manifest))
    return 0 if not errors else 1


def list_input_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    policy = _mapping(_load_json(repo_root / POLICY_PATH))
    allowed_roots = _string_items(policy.get("allowed_input_roots"))
    inputs: list[str] = []
    for relative_path in PRIMARY_INPUT_PATHS:
        path = repo_root / relative_path
        if path.exists() and _allowed_by_policy(relative_path, allowed_roots):
            inputs.append(relative_path)
    return sorted(inputs)


def build_source_gap_manifest(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    policy = _mapping(_load_json(root / POLICY_PATH))
    priority_model = _mapping(_load_json(root / PRIORITY_MODEL_PATH))
    source_summary = _mapping(_load_json(root / SOURCE_SUMMARY_PATH))
    obs01_manifest = _mapping(_load_json(root / OBS01_MANIFEST_PATH))

    candidates = [_candidate_record_from_example(root, path) for path in EXAMPLE_PATHS]
    candidates = [candidate for candidate in candidates if candidate]
    candidates = sorted(candidates, key=lambda item: (-int(item["priority_score"]), str(item["observation_candidate_id"])))

    status_counts = Counter(str(item["candidate_status"]) for item in candidates)
    family_counts = Counter(str(item["source_family"]) for item in candidates)
    mode_counts = Counter(str(item["source_access_mode"]) for item in candidates)
    scores = [int(item["priority_score"]) for item in candidates]
    score_summary = _score_summary(scores)

    inspected_inputs = list_input_paths(root)
    inspected_roots = _inspected_roots(inspected_inputs, _string_items(policy.get("allowed_input_roots")))
    skipped_roots = _skipped_roots(_string_items(policy.get("allowed_input_roots")), inspected_roots)

    notes = [
        "Generated from committed repo-local materials only.",
        "Source gap candidates are review items, not source approvals.",
        "No live source access, browser use, API calls, scraping, crawling, downloads, model calls, or provider calls were performed.",
        "Track B local task packet was observed at TRACK-B-06; queue/context mutation is deferred to avoid overwriting parallel Track B state.",
    ]
    if not candidates:
        notes.append("insufficient_local_evidence")

    return {
        "schema_version": "obs_agent_source_gap_candidate_manifest.v0",
        "manifest_id": "obs_agent_source_gap_candidate_manifest_v0",
        "label": "OBS agent source gap candidate manifest",
        "description": "Deterministic repo-local source gap candidates for OBS-AGENT-02.",
        "generated_from": inspected_inputs,
        "source_policy": POLICY_PATH,
        "priority_model": PRIORITY_MODEL_PATH,
        "source_gap_candidate_count": len(candidates),
        "source_gap_candidates": candidates,
        "candidate_status_counts": dict(sorted(status_counts.items())),
        "source_family_counts": dict(sorted(family_counts.items())),
        "source_access_mode_counts": dict(sorted(mode_counts.items())),
        "priority_score_summary": score_summary,
        "source_roots_inspected": inspected_roots,
        "source_roots_skipped": skipped_roots,
        "local_evidence_summary": {
            "obs_agent_01_candidate_count": obs01_manifest.get("candidate_count", 0),
            "source_inventory_count": source_summary.get("source_count", 0),
            "source_summary_contains_live_data": source_summary.get("contains_live_data"),
            "source_summary_contains_live_probes": source_summary.get("contains_live_probes"),
        },
        "priority_model_summary": {
            "model_id": priority_model.get("model_id"),
            "score_minimum": _mapping(priority_model.get("score_fields")).get("minimum"),
            "score_maximum": _mapping(priority_model.get("score_fields")).get("maximum"),
            "advisory_only": _mapping(priority_model.get("output_interpretation")).get("advisory_only"),
        },
        "review_required": True,
        "truth_boundary": {
            "candidates_are_observed_baselines": False,
            "candidates_are_evidence_truth": False,
            "candidates_can_mutate_master_index": False,
            "human_review_required": True,
            "source_access_approved": False,
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "notes": notes,
    }


def validate_generated_manifest(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    records = [_mapping(item) for item in _sequence_items(manifest.get("source_gap_candidates"))]
    if manifest.get("source_gap_candidate_count") != len(records):
        errors.append("source_gap_candidate_count must match source_gap_candidates length")
    if manifest.get("review_required") is not True:
        errors.append("review_required must be true")
    errors.extend(_validate_truth_boundary(_mapping(manifest.get("truth_boundary")), "manifest"))
    errors.extend(_validate_product_boundary(_mapping(manifest.get("product_boundary")), "manifest"))

    status_counts = Counter(str(item.get("candidate_status")) for item in records)
    family_counts = Counter(str(item.get("source_family")) for item in records)
    mode_counts = Counter(str(item.get("source_access_mode")) for item in records)
    if manifest.get("candidate_status_counts") != dict(sorted(status_counts.items())):
        errors.append("candidate_status_counts must match source_gap_candidates")
    if manifest.get("source_family_counts") != dict(sorted(family_counts.items())):
        errors.append("source_family_counts must match source_gap_candidates")
    if manifest.get("source_access_mode_counts") != dict(sorted(mode_counts.items())):
        errors.append("source_access_mode_counts must match source_gap_candidates")

    for record in records:
        errors.extend(validate_generated_candidate_record(record))
    return sorted(set(errors))


def validate_generated_candidate_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate_id = str(record.get("observation_candidate_id", "<missing>"))
    for field in (
        "observation_candidate_id",
        "candidate_type",
        "candidate_status",
        "source_family",
        "source_access_mode",
        "source_policy_status",
        "related_query_ids",
        "related_batch_slots",
        "proposed_failure_modes",
        "source_gap_summary",
        "why_this_source_family",
        "recommended_next_review_action",
        "priority_score",
        "priority_score_rationale",
        "candidate_file_path",
    ):
        if field not in record:
            errors.append(f"{candidate_id}: missing {field}")
    if record.get("requires_human_review") is not True:
        errors.append(f"{candidate_id}: requires_human_review must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if record.get(field) is not False:
            errors.append(f"{candidate_id}: {field} must be false")
    mode = record.get("source_access_mode")
    if mode not in ALLOWED_SOURCE_ACCESS_MODES:
        errors.append(f"{candidate_id}: source_access_mode {mode!r} is not allowed")
    policy_status = str(record.get("source_policy_status", "")).lower()
    if mode in {"approved_api_future", "approved_metadata_probe_future", "approved_static_dump_future"}:
        if not any(marker in policy_status for marker in ("future", "deferred", "required")):
            errors.append(f"{candidate_id}: future source mode must remain future/deferred or policy-required")
    if record.get("candidate_status") == "policy_blocked" and "block" not in policy_status:
        errors.append(f"{candidate_id}: policy_blocked candidate must remain blocked")
    score = record.get("priority_score")
    if not isinstance(score, int) or score < 0 or score > 100:
        errors.append(f"{candidate_id}: priority_score must be an integer from 0 to 100")
    if _contains_forbidden_text(record):
        errors.append(f"{candidate_id}: forbidden source-access claim marker found")
    return errors


def format_plain_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "generate_source_gap_observation_candidates:",
        f"- source_gap_candidate_count: {manifest.get('source_gap_candidate_count')}",
        f"- source_family_counts: {json.dumps(manifest.get('source_family_counts', {}), sort_keys=True)}",
        f"- source_access_mode_counts: {json.dumps(manifest.get('source_access_mode_counts', {}), sort_keys=True)}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# Source Gap Candidate Summary",
        "",
        "OBS-AGENT-02 generated review-gated source gap candidates from committed repo-local materials only.",
        "",
        "## Source Families Recommended For Review",
        "",
        "| Priority | Candidate | Source family | Source mode | Review action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in _sequence_items(manifest.get("source_gap_candidates")):
        item = _mapping(record)
        lines.append(
            "| {} | `{}` | `{}` | `{}` | {} |".format(
                item.get("priority_score"),
                item.get("observation_candidate_id"),
                item.get("source_family"),
                item.get("source_access_mode"),
                item.get("recommended_next_review_action"),
            )
        )

    lines.extend(
        [
            "",
            "## Local Evidence",
            "",
        ]
    )
    for record in _sequence_items(manifest.get("source_gap_candidates")):
        item = _mapping(record)
        lines.extend(
            [
                f"- `{item.get('observation_candidate_id')}`: {item.get('source_gap_summary')}",
                f"  Evidence refs: {', '.join('`' + ref + '`' for ref in _string_items(item.get('evidence_refs')))}",
            ]
        )

    lines.extend(
        [
            "",
            "## Uncertain",
            "",
            "- Source fit is inferred from committed local inventories, audits, docs, eval query classes, and candidate examples.",
            "- No candidate is an observed baseline, accepted evidence, source approval, connector runtime, or master-index mutation.",
            "- Future Track B consumption depends on matching contracts and review gates.",
            "",
            "## Source Policy Decisions Needed",
            "",
            "- Internet Archive metadata policy.",
            "- Wayback/CDX/Memento availability and capture metadata policy.",
            "- GitHub Releases metadata policy.",
            "- PyPI/npm-style package metadata policy.",
            "- Manual-only community or forum lead policy.",
            "- Broad web recall baseline policy for any future approved API path.",
            "",
            "## Likely Future Seeds",
            "",
            "- SearchNeed seeds: Internet Archive, Wayback/CDX/Memento, GitHub Releases, and package registry metadata candidates.",
            "- WorkUnit seeds: source policy review packets for each candidate family.",
            "- Connector pattern candidates: metadata-only Internet Archive is the strongest first review target because it has high local relevance and a bounded metadata shape.",
            "",
            "## Policy-Blocked",
            "",
            "- `obs_candidate_source_gap_policy_blocked_v0` remains blocked for autonomous source access.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidate_record_from_example(repo_root: Path, candidate_path: str) -> dict[str, Any]:
    data = _mapping(_load_json(repo_root / candidate_path))
    if not data:
        return {}
    return {
        "observation_candidate_id": data.get("observation_candidate_id"),
        "candidate_type": data.get("candidate_type"),
        "candidate_status": data.get("candidate_status"),
        "source_family": data.get("source_family"),
        "source_access_mode": data.get("source_access_mode"),
        "source_policy_status": data.get("source_policy_status"),
        "related_query_ids": _related_query_ids(data),
        "related_batch_slots": _related_batch_slots(data),
        "proposed_failure_modes": _string_items(data.get("proposed_failure_modes")),
        "source_gap_summary": data.get("source_gap_summary"),
        "why_this_source_family": data.get("why_this_source_family"),
        "recommended_next_review_action": data.get("recommended_next_review_action"),
        "priority_score": data.get("priority_score"),
        "priority_band": data.get("priority_band"),
        "priority_score_rationale": _string_items(data.get("priority_score_rationale")),
        "candidate_file_path": candidate_path,
        "requires_human_review": data.get("required_human_review"),
        "accepted_as_observed_baseline": data.get("accepted_as_observed_baseline"),
        "accepted_as_evidence_truth": data.get("accepted_as_evidence_truth"),
        "master_index_mutation_allowed": data.get("master_index_mutation_allowed"),
        "evidence_refs": _string_items(data.get("evidence_refs")),
        "source_lead_refs": _string_items(data.get("source_lead_refs")),
        "work_unit_refs_future": _string_items(data.get("work_unit_refs_future")),
        "notes": _string_items(data.get("notes")),
    }


def _related_query_ids(data: Mapping[str, Any]) -> list[str]:
    query_id = data.get("related_query_id")
    return [str(query_id)] if isinstance(query_id, str) and query_id else []


def _related_batch_slots(data: Mapping[str, Any]) -> list[str]:
    slot_id = data.get("related_slot_id")
    return [str(slot_id)] if isinstance(slot_id, str) and slot_id else []


def _score_summary(scores: Sequence[int]) -> dict[str, Any]:
    if not scores:
        return {"min": 0, "max": 0, "average": 0}
    return {
        "min": min(scores),
        "max": max(scores),
        "average": round(sum(scores) / len(scores), 2),
    }


def _validate_truth_boundary(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    if boundary.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("candidates_are_observed_baselines", "candidates_are_evidence_truth", "candidates_can_mutate_master_index", "source_access_approved"):
        if boundary.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    return errors


def _validate_product_boundary(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field, expected in sorted(PRODUCT_BOUNDARY.items()):
        if boundary.get(field) is not expected:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _contains_forbidden_text(payload: Any) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    markers = (
        "google " + "scrape",
        "forum scrape",
        "live source observed",
        "external observation performed",
        "accepted evidence truth",
        "source access approved",
        "source sync enabled",
        "browser opened",
        "provider call completed",
        "model call completed",
    )
    return any(marker in text for marker in markers)


def _inspected_roots(inputs: Sequence[str], allowed_roots: Sequence[str]) -> list[str]:
    inspected: set[str] = set()
    for root in allowed_roots:
        prefix = root[:-3] if root.endswith("/**") else root
        if any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for path in inputs):
            inspected.add(root)
    return sorted(inspected)


def _skipped_roots(allowed_roots: Sequence[str], inspected_roots: Sequence[str]) -> list[str]:
    return sorted(set(allowed_roots) - set(inspected_roots))


def _allowed_by_policy(relative_path: str, allowed_roots: Sequence[str]) -> bool:
    normalized = relative_path.replace("\\", "/")
    for root in allowed_roots:
        if root.endswith("/**"):
            prefix = root[:-3].rstrip("/")
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return True
        elif normalized == root:
            return True
    return False


def _write_text(repo_root: Path, output_arg: str, text: str) -> None:
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _string_items(value: Any) -> list[str]:
    return [item for item in _sequence_items(value) if isinstance(item, str)]


if __name__ == "__main__":
    raise SystemExit(main())
