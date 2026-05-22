"""Mine repo-local eval materials into review-gated observation candidates.

The miner is deliberately local and deterministic. It reads committed files,
does not call external tools or networks, and writes output only when explicit
paths are supplied.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = "control/inventory/observations/obs_agent_local_eval_failure_mining_policy.json"
BATCH_MANIFEST_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/batch_manifest.json"
PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
QUERY_PACK_PATH = "evals/search_usefulness/queries/search_usefulness_v0.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
SOURCE_MODES_PATH = "control/inventory/observations/observation_source_access_modes.json"
FAILURE_TAXONOMY_PATH = "control/inventory/observations/manual_observation_failure_taxonomy.json"
EVAL_SUMMARY_PATH = "site/dist/data/eval_summary.json"
DEMO_SNAPSHOTS_PATH = "site/dist/demo/data/demo_snapshots.json"
SOURCE_POLICY_DOC_PATH = "docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md"
AGENT_WORKFLOW_DOC_PATH = "docs/operations/AGENT_ASSISTED_OBSERVATION_WORKFLOW.md"
FAILURE_TAXONOMY_DOC_PATH = "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md"
OBS_REPLAN_REPORT_PATH = "control/audits/obs-replan-01-agent-assisted-observation-workflow-v0/obs_replan_01_report.json"
OBS0_02_REPORT_PATH = "control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/obs0_02_report.json"

PRIMARY_INPUT_PATHS = (
    POLICY_PATH,
    QUERY_PACK_PATH,
    BATCH_MANIFEST_PATH,
    PENDING_BATCH_PATH,
    SLOT_MANIFEST_PATH,
    SOURCE_MODES_PATH,
    FAILURE_TAXONOMY_PATH,
    EVAL_SUMMARY_PATH,
    DEMO_SNAPSHOTS_PATH,
    SOURCE_POLICY_DOC_PATH,
    AGENT_WORKFLOW_DOC_PATH,
    FAILURE_TAXONOMY_DOC_PATH,
    OBS_REPLAN_REPORT_PATH,
    OBS0_02_REPORT_PATH,
)

CANDIDATE_FILES = {
    "obs_candidate_local_eval_failure_mining_batch_0_v0": "examples/observation_candidates/local_eval_failure_mining_batch_0_v0.json",
    "obs_candidate_local_eval_source_gap_v0": "examples/observation_candidates/local_eval_source_gap_candidate_v0.json",
    "obs_candidate_local_eval_extraction_gap_v0": "examples/observation_candidates/local_eval_extraction_gap_candidate_v0.json",
    "obs_candidate_local_eval_ranking_gap_v0": "examples/observation_candidates/local_eval_ranking_gap_candidate_v0.json",
    "obs_candidate_local_eval_policy_blocked_v0": "examples/observation_candidates/local_eval_policy_blocked_candidate_v0.json",
}

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
    "modified_track_b_files": False,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mine local eval failure candidates without external access.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate that local mining can produce a safe manifest.")
    parser.add_argument("--json-output", help="Explicit path for generated candidate manifest JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated candidate summary Markdown.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output = stdout or sys.stdout

    if args.list_inputs:
        for path in list_input_paths(root):
            output.write(f"{path}\n")
        return 0

    report = build_candidate_manifest(root)
    errors = validate_generated_manifest(report)

    if args.check:
        if errors:
            output.write("mine_local_eval_observation_candidates: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("mine_local_eval_observation_candidates: pass\n")
        output.write(f"candidate_count: {report['candidate_count']}\n")

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(report, indent=2, sort_keys=True) + "\n")

    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_summary(report))

    if not args.check and not args.json_output and not args.markdown_output:
        output.write(format_plain_summary(report))
    return 0 if not errors else 1


def list_input_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    policy = _load_json(repo_root / POLICY_PATH)
    allowed = _string_items(_mapping(policy).get("allowed_input_roots"))
    inputs: list[str] = []
    for relative_path in PRIMARY_INPUT_PATHS:
        path = repo_root / relative_path
        if path.exists() and _allowed_by_policy(relative_path, allowed):
            inputs.append(relative_path)
    return sorted(inputs)


def build_candidate_manifest(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    policy = _mapping(_load_json(root / POLICY_PATH))
    query_pack = _mapping(_load_json(root / QUERY_PACK_PATH))
    batch_manifest = _mapping(_load_json(root / BATCH_MANIFEST_PATH))
    pending_batch = _mapping(_load_json(root / PENDING_BATCH_PATH))
    slot_manifest = _mapping(_load_json(root / SLOT_MANIFEST_PATH))
    eval_summary = _mapping(_load_json(root / EVAL_SUMMARY_PATH))
    demo_snapshots = _mapping(_load_json(root / DEMO_SNAPSHOTS_PATH))

    queries = {
        str(item.get("id")): _mapping(item)
        for item in _sequence_items(query_pack.get("queries"))
        if isinstance(item, Mapping) and item.get("id")
    }
    selected_query_ids = _string_items(batch_manifest.get("selected_query_ids"))
    pending_observations = _sequence_items(pending_batch.get("observations"))
    pending_count = sum(1 for item in pending_observations if _mapping(item).get("observation_status") == "pending_manual_observation")
    observed_count = sum(1 for item in pending_observations if _mapping(item).get("observation_status") == "observed")

    search_summary = _mapping(eval_summary.get("search_usefulness"))
    eval_failure_counts = {
        key: value
        for key, value in sorted(_mapping(search_summary.get("failure_mode_counts")).items())
        if isinstance(key, str) and isinstance(value, int)
    }
    status_counts = {
        key: value
        for key, value in sorted(_mapping(search_summary.get("status_counts")).items())
        if isinstance(key, str) and isinstance(value, int)
    }

    records = _candidate_records(
        queries=queries,
        selected_query_ids=selected_query_ids,
        pending_count=pending_count,
        observed_count=observed_count,
    )
    candidate_status_counts = Counter(str(record["candidate_status"]) for record in records)
    candidate_failure_counts = Counter(
        mode
        for record in records
        for mode in _string_items(record.get("proposed_failure_modes"))
    )

    inspected_inputs = list_input_paths(root)
    inspected_roots = _inspected_roots(inspected_inputs, _string_items(policy.get("allowed_input_roots")))
    skipped_roots = _skipped_roots(_string_items(policy.get("allowed_input_roots")), inspected_roots)
    notes = [
        "Generated from committed repo-local materials only.",
        "Manual external baseline slots remain pending.",
        "No live source access, browser use, API calls, scraping, crawling, downloads, model calls, or provider calls were performed.",
        "Track B local task packet was observed at TRACK-B-06; queue/context mutation is deferred to avoid overwriting parallel Track B state.",
    ]
    if not records:
        notes.append("insufficient_local_evidence")

    return {
        "schema_version": "obs_agent_candidate_batch_local_eval_manifest.v0",
        "manifest_id": "obs_agent_candidate_batch_0_local_eval_manifest_v0",
        "label": "OBS agent candidate batch 0 local eval manifest",
        "description": "Deterministic repo-local candidate manifest for OBS-AGENT-01 local eval failure mining.",
        "batch_id": "obs_agent_local_eval_failure_mining_batch_0",
        "source_policy": POLICY_PATH,
        "candidate_count": len(records),
        "candidate_records": records,
        "status_counts": dict(sorted(candidate_status_counts.items())),
        "failure_mode_counts": dict(sorted(candidate_failure_counts.items())),
        "local_eval_failure_mode_counts": eval_failure_counts,
        "local_eval_status_counts": status_counts,
        "source_roots_inspected": inspected_roots,
        "source_roots_skipped": skipped_roots,
        "input_files": inspected_inputs,
        "manual_batch_0": {
            "selected_query_count": len(selected_query_ids),
            "pending_observation_count": pending_count,
            "observed_observation_count": observed_count,
            "slot_manifest_status_counts": _mapping(slot_manifest.get("status_counts")),
        },
        "static_demo_summary": {
            "demo_count": demo_snapshots.get("demo_count"),
            "contains_live_data": demo_snapshots.get("contains_live_data"),
            "contains_live_probes": demo_snapshots.get("contains_live_probes"),
        },
        "review_required": True,
        "truth_boundary": {
            "candidates_are_observed_baselines": False,
            "candidates_are_evidence_truth": False,
            "candidates_can_mutate_master_index": False,
            "human_review_required": True,
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "notes": notes,
    }


def validate_generated_manifest(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    records = _sequence_items(manifest.get("candidate_records"))
    if manifest.get("candidate_count") != len(records):
        errors.append("candidate_count must match candidate_records length")
    if manifest.get("review_required") is not True:
        errors.append("review_required must be true")
    for field, value in _mapping(manifest.get("truth_boundary")).items():
        if field == "human_review_required":
            if value is not True:
                errors.append("truth_boundary.human_review_required must be true")
        elif value is not False:
            errors.append(f"truth_boundary.{field} must be false")
    for field, value in _mapping(manifest.get("product_boundary")).items():
        if value is not False:
            errors.append(f"product_boundary.{field} must be false")
    for record in records:
        item = _mapping(record)
        candidate_id = item.get("observation_candidate_id", "<missing>")
        if item.get("requires_human_review") is not True:
            errors.append(f"{candidate_id}: requires_human_review must be true")
        for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
            if item.get(field) is not False:
                errors.append(f"{candidate_id}: {field} must be false")
        if item.get("source_access_mode") not in {"repo_local_only", "no_autonomous_access"}:
            errors.append(f"{candidate_id}: source_access_mode must remain repo_local_only or no_autonomous_access")
    return sorted(set(errors))


def format_plain_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "mine_local_eval_observation_candidates:",
        f"- candidate_count: {manifest.get('candidate_count')}",
        f"- status_counts: {json.dumps(manifest.get('status_counts', {}), sort_keys=True)}",
        f"- failure_mode_counts: {json.dumps(manifest.get('failure_mode_counts', {}), sort_keys=True)}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# Local Eval Candidate Summary",
        "",
        "OBS-AGENT-01 generated review-gated candidates from committed repo-local materials only.",
        "",
        "## Inputs Inspected",
        "",
    ]
    lines.extend(f"- `{path}`" for path in _string_items(manifest.get("input_files")))
    lines.extend(
        [
            "",
            "## Candidate Records",
            "",
            "| Candidate | Type | Status | Source mode | Failure modes |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for record in _sequence_items(manifest.get("candidate_records")):
        item = _mapping(record)
        modes = ", ".join(_string_items(item.get("proposed_failure_modes")))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                item.get("observation_candidate_id"),
                item.get("candidate_type"),
                item.get("candidate_status"),
                item.get("source_access_mode"),
                modes,
            )
        )
    lines.extend(
        [
            "",
            "## Uncertain",
            "",
            "- Ranking gaps are local audit labels, not externally observed ranks.",
            "- Manual external baseline slots remain pending until a human records observations.",
            "- Source leads and WorkUnit seeds remain future review targets.",
            "",
            "## Human Review Required",
            "",
            "- Reviewers may approve, reject, tune, deduplicate, or defer candidates.",
            "- Review does not turn candidates into observed baselines or evidence truth.",
            "- Track B should consume these records only after matching contracts and review gates exist.",
            "",
            "## Future Seeds",
            "",
            "- SearchNeed seed candidates: `obs_candidate_local_eval_ranking_gap_v0`.",
            "- WorkUnit seed candidates: `obs_candidate_local_eval_extraction_gap_v0` and source-policy review for `obs_candidate_local_eval_policy_blocked_v0`.",
            "- Source gap candidates may later become source leads after human review.",
            "",
            "## Source Policy Blocks",
            "",
            "- `obs_candidate_local_eval_policy_blocked_v0` remains blocked for autonomous agent access.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidate_records(
    *,
    queries: Mapping[str, Mapping[str, Any]],
    selected_query_ids: Sequence[str],
    pending_count: int,
    observed_count: int,
) -> list[dict[str, Any]]:
    selected = set(selected_query_ids)
    source_query = _query_or_empty(queries, "windows_7_apps")
    extraction_query = _query_or_empty(queries, "driver_inf_inside_support_cd")
    ranking_query = _query_or_empty(queries, "pc_magazine_july_1994_ray_tracing")

    records = [
        {
            "observation_candidate_id": "obs_candidate_local_eval_failure_mining_batch_0_v0",
            "candidate_type": "local_eval_failure",
            "candidate_status": "needs_human_review",
            "origin": "local_eval",
            "related_batch_id": "batch_0",
            "related_query_id": None,
            "related_slot_id": None,
            "source_access_mode": "repo_local_only",
            "proposed_failure_modes": [
                "source_coverage_gap",
                "compatibility_evidence_gap",
                "planner_gap",
                "representation_gap",
                "member_access_gap",
                "ranking_gap",
            ],
            "candidate_file_path": CANDIDATE_FILES["obs_candidate_local_eval_failure_mining_batch_0_v0"],
            "requires_human_review": True,
            "accepted_as_observed_baseline": False,
            "accepted_as_evidence_truth": False,
            "master_index_mutation_allowed": False,
            "notes": [
                f"batch_0_pending_observation_count={pending_count}",
                f"batch_0_observed_observation_count={observed_count}",
            ],
        },
        _candidate_record(
            candidate_id="obs_candidate_local_eval_source_gap_v0",
            candidate_type="source_lead",
            candidate_status="proposed",
            origin="search_usefulness_audit",
            related_batch_id="batch_0",
            query_id="windows_7_apps",
            query=source_query,
            modes=["source_coverage_gap", "compatibility_evidence_gap", "ranking_gap"],
            source_access_mode="repo_local_only",
            notes=["Selected query is in Batch 0." if "windows_7_apps" in selected else "Selected query not present in Batch 0."],
        ),
        _candidate_record(
            candidate_id="obs_candidate_local_eval_extraction_gap_v0",
            candidate_type="work_unit_seed",
            candidate_status="proposed",
            origin="local_eval",
            related_batch_id="batch_0",
            query_id="driver_inf_inside_support_cd",
            query=extraction_query,
            modes=["decomposition_gap", "member_access_gap", "extraction_gap", "source_coverage_gap"],
            source_access_mode="repo_local_only",
            notes=["Candidate is limited to local support-media member query classes."],
        ),
        _candidate_record(
            candidate_id="obs_candidate_local_eval_ranking_gap_v0",
            candidate_type="search_need_seed",
            candidate_status="proposed",
            origin="search_usefulness_audit",
            related_batch_id="batch_0",
            query_id="pc_magazine_july_1994_ray_tracing",
            query=ranking_query,
            modes=["source_coverage_gap", "member_access_gap", "ranking_gap"],
            source_access_mode="repo_local_only",
            notes=["Ranking weakness is inferred only from committed local audit labels."],
        ),
        {
            "observation_candidate_id": "obs_candidate_local_eval_policy_blocked_v0",
            "candidate_type": "policy_blocked_candidate",
            "candidate_status": "policy_blocked",
            "origin": "search_usefulness_audit",
            "related_batch_id": "batch_0",
            "related_query_id": "windows_7_apps",
            "related_slot_id": None,
            "source_access_mode": "no_autonomous_access",
            "proposed_failure_modes": [
                "rights_or_policy_block",
                "external_baseline_unavailable",
            ],
            "candidate_file_path": CANDIDATE_FILES["obs_candidate_local_eval_policy_blocked_v0"],
            "requires_human_review": True,
            "accepted_as_observed_baseline": False,
            "accepted_as_evidence_truth": False,
            "master_index_mutation_allowed": False,
            "notes": [
                "Google web search remains blocked for autonomous agent access in this lane.",
                "No source result was collected.",
            ],
        },
    ]
    return sorted(records, key=lambda item: str(item["observation_candidate_id"]))


def _candidate_record(
    *,
    candidate_id: str,
    candidate_type: str,
    candidate_status: str,
    origin: str,
    related_batch_id: str,
    query_id: str,
    query: Mapping[str, Any],
    modes: Sequence[str],
    source_access_mode: str,
    notes: Sequence[str],
) -> dict[str, Any]:
    return {
        "observation_candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "candidate_status": candidate_status,
        "origin": origin,
        "related_batch_id": related_batch_id,
        "related_query_id": query_id,
        "related_slot_id": None,
        "source_access_mode": source_access_mode,
        "proposed_failure_modes": list(modes),
        "candidate_file_path": CANDIDATE_FILES[candidate_id],
        "requires_human_review": True,
        "accepted_as_observed_baseline": False,
        "accepted_as_evidence_truth": False,
        "master_index_mutation_allowed": False,
        "notes": [
            f"query_text={query.get('query', 'insufficient_local_evidence')}",
            *notes,
        ],
    }


def _query_or_empty(queries: Mapping[str, Mapping[str, Any]], query_id: str) -> Mapping[str, Any]:
    return queries.get(query_id, {"query": "insufficient_local_evidence", "expected_failure_modes": ["insufficient_local_evidence"]})


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
