"""Build a deterministic review queue for ObservationCandidate records.

The builder is local-only. It reads committed candidate examples and OBS
manifests, emits queue entries for human review, and writes output only when
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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_observation_candidate import CANDIDATE_EXAMPLES  # noqa: E402


CONTRACT_PATH = "contracts/query/observation_candidate_review_queue.v0.json"
POLICY_PATH = "control/inventory/observations/observation_candidate_review_queue_policy.json"
TRIAGE_RULES_PATH = "control/inventory/observations/observation_candidate_triage_rules.json"
OBS01_MANIFEST_PATH = "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json"
OBS02_MANIFEST_PATH = "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json"
OBS01_AUDIT_MANIFEST_PATH = "control/audits/obs-agent-01-local-eval-failure-mining-v0/local_eval_candidate_manifest.json"
OBS02_AUDIT_MANIFEST_PATH = "control/audits/obs-agent-02-source-gap-candidate-generation-v0/source_gap_candidate_manifest.json"
SOURCE_ACCESS_MODES_PATH = "control/inventory/observations/observation_source_access_modes.json"

PRIMARY_INPUT_PATHS = (
    CONTRACT_PATH,
    POLICY_PATH,
    TRIAGE_RULES_PATH,
    OBS01_MANIFEST_PATH,
    OBS02_MANIFEST_PATH,
    OBS01_AUDIT_MANIFEST_PATH,
    OBS02_AUDIT_MANIFEST_PATH,
    SOURCE_ACCESS_MODES_PATH,
    *CANDIDATE_EXAMPLES,
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

PRIORITY_BAND_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "blocked": 3,
    "insufficient_local_evidence": 4,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an observation candidate review queue without external access.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate that the queue can be safely built.")
    parser.add_argument("--json-output", help="Explicit path for generated queue JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated queue Markdown.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output = stdout or sys.stdout

    if args.list_inputs:
        for path in list_input_paths(root):
            output.write(f"{path}\n")
        return 0

    queue = build_review_queue(root)
    errors = validate_built_queue(queue)

    if args.check:
        if errors:
            output.write("build_observation_candidate_review_queue: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("build_observation_candidate_review_queue: pass\n")
        output.write(f"queue_entry_count: {len(queue['queue_entries'])}\n")

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(queue, indent=2, sort_keys=True) + "\n")

    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_queue(queue))

    if not args.check and not args.json_output and not args.markdown_output:
        output.write(format_plain_summary(queue))
    return 0 if not errors else 1


def list_input_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    return sorted(path for path in PRIMARY_INPUT_PATHS if (repo_root / path).exists())


def build_review_queue(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    triage_rules = _mapping(_load_json(root / TRIAGE_RULES_PATH))
    manifest_index = _build_manifest_index(root)
    candidates = _load_candidate_examples(root)

    entries = [
        _entry_from_candidate(candidate, path, manifest_index.get(str(candidate.get("observation_candidate_id")), {}), triage_rules)
        for path, candidate in candidates
    ]
    entries = [entry for entry in entries if entry]
    entries = sorted(
        entries,
        key=lambda item: (
            PRIORITY_BAND_RANK.get(str(item["priority_band"]), 99),
            -int(item["priority_score"]),
            str(item["recommended_review_action"]),
            str(item["observation_candidate_id"]),
        ),
    )

    status_counts = Counter(str(item["proposed_review_state"]) for item in entries)
    action_counts = Counter(str(item["recommended_review_action"]) for item in entries)
    type_counts = Counter(str(item["candidate_type"]) for item in entries)
    family_counts = Counter(str(item["source_family"]) for item in entries)
    band_counts = Counter(str(item["priority_band"]) for item in entries)
    scores = [int(item["priority_score"]) for item in entries]
    input_paths = list_input_paths(root)

    return {
        "schema_version": "observation_candidate_review_queue.v0",
        "review_queue_id": "observation_candidate_review_queue_v0",
        "label": "Observation candidate review queue",
        "description": "Deterministic OBS side-lane review queue over repo-local ObservationCandidate records.",
        "queue_status": "queued_for_review" if entries else "no_generated_candidates_available",
        "generated_from": input_paths,
        "candidate_sources": [path for path, _candidate in candidates],
        "queue_entries": entries,
        "status_counts": dict(sorted(status_counts.items())),
        "recommended_action_counts": dict(sorted(action_counts.items())),
        "candidate_type_counts": dict(sorted(type_counts.items())),
        "source_family_counts": dict(sorted(family_counts.items())),
        "priority_band_counts": dict(sorted(band_counts.items())),
        "priority_summary": _score_summary(scores),
        "review_policy_ref": POLICY_PATH,
        "triage_rules_ref": TRIAGE_RULES_PATH,
        "truth_boundary": {
            "queue_entries_are_observed_baselines": False,
            "queue_entries_are_evidence_truth": False,
            "queue_entries_can_mutate_master_index": False,
            "human_review_required": True,
            "source_access_approved": False,
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "no_goals": [
            "No candidate approval or rejection.",
            "No observed baseline creation.",
            "No evidence truth creation.",
            "No SearchNeed or WorkUnit record creation.",
            "No source access approval.",
            "No source sync, live probes, connector runtime, browser use, API calls, or external source access.",
            "No master-index mutation or product behavior change.",
        ],
        "notes": [
            "Queue entries are governance records only.",
            "Recommended actions are future recommendations and do not record review decisions.",
            "Human review is required before downstream use.",
            "Track B local task packet was observed at TRACK-B-06; queue/context mutation is deferred to avoid overwriting parallel Track B state.",
        ],
    }


def validate_built_queue(queue: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    entries = [_mapping(item) for item in _sequence_items(queue.get("queue_entries"))]
    if queue.get("queue_status") not in {"queued_for_review", "no_generated_candidates_available"}:
        errors.append("queue_status must be queued_for_review or no_generated_candidates_available")
    if queue.get("queue_status") == "queued_for_review" and not entries:
        errors.append("queued_for_review queue must have entries")
    for field, value in _mapping(queue.get("truth_boundary")).items():
        if field == "human_review_required":
            if value is not True:
                errors.append("truth_boundary.human_review_required must be true")
        elif value is not False:
            errors.append(f"truth_boundary.{field} must be false")
    for field, value in _mapping(queue.get("product_boundary")).items():
        if value is not False:
            errors.append(f"product_boundary.{field} must be false")
    for entry in entries:
        errors.extend(validate_built_entry(entry))
    return sorted(set(errors))


def validate_built_entry(entry: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    entry_id = str(entry.get("review_queue_entry_id", "<missing>"))
    if entry.get("review_required") is not True:
        errors.append(f"{entry_id}: review_required must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if entry.get(field) is not False:
            errors.append(f"{entry_id}: {field} must be false")
    if entry.get("review_decision_ref") is not None:
        errors.append(f"{entry_id}: review_decision_ref must remain null")
    if not str(entry.get("recommended_review_action", "")).endswith("_future"):
        errors.append(f"{entry_id}: recommended_review_action must be future-only")
    score = entry.get("priority_score")
    if not isinstance(score, int) or score < 0 or score > 100:
        errors.append(f"{entry_id}: priority_score must be 0..100")
    if _contains_forbidden_text(entry):
        errors.append(f"{entry_id}: forbidden claim marker found")
    return errors


def format_plain_summary(queue: Mapping[str, Any]) -> str:
    lines = [
        "build_observation_candidate_review_queue:",
        f"- queue_entry_count: {len(_sequence_items(queue.get('queue_entries')))}",
        f"- recommended_action_counts: {json.dumps(queue.get('recommended_action_counts', {}), sort_keys=True)}",
        f"- priority_band_counts: {json.dumps(queue.get('priority_band_counts', {}), sort_keys=True)}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_queue(queue: Mapping[str, Any]) -> str:
    lines = [
        "# Observation Candidate Review Queue",
        "",
        "This queue is governance only. It records future recommended review actions without approving candidates.",
        "",
        "## Queue Entries",
        "",
        "| Priority | Candidate | Type | Source family | Review state | Recommended action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in _sequence_items(queue.get("queue_entries")):
        item = _mapping(entry)
        lines.append(
            "| {} {} | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                item.get("priority_band"),
                item.get("priority_score"),
                item.get("observation_candidate_id"),
                item.get("candidate_type"),
                item.get("source_family"),
                item.get("proposed_review_state"),
                item.get("recommended_review_action"),
            )
        )
    lines.extend(
        [
            "",
            "## Review Boundary",
            "",
            "- Queue entry is not approval.",
            "- Recommended action is not a review decision.",
            "- No entry is observed baseline evidence.",
            "- No entry is accepted evidence truth.",
            "- No entry can mutate the master index.",
            "- Source access remains unapproved unless a separate future source policy approves it.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_candidate_examples(repo_root: Path) -> list[tuple[str, Mapping[str, Any]]]:
    records: list[tuple[str, Mapping[str, Any]]] = []
    seen: set[str] = set()
    for path in CANDIDATE_EXAMPLES:
        payload = _mapping(_load_json(repo_root / path))
        candidate_id = payload.get("observation_candidate_id")
        if not isinstance(candidate_id, str) or candidate_id in seen:
            continue
        seen.add(candidate_id)
        records.append((path, payload))
    return sorted(records, key=lambda item: str(item[1].get("observation_candidate_id")))


def _build_manifest_index(repo_root: Path) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for manifest_path, key in (
        (OBS01_MANIFEST_PATH, "candidate_records"),
        (OBS01_AUDIT_MANIFEST_PATH, "candidate_records"),
        (OBS02_MANIFEST_PATH, "source_gap_candidates"),
        (OBS02_AUDIT_MANIFEST_PATH, "source_gap_candidates"),
    ):
        manifest = _mapping(_load_json(repo_root / manifest_path))
        for item in _sequence_items(manifest.get(key)):
            record = _mapping(item)
            candidate_id = record.get("observation_candidate_id")
            if isinstance(candidate_id, str):
                index[candidate_id] = record
    return index


def _entry_from_candidate(
    candidate: Mapping[str, Any],
    candidate_path: str,
    manifest_record: Mapping[str, Any],
    triage_rules: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_id = str(candidate.get("observation_candidate_id", "missing_candidate_id"))
    candidate_type = str(candidate.get("candidate_type", "not_evaluable_candidate"))
    source_access_mode = str(candidate.get("source_access_mode", manifest_record.get("source_access_mode", "repo_local_only")))
    policy_status = str(candidate.get("source_policy_status", manifest_record.get("source_policy_status", "not_external")))
    priority_score = _priority_score(candidate, manifest_record, triage_rules)
    priority_band = _priority_band(candidate, manifest_record, priority_score)
    recommended_action = _recommended_action(candidate_type, triage_rules)
    proposed_review_state = _proposed_review_state(candidate, priority_band)
    if priority_band == "insufficient_local_evidence":
        recommended_action = "request_more_evidence_future"
        proposed_review_state = "needs_more_evidence"

    return {
        "review_queue_entry_id": f"review_queue_entry::{candidate_id}",
        "observation_candidate_id": candidate_id,
        "candidate_file_path": candidate_path,
        "candidate_type": candidate_type,
        "candidate_status": candidate.get("candidate_status"),
        "candidate_origin": candidate.get("origin"),
        "related_batch_id": candidate.get("related_batch_id"),
        "related_query_id": candidate.get("related_query_id"),
        "related_slot_id": candidate.get("related_slot_id"),
        "source_family": _source_family(candidate, manifest_record),
        "source_access_mode": source_access_mode,
        "source_policy_status": policy_status,
        "proposed_failure_modes": _string_items(candidate.get("proposed_failure_modes")) or _string_items(manifest_record.get("proposed_failure_modes")),
        "proposed_review_state": proposed_review_state,
        "recommended_review_action": recommended_action,
        "priority_score": priority_score,
        "priority_band": priority_band,
        "review_required": True,
        "review_decision_ref": None,
        "accepted_as_observed_baseline": False,
        "accepted_as_evidence_truth": False,
        "master_index_mutation_allowed": False,
        "notes": [
            "Recommendation only; no review decision is recorded.",
            "Candidate remains review-gated and cannot be converted downstream by this queue.",
            f"source_policy_status={policy_status}",
        ],
    }


def _priority_score(candidate: Mapping[str, Any], manifest_record: Mapping[str, Any], triage_rules: Mapping[str, Any]) -> int:
    for value in (candidate.get("priority_score"), manifest_record.get("priority_score")):
        if isinstance(value, int):
            return max(0, min(100, value))
    fallback = _mapping(triage_rules.get("fallback_scores")).get(candidate.get("candidate_type"), 0)
    return int(fallback) if isinstance(fallback, int) else 0


def _priority_band(candidate: Mapping[str, Any], manifest_record: Mapping[str, Any], score: int) -> str:
    candidate_type = candidate.get("candidate_type")
    candidate_status = candidate.get("candidate_status")
    modes = set(_string_items(candidate.get("proposed_failure_modes")))
    if candidate_type == "policy_blocked_candidate" or candidate_status == "policy_blocked" or "rights_or_policy_block" in modes:
        return "blocked"
    for value in (candidate.get("priority_band"), manifest_record.get("priority_band")):
        if value in PRIORITY_BAND_RANK:
            return str(value)
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    if score > 0:
        return "low"
    return "insufficient_local_evidence"


def _recommended_action(candidate_type: str, triage_rules: Mapping[str, Any]) -> str:
    for rule in _sequence_items(triage_rules.get("recommended_action_rules")):
        item = _mapping(rule)
        if item.get("when_candidate_type") == candidate_type:
            return str(item.get("recommended_review_action"))
    return "request_more_evidence_future"


def _proposed_review_state(candidate: Mapping[str, Any], priority_band: str) -> str:
    if priority_band == "blocked" or candidate.get("candidate_status") == "policy_blocked":
        return "policy_blocked"
    if priority_band == "high":
        return "ready_for_human_decision"
    if candidate.get("candidate_status") == "needs_human_review":
        return "needs_human_review"
    if candidate.get("candidate_status") == "deferred":
        return "deferred"
    return "queued_for_review"


def _source_family(candidate: Mapping[str, Any], manifest_record: Mapping[str, Any]) -> str:
    for value in (candidate.get("source_family"), manifest_record.get("source_family")):
        if isinstance(value, str) and value:
            return value
    source_mode = str(candidate.get("source_access_mode", ""))
    related_system = str(candidate.get("related_system_id", ""))
    candidate_type = str(candidate.get("candidate_type", ""))
    if "google" in related_system or candidate_type == "policy_blocked_candidate":
        return "broad_web_policy_blocked"
    if source_mode == "manual_human_only":
        return "manual_external_baseline"
    if candidate_type == "local_eval_failure":
        return "local_eval"
    return "repo_local_candidate"


def _score_summary(scores: Sequence[int]) -> dict[str, Any]:
    if not scores:
        return {"min": 0, "max": 0, "average": 0}
    return {
        "min": min(scores),
        "max": max(scores),
        "average": round(sum(scores) / len(scores), 2),
    }


def _contains_forbidden_text(payload: Any) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    markers = (
        "scraped google result",
        "google " + "scrape",
        "scrape_google",
        "forum scrape",
        "reddit thread contents",
        "live source observed",
        "external observation performed",
        "accepted evidence truth",
        "accepted-public-truth",
        "observed-baseline claim",
        "source access approved",
        "source sync enabled",
        "provider call completed",
        "model call completed",
        "browser opened",
    )
    return any(marker in text for marker in markers)


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
