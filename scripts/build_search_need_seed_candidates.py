"""Build deterministic SearchNeed seed draft manifests from repo-local OBS inputs.

The builder is local-only. It reads committed review queue and seed examples,
emits draft SearchNeed seed manifest records, and writes output only when
explicit output paths are supplied.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

SEED_CONTRACT_PATH = "contracts/query/search_need_seed.v0.json"
CONVERSION_CONTRACT_PATH = "contracts/query/search_need_seed_conversion.v0.json"
POLICY_PATH = "control/inventory/observations/search_need_seed_conversion_policy.json"
PRIORITY_MODEL_PATH = "control/inventory/observations/search_need_seed_priority_model.json"
REVIEW_QUEUE_PATH = "control/inventory/observations/observation_candidate_review_queue.json"
OBS01_MANIFEST_PATH = "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json"
OBS02_MANIFEST_PATH = "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json"
OBS03_AUDIT_QUEUE_PATH = "control/audits/obs-agent-03-observation-candidate-review-queue-v0/observation_candidate_review_queue.json"

SEARCH_NEED_SEED_EXAMPLES = (
    "examples/search_need_seeds/minimal_search_need_seed_v0.json",
    "examples/search_need_seeds/source_gap_search_need_seed_v0.json",
    "examples/search_need_seeds/extraction_gap_search_need_seed_v0.json",
    "examples/search_need_seeds/compatibility_gap_search_need_seed_v0.json",
    "examples/search_need_seeds/policy_blocked_search_need_seed_v0.json",
)

SEARCH_NEED_CONVERSION_EXAMPLES = (
    "examples/search_need_seed_conversions/minimal_candidate_to_need_conversion_v0.json",
    "examples/search_need_seed_conversions/source_gap_candidate_to_need_conversion_v0.json",
    "examples/search_need_seed_conversions/request_more_evidence_conversion_v0.json",
)

PRIMARY_INPUT_PATHS = (
    SEED_CONTRACT_PATH,
    CONVERSION_CONTRACT_PATH,
    POLICY_PATH,
    PRIORITY_MODEL_PATH,
    REVIEW_QUEUE_PATH,
    OBS01_MANIFEST_PATH,
    OBS02_MANIFEST_PATH,
    OBS03_AUDIT_QUEUE_PATH,
    *SEARCH_NEED_SEED_EXAMPLES,
    *SEARCH_NEED_CONVERSION_EXAMPLES,
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
    "accepted_runtime_search_need": False,
}

PRIORITY_BAND_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "blocked": 3,
    "insufficient_local_evidence": 4,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build SearchNeed seed draft candidates without external access.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate that the seed manifest can be safely built.")
    parser.add_argument("--json-output", help="Explicit path for generated seed manifest JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated seed summary Markdown.")
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
            output.write("build_search_need_seed_candidates: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("build_search_need_seed_candidates: pass\n")
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
            str(item.get("search_need_seed_id")),
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
    scores = [_priority_score(item.get("proposed_priority")) for item in seed_records]

    return {
        "schema_version": "search_need_seed_manifest.v0",
        "manifest_id": "search_need_seed_manifest_v0",
        "label": "SearchNeed seed draft manifest",
        "description": "Review-gated draft SearchNeed seed records generated from repo-local OBS candidate and review queue artifacts.",
        "generated_from": list_input_paths(root),
        "seed_count": len(seed_records),
        "seed_records": seed_records,
        "seed_status_counts": dict(sorted(status_counts.items())),
        "seed_type_counts": dict(sorted(type_counts.items())),
        "priority_band_counts": dict(sorted(band_counts.items())),
        "related_candidate_counts": dict(sorted(related_candidate_counts.items())),
        "review_required": True,
        "downstream_track_b_dependency": [
            "Track B SearchNeed runtime contract required before activation.",
            "Human review decision required before downstream use.",
            "Source policy decisions remain separate from seed review."
        ],
        "truth_boundary": {
            "seeds_are_runtime_search_needs": False,
            "seeds_are_observed_baselines": False,
            "seeds_are_evidence_truth": False,
            "seeds_can_mutate_master_index": False,
            "human_review_required": True,
            "source_access_approved": False
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "priority_score_summary": _score_summary(scores),
        "notes": [
            "Seeds are draft inputs only.",
            "No runtime SearchNeed, source approval, observed baseline, evidence truth, or master-index mutation is created.",
            "Track B local task packet was observed at TRACK-B-06; queue/context mutation is deferred to avoid overwriting parallel Track B state."
        ]
    }


def validate_built_manifest(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    records = [_mapping(item) for item in _sequence_items(manifest.get("seed_records"))]
    if manifest.get("schema_version") != "search_need_seed_manifest.v0":
        errors.append("schema_version must be search_need_seed_manifest.v0")
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
    seed_id = str(record.get("search_need_seed_id", "<missing>"))
    for field in (
        "search_need_seed_id",
        "seed_status",
        "seed_type",
        "related_observation_candidate_ids",
        "related_review_queue_entry_ids",
        "related_query_ids",
        "canonical_need_label",
        "proposed_priority",
        "proposed_review_action",
        "seed_file_path",
        "review_required",
        "accepted_as_runtime_search_need",
        "accepted_as_observed_baseline",
        "accepted_as_evidence_truth",
        "master_index_mutation_allowed",
        "notes",
    ):
        if field not in record:
            errors.append(f"{seed_id}: missing {field}")
    if record.get("review_required") is not True:
        errors.append(f"{seed_id}: review_required must be true")
    for field in ("accepted_as_runtime_search_need", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if record.get(field) is not False:
            errors.append(f"{seed_id}: {field} must be false")
    score = _priority_score(record.get("proposed_priority"))
    if score < 0 or score > 100:
        errors.append(f"{seed_id}: proposed_priority.score must be 0..100")
    return errors


def format_plain_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "build_search_need_seed_candidates:",
        f"- seed_count: {manifest.get('seed_count')}",
        f"- seed_status_counts: {json.dumps(manifest.get('seed_status_counts', {}), sort_keys=True)}",
        f"- seed_type_counts: {json.dumps(manifest.get('seed_type_counts', {}), sort_keys=True)}",
        f"- priority_band_counts: {json.dumps(manifest.get('priority_band_counts', {}), sort_keys=True)}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_summary(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# SearchNeed Seed Draft Summary",
        "",
        "This summary is generated from repo-local seed examples and review queue metadata. It does not create runtime SearchNeeds.",
        "",
        f"Proposed seed drafts: {manifest.get('seed_count')}",
        "",
        "## Seed Drafts",
        "",
        "| Priority | Seed | Type | Status | Review action | Source family |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in _sequence_items(manifest.get("seed_records")):
        item = _mapping(record)
        priority = _mapping(item.get("proposed_priority"))
        lines.append(
            "| {} {} | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                priority.get("band"),
                priority.get("score"),
                item.get("search_need_seed_id"),
                item.get("seed_type"),
                item.get("seed_status"),
                item.get("proposed_review_action"),
                item.get("source_family"),
            )
        )
    high_priority = [
        _mapping(record) for record in _sequence_items(manifest.get("seed_records"))
        if _priority_band(_mapping(record).get("proposed_priority")) == "high"
    ]
    policy_blocked = [
        _mapping(record) for record in _sequence_items(manifest.get("seed_records"))
        if _mapping(record).get("seed_status") == "policy_blocked"
        or _priority_band(_mapping(record).get("proposed_priority")) == "blocked"
    ]
    source_gap = [
        _mapping(record) for record in _sequence_items(manifest.get("seed_records"))
        if _mapping(record).get("seed_type") == "source_gap_need_seed"
    ]
    extraction_gap = [
        _mapping(record) for record in _sequence_items(manifest.get("seed_records"))
        if _mapping(record).get("seed_type") == "extraction_gap_need_seed"
    ]
    compatibility_gap = [
        _mapping(record) for record in _sequence_items(manifest.get("seed_records"))
        if _mapping(record).get("seed_type") == "compatibility_gap_need_seed"
    ]
    lines.extend(["", "## High-Priority Seed Drafts", ""])
    lines.extend(_seed_lines(high_priority) or ["- None."])
    lines.extend(["", "## Policy-Blocked Seed Drafts", ""])
    lines.extend(_seed_lines(policy_blocked) or ["- None."])
    lines.extend(["", "## Duplicate Or Ambiguous Seed Drafts", ""])
    lines.append("- No duplicate seed is asserted by this generated manifest; compatibility and manual-observation seeds still require human review for ambiguity.")
    lines.extend(["", "## Source-Gap-Derived Seed Drafts", ""])
    lines.extend(_seed_lines(source_gap) or ["- None."])
    lines.extend(["", "## Extraction-Gap-Derived Seed Drafts", ""])
    lines.extend(_seed_lines(extraction_gap) or ["- None."])
    lines.extend(["", "## Compatibility-Gap-Derived Seed Drafts", ""])
    lines.extend(_seed_lines(compatibility_gap) or ["- None."])
    lines.extend(
        [
            "",
            "## Review Boundary",
            "",
            "- Approving a seed does not make it an observed baseline.",
            "- Approving a seed does not make it accepted evidence.",
            "- Approving a seed does not create a runtime SearchNeed until Track B runtime accepts it.",
            "- Approving a seed does not mutate the master index.",
            "- Approving a seed does not approve live source access.",
            "",
            "## Track B Dependency",
            "",
            "- Track B must define and accept runtime SearchNeed semantics before any seed can become runtime state.",
            "- Source policy review remains separate from SearchNeed seed review.",
            "",
            "## Human Review Needs",
            "",
            "- Confirm whether each draft describes a useful future SearchNeed.",
            "- Tune labels and aliases before any downstream Track B handoff.",
            "- Keep policy-blocked and needs-more-evidence seeds out of runtime flows.",
            "",
        ]
    )
    return "\n".join(lines)


def _seed_lines(records: Sequence[Mapping[str, Any]]) -> list[str]:
    return [
        "- `{}`: `{}` ({})".format(
            record.get("search_need_seed_id"),
            record.get("seed_type"),
            record.get("canonical_need_label"),
        )
        for record in records
    ]


def _load_seed_examples(repo_root: Path) -> list[tuple[str, Mapping[str, Any]]]:
    records: list[tuple[str, Mapping[str, Any]]] = []
    seen: set[str] = set()
    for path in SEARCH_NEED_SEED_EXAMPLES:
        payload = _mapping(_load_json(repo_root / path))
        seed_id = payload.get("search_need_seed_id")
        if not isinstance(seed_id, str) or seed_id in seen:
            continue
        seen.add(seed_id)
        records.append((path, payload))
    return sorted(records, key=lambda item: str(item[1].get("search_need_seed_id")))


def _manifest_record(path: str, seed: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "search_need_seed_id": seed.get("search_need_seed_id"),
        "seed_status": seed.get("seed_status"),
        "seed_type": seed.get("seed_type"),
        "related_observation_candidate_ids": _string_items(seed.get("related_observation_candidate_ids")),
        "related_review_queue_entry_ids": _string_items(seed.get("related_review_queue_entry_ids")),
        "related_query_ids": _string_items(seed.get("related_query_ids")),
        "canonical_need_label": seed.get("canonical_need_label"),
        "source_family": seed.get("source_family"),
        "source_access_mode": seed.get("source_access_mode"),
        "source_policy_status": seed.get("source_policy_status"),
        "failure_mode_summary": _string_items(seed.get("failure_mode_summary")),
        "proposed_priority": dict(_mapping(seed.get("proposed_priority"))),
        "proposed_review_action": seed.get("proposed_review_action"),
        "seed_file_path": path,
        "review_required": True,
        "accepted_as_runtime_search_need": False,
        "accepted_as_observed_baseline": False,
        "accepted_as_evidence_truth": False,
        "master_index_mutation_allowed": False,
        "notes": [
            "Manifest record references a draft seed file.",
            "Human review is required before downstream use."
        ],
    }


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
