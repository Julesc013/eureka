"""Build deterministic WorkUnit seed draft manifests from repo-local OBS inputs.

The builder is local-only. It reads committed WorkUnit seed examples, OBS review
queue material, and SearchNeed seed drafts, then emits non-executable WorkUnit
seed manifest records. Files are written only when explicit output paths are
supplied.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

SEED_CONTRACT_PATH = "contracts/query/workunit_seed.v0.json"
CONVERSION_CONTRACT_PATH = "contracts/query/workunit_seed_conversion.v0.json"
POLICY_PATH = "control/inventory/observations/workunit_seed_conversion_policy.json"
PRIORITY_MODEL_PATH = "control/inventory/observations/workunit_seed_priority_model.json"
REVIEW_QUEUE_PATH = "control/inventory/observations/observation_candidate_review_queue.json"
SEARCH_NEED_MANIFEST_PATH = "control/inventory/observations/search_need_seed_manifest.json"
OBS01_MANIFEST_PATH = "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json"
OBS02_MANIFEST_PATH = "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json"
OBS04_AUDIT_MANIFEST_PATH = "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/search_need_seed_manifest.json"
TRACK_B_WORKUNIT_CONTRACT_PATH = "contracts/node/work_unit.v0.json"
TRACK_B_WORKUNIT_RESULT_CONTRACT_PATH = "contracts/node/work_unit_result.v0.json"

WORKUNIT_SEED_EXAMPLES = (
    "examples/workunit_seeds/minimal_workunit_seed_v0.json",
    "examples/workunit_seeds/source_policy_review_workunit_seed_v0.json",
    "examples/workunit_seeds/metadata_probe_planning_workunit_seed_v0.json",
    "examples/workunit_seeds/extraction_gap_workunit_seed_v0.json",
    "examples/workunit_seeds/compatibility_review_workunit_seed_v0.json",
    "examples/workunit_seeds/policy_blocked_workunit_seed_v0.json",
)

WORKUNIT_CONVERSION_EXAMPLES = (
    "examples/workunit_seed_conversions/minimal_candidate_to_workunit_conversion_v0.json",
    "examples/workunit_seed_conversions/search_need_seed_to_workunit_conversion_v0.json",
    "examples/workunit_seed_conversions/source_gap_candidate_to_workunit_conversion_v0.json",
    "examples/workunit_seed_conversions/request_more_evidence_workunit_conversion_v0.json",
)

PRIMARY_INPUT_PATHS = (
    SEED_CONTRACT_PATH,
    CONVERSION_CONTRACT_PATH,
    POLICY_PATH,
    PRIORITY_MODEL_PATH,
    REVIEW_QUEUE_PATH,
    SEARCH_NEED_MANIFEST_PATH,
    OBS01_MANIFEST_PATH,
    OBS02_MANIFEST_PATH,
    OBS04_AUDIT_MANIFEST_PATH,
    TRACK_B_WORKUNIT_CONTRACT_PATH,
    TRACK_B_WORKUNIT_RESULT_CONTRACT_PATH,
    *WORKUNIT_SEED_EXAMPLES,
    *WORKUNIT_CONVERSION_EXAMPLES,
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
    "executed_workunits": False,
    "modified_track_b_files": False,
    "accepted_runtime_workunit": False,
}

PRIORITY_BAND_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "blocked": 3,
    "insufficient_local_evidence": 4,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build WorkUnit seed draft candidates without external access.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate that the WorkUnit seed manifest can be safely built.")
    parser.add_argument("--json-output", help="Explicit path for generated WorkUnit seed manifest JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated WorkUnit seed summary Markdown.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output = stdout or sys.stdout

    if args.list_inputs:
        for path in list_input_paths(root):
            output.write(f"{path}\n")
        return 0

    manifest = build_seed_manifest(root)
    errors = validate_built_manifest(manifest)

    if args.check:
        if errors:
            output.write("build_workunit_seed_candidates: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("build_workunit_seed_candidates: pass\n")
        output.write(f"seed_count: {manifest['seed_count']}\n")

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_summary(manifest))

    if not args.check and not args.json_output and not args.markdown_output:
        output.write(format_plain_summary(manifest))
    return 0 if not errors else 1


def list_input_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    return sorted(path for path in PRIMARY_INPUT_PATHS if (repo_root / path).exists())


def build_seed_manifest(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    seeds = _load_seed_examples(root)
    seed_records = [_manifest_record(path, seed) for path, seed in seeds]
    seed_records = sorted(
        seed_records,
        key=lambda item: (
            PRIORITY_BAND_RANK.get(str(_priority_band(item.get("proposed_priority"))), 99),
            -int(_priority_score(item.get("proposed_priority"))),
            str(item.get("workunit_seed_id")),
        ),
    )

    status_counts = Counter(str(item.get("seed_status")) for item in seed_records)
    type_counts = Counter(str(item.get("seed_type")) for item in seed_records)
    band_counts = Counter(str(_priority_band(item.get("proposed_priority"))) for item in seed_records)
    related_candidate_counts = Counter(
        candidate_id
        for item in seed_records
        for candidate_id in _string_items(item.get("related_observation_candidate_ids"))
    )
    related_search_need_counts = Counter(
        seed_id
        for item in seed_records
        for seed_id in _string_items(item.get("related_search_need_seed_ids"))
    )
    scores = [_priority_score(item.get("proposed_priority")) for item in seed_records]

    return {
        "schema_version": "workunit_seed_manifest.v0",
        "manifest_id": "workunit_seed_manifest_v0",
        "label": "WorkUnit seed draft manifest",
        "description": "Review-gated non-executable WorkUnit seed records generated from repo-local OBS candidates, review queue entries, and SearchNeed seed drafts.",
        "generated_from": list_input_paths(root),
        "seed_count": len(seed_records),
        "seed_records": seed_records,
        "seed_status_counts": dict(sorted(status_counts.items())),
        "seed_type_counts": dict(sorted(type_counts.items())),
        "priority_band_counts": dict(sorted(band_counts.items())),
        "related_candidate_counts": dict(sorted(related_candidate_counts.items())),
        "related_search_need_seed_counts": dict(sorted(related_search_need_counts.items())),
        "review_required": True,
        "downstream_track_b_dependency": [
            "Track B WorkUnit runtime contract required before activation.",
            "Human review decision required before downstream use.",
            "Source policy decisions remain separate from WorkUnit seed review.",
            "Node capability and local state requirements remain future/deferred."
        ],
        "truth_boundary": {
            "seeds_are_executable_workunits": False,
            "seeds_are_runtime_workunits": False,
            "seeds_are_observed_baselines": False,
            "seeds_are_evidence_truth": False,
            "seeds_can_mutate_master_index": False,
            "human_review_required": True,
            "source_access_approved": False
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "priority_score_summary": _score_summary(scores),
        "notes": [
            "WorkUnit seeds are draft task proposals only.",
            "No runtime WorkUnit, WorkUnit execution, source approval, observed baseline, evidence truth, or master-index mutation is created.",
            "Track B local task packet was observed at TRACK-B-06; queue/context mutation is deferred to avoid overwriting parallel Track B state."
        ]
    }


def validate_built_manifest(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    records = [_mapping(item) for item in _sequence_items(manifest.get("seed_records"))]
    if manifest.get("schema_version") != "workunit_seed_manifest.v0":
        errors.append("schema_version must be workunit_seed_manifest.v0")
    if manifest.get("seed_count") != len(records):
        errors.append("seed_count must match seed_records")
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
        errors.extend(validate_built_record(record))
    return sorted(set(errors))


def validate_built_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    seed_id = str(record.get("workunit_seed_id", "<missing>"))
    for field in (
        "workunit_seed_id",
        "seed_status",
        "seed_type",
        "related_observation_candidate_ids",
        "related_review_queue_entry_ids",
        "related_search_need_seed_ids",
        "related_query_ids",
        "proposed_workunit_label",
        "proposed_priority",
        "proposed_review_action",
        "seed_file_path",
        "review_required",
        "execution_allowed_now",
        "accepted_as_runtime_workunit",
        "accepted_as_observed_baseline",
        "accepted_as_evidence_truth",
        "master_index_mutation_allowed",
        "notes",
    ):
        if field not in record:
            errors.append(f"{seed_id}: missing {field}")
    if record.get("review_required") is not True:
        errors.append(f"{seed_id}: review_required must be true")
    for field in ("execution_allowed_now", "accepted_as_runtime_workunit", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if record.get(field) is not False:
            errors.append(f"{seed_id}: {field} must be false")
    score = _priority_score(record.get("proposed_priority"))
    if score < 0 or score > 100:
        errors.append(f"{seed_id}: proposed_priority.score must be 0..100")
    return errors


def format_plain_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "build_workunit_seed_candidates:",
        f"- seed_count: {manifest.get('seed_count')}",
        f"- seed_status_counts: {json.dumps(manifest.get('seed_status_counts', {}), sort_keys=True)}",
        f"- seed_type_counts: {json.dumps(manifest.get('seed_type_counts', {}), sort_keys=True)}",
        f"- priority_band_counts: {json.dumps(manifest.get('priority_band_counts', {}), sort_keys=True)}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_summary(manifest: Mapping[str, Any]) -> str:
    records = [_mapping(record) for record in _sequence_items(manifest.get("seed_records"))]
    lines = [
        "# WorkUnit Seed Draft Summary",
        "",
        "This summary is generated from repo-local WorkUnit seed examples, SearchNeed seed drafts, and review queue metadata. It does not create executable WorkUnits.",
        "",
        f"Proposed WorkUnit seed drafts: {manifest.get('seed_count')}",
        "",
        "## Seed Drafts",
        "",
        "| Priority | Seed | Type | Status | Review action | Source family |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        priority = _mapping(record.get("proposed_priority"))
        lines.append(
            "| {} {} | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                priority.get("band"),
                priority.get("score"),
                record.get("workunit_seed_id"),
                record.get("seed_type"),
                record.get("seed_status"),
                record.get("proposed_review_action"),
                record.get("source_family"),
            )
        )

    high_priority = [record for record in records if _priority_band(record.get("proposed_priority")) == "high"]
    source_policy = [record for record in records if record.get("seed_type") == "source_policy_review"]
    metadata_probe = [record for record in records if record.get("seed_type") == "approved_metadata_probe_planning_future"]
    extraction_gap = [record for record in records if record.get("seed_type") == "container_deepening_planning_future"]
    compatibility_review = [record for record in records if record.get("seed_type") == "compatibility_evidence_review"]
    policy_blocked = [
        record for record in records
        if record.get("seed_status") == "policy_blocked"
        or _priority_band(record.get("proposed_priority")) == "blocked"
    ]

    lines.extend(["", "## High-Priority WorkUnit Seed Drafts", ""])
    lines.extend(_seed_lines(high_priority) or ["- None."])
    lines.extend(["", "## Source-Policy Review WorkUnit Seed Drafts", ""])
    lines.extend(_seed_lines(source_policy) or ["- None."])
    lines.extend(["", "## Metadata-Probe Planning WorkUnit Seed Drafts", ""])
    lines.extend(_seed_lines(metadata_probe) or ["- None."])
    lines.extend(["", "## Extraction-Gap WorkUnit Seed Drafts", ""])
    lines.extend(_seed_lines(extraction_gap) or ["- None."])
    lines.extend(["", "## Compatibility-Review WorkUnit Seed Drafts", ""])
    lines.extend(_seed_lines(compatibility_review) or ["- None."])
    lines.extend(["", "## Policy-Blocked WorkUnit Seed Drafts", ""])
    lines.extend(_seed_lines(policy_blocked) or ["- None."])
    lines.extend(
        [
            "",
            "## Review Boundary",
            "",
            "- Approving a WorkUnit seed does not execute it.",
            "- Approving a WorkUnit seed does not make it an observed baseline.",
            "- Approving a WorkUnit seed does not make it accepted evidence.",
            "- Approving a WorkUnit seed does not create a runtime WorkUnit until Track B accepts it.",
            "- Approving a WorkUnit seed does not mutate the master index.",
            "- Approving a WorkUnit seed does not approve live source access.",
            "",
            "## Track B Dependencies",
            "",
            "- Track B must define and accept runtime WorkUnit semantics before any seed can become executable work.",
            "- Source policy review remains separate from WorkUnit seed review.",
            "- Node capability, local state, idempotency, and recovery semantics remain future/deferred.",
            "",
            "## Human Review Needs",
            "",
            "- Confirm each proposed work label, scope, allowed action, and forbidden action.",
            "- Tune or deduplicate seeds before any downstream Track B handoff.",
            "- Keep policy-blocked and needs-more-evidence seeds out of executable flows.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_seed_examples(repo_root: Path) -> list[tuple[str, Mapping[str, Any]]]:
    records: list[tuple[str, Mapping[str, Any]]] = []
    seen: set[str] = set()
    for path in WORKUNIT_SEED_EXAMPLES:
        payload = _mapping(_load_json(repo_root / path))
        seed_id = payload.get("workunit_seed_id")
        if not isinstance(seed_id, str) or seed_id in seen:
            continue
        seen.add(seed_id)
        records.append((path, payload))
    return sorted(records, key=lambda item: str(item[1].get("workunit_seed_id")))


def _manifest_record(path: str, seed: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "workunit_seed_id": seed.get("workunit_seed_id"),
        "seed_status": seed.get("seed_status"),
        "seed_type": seed.get("seed_type"),
        "related_observation_candidate_ids": _string_items(seed.get("related_observation_candidate_ids")),
        "related_review_queue_entry_ids": _string_items(seed.get("related_review_queue_entry_ids")),
        "related_search_need_seed_ids": _string_items(seed.get("related_search_need_seed_ids")),
        "related_query_ids": _string_items(seed.get("related_query_ids")),
        "proposed_workunit_label": seed.get("proposed_workunit_label"),
        "proposed_workunit_type": seed.get("proposed_workunit_type"),
        "source_family": seed.get("source_family"),
        "source_access_mode": seed.get("source_access_mode"),
        "source_policy_status": seed.get("source_policy_status"),
        "failure_mode_summary": _string_items(seed.get("failure_mode_summary")),
        "proposed_priority": dict(_mapping(seed.get("proposed_priority"))),
        "proposed_review_action": seed.get("proposed_review_action"),
        "seed_file_path": path,
        "review_required": True,
        "execution_allowed_now": False,
        "accepted_as_runtime_workunit": False,
        "accepted_as_observed_baseline": False,
        "accepted_as_evidence_truth": False,
        "master_index_mutation_allowed": False,
        "notes": [
            "Manifest record references a non-executable draft WorkUnit seed file.",
            "Human review is required before downstream use."
        ],
    }


def _seed_lines(records: Sequence[Mapping[str, Any]]) -> list[str]:
    return [
        "- `{}`: `{}` ({})".format(
            record.get("workunit_seed_id"),
            record.get("seed_type"),
            record.get("proposed_workunit_label"),
        )
        for record in records
    ]


def _score_summary(scores: Sequence[int]) -> dict[str, Any]:
    if not scores:
        return {"min": 0, "max": 0, "average": 0}
    return {
        "min": min(scores),
        "max": max(scores),
        "average": round(sum(scores) / len(scores), 2),
    }


def _priority_score(priority: Any) -> int:
    value = _mapping(priority).get("score")
    return int(value) if isinstance(value, int) else 0


def _priority_band(priority: Any) -> str:
    value = _mapping(priority).get("band")
    return str(value) if isinstance(value, str) else "insufficient_local_evidence"


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
