"""SCOUT runtime over local review-only candidate memory.

SCOUT expands deterministic relations between candidates. It is not a crawler,
does not call live sources, does not mutate indexes, and does not create
accepted truth.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from runtime.candidate_store import build_candidate_fingerprint, sample_candidate_index


DEFAULT_TIMESTAMP = "2026-05-30T00:00:00Z"

RELATION_TYPES = (
    "same_source_family",
    "same_source_locator",
    "same_collection",
    "same_creator",
    "same_uploader",
    "same_domain",
    "same_platform",
    "same_format_family",
    "same_filename_pattern",
    "same_version_family",
    "same_package_family",
    "same_archived_url",
    "same_identifier_hint",
    "near_miss_cluster",
    "duplicate_candidate",
    "provenance_chain",
    "source_lead_from_candidate",
)

RELATED_PATH_KINDS = (
    "related_candidate",
    "related_source_path",
    "related_collection",
    "related_platform",
    "related_format_family",
    "related_package_family",
    "related_review_handoff",
    "related_workunit_seed",
)

WORKUNIT_SEED_TYPES = (
    "inspect_related_collection",
    "compare_near_miss",
    "trace_archived_url",
    "inspect_source_family",
    "verify_candidate_identity",
    "deduplicate_candidate_cluster",
    "request_more_evidence",
)

DEFAULT_POLICY: dict[str, Any] = {
    "scout_outputs_are_not_truth": True,
    "scout_does_not_accept_candidates": True,
    "scout_does_not_promote_records": True,
    "scout_does_not_mutate_reviewed_index": True,
    "scout_does_not_mutate_master_index": True,
    "scout_does_not_mutate_public_index": True,
    "scout_uses_local_candidates_only_by_default": True,
    "live_source_calls_enabled": False,
    "crawling_enabled": False,
    "arbitrary_scraping_enabled": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "public_mutation_enabled": False,
    "review_required_for_outputs": True,
}


def build_scout_run(
    seed_candidate: Mapping[str, Any] | str,
    candidate_index: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a full deterministic SCOUT packet for one seed candidate."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates = _candidate_list(candidate_index)
    seed = _resolve_seed(seed_candidate, candidates)
    relations = infer_candidate_relations(seed, candidates, merged_policy)
    trail = build_discovery_trail(seed, relations, merged_policy)
    related_paths = build_related_path_packets(seed, relations, merged_policy)
    source_trust = build_source_trust_observation([seed, *_related_candidates(relations, candidates)], merged_policy)
    workunit_seeds = build_scout_workunit_seeds(trail, merged_policy)
    scout_run_id = _stable_id("scout_run", seed["candidate_id"], [item["relation_id"] for item in relations])
    run = {
        "schema_version": "scout_run.v0",
        "record_type": "scout_run",
        "scout_run_id": scout_run_id,
        "seed_candidate_id": seed["candidate_id"],
        "candidate_refs": sorted({seed["candidate_id"], *[item["to_ref"] for item in relations]}),
        "relations": relations,
        "relation_count": len(relations),
        "discovery_trail": trail,
        "related_paths": related_paths,
        "source_trust_observations": [source_trust],
        "workunit_seeds": workunit_seeds,
        "projection": project_scout_results(
            {
                "schema_version": "scout_run.v0",
                "scout_run_id": scout_run_id,
                "relations": relations,
                "discovery_trail": trail,
                "related_paths": related_paths,
                "source_trust_observations": [source_trust],
                "workunit_seeds": workunit_seeds,
            },
            "public_web",
            merged_policy,
        ),
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    run["boundary_report"] = build_scout_boundary_report(run, merged_policy)
    return run


def infer_candidate_relations(
    candidate: Mapping[str, Any],
    candidate_index: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Infer deterministic local relations from one candidate to local candidates."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed = dict(candidate)
    candidates = _candidate_list(candidate_index)
    relations: list[dict[str, Any]] = []
    for other in candidates:
        if _candidate_id(other) == _candidate_id(seed):
            continue
        for relation_type, reason in _relation_matches(seed, other):
            relations.append(_relation(seed, other, relation_type, reason))
    relations.append(_relation(seed, seed, "source_lead_from_candidate", "seed candidate can produce reviewable follow-up leads"))
    relations.sort(key=lambda item: (item["relation_type"], item["to_ref"], item["relation_id"]))
    return relations


def build_discovery_trail(
    seed_candidate: Mapping[str, Any],
    relations: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_id = _candidate_id(seed_candidate)
    steps = [
        {
            "step_id": _stable_id("scout_trail_step", seed_id, relation.get("relation_id")),
            "relation_id": str(relation.get("relation_id") or ""),
            "relation_type": str(relation.get("relation_type") or ""),
            "from_ref": str(relation.get("from_ref") or ""),
            "to_ref": str(relation.get("to_ref") or ""),
            "explanation": str(relation.get("explanation") or ""),
            "review_required": True,
            "accepted_truth": False,
        }
        for relation in relations
    ]
    return {
        "schema_version": "discovery_trail.v0",
        "record_type": "discovery_trail",
        "scout_run_id": _stable_id("scout_run_hint", seed_id),
        "trail_id": _stable_id("discovery_trail", seed_id, [step["relation_id"] for step in steps]),
        "seed_id": seed_id,
        "candidate_refs": sorted({seed_id, *[step["to_ref"] for step in steps]}),
        "relation_path": [step["relation_type"] for step in steps],
        "steps": steps,
        "related_path_refs": [],
        "source_trust_observation_ids": [],
        "workunit_seed_ids": [],
        "confidence_label": _confidence_for_count(len(steps)),
        "evidence_refs": [],
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_related_path_packets(
    seed_candidate: Mapping[str, Any],
    relations: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_id = _candidate_id(seed_candidate)
    packets: list[dict[str, Any]] = []
    for relation in relations:
        relation_type = str(relation.get("relation_type") or "")
        path_kind = _path_kind(relation_type)
        packets.append(
            {
                "schema_version": "related_path_packet.v0",
                "record_type": "related_path_packet",
                "scout_run_id": _stable_id("scout_run_hint", seed_id),
                "related_path_id": _stable_id("related_path", seed_id, relation.get("relation_id"), path_kind),
                "path_kind": path_kind,
                "seed_id": seed_id,
                "candidate_refs": [seed_id, str(relation.get("to_ref") or "")],
                "relation_type": relation_type,
                "relation_path": [relation_type],
                "path_ref": str(relation.get("to_ref") or ""),
                "confidence_label": str(relation.get("confidence_label") or "low"),
                "evidence_refs": [],
                "limitations": _limitations(),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    packets.sort(key=lambda item: item["related_path_id"])
    return packets


def build_source_trust_observation(
    candidate_group: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates_by_id = {
        _candidate_id(item): dict(item)
        for item in candidate_group
        if isinstance(item, Mapping) and _candidate_id(item)
    }
    candidates = [candidates_by_id[key] for key in sorted(candidates_by_id)]
    source_families = sorted({_text(item.get("source_family")) for item in candidates if _text(item.get("source_family"))})
    domains = sorted({_text(item.get("domain_id")) for item in candidates if _text(item.get("domain_id"))})
    source_family = source_families[0] if source_families else "unknown_source_family"
    observation_value = {
        "candidate_count": len(candidates),
        "source_families": source_families,
        "domains": domains,
        "metadata_only": True,
        "accepted_evidence_count": 0,
        "live_verified": False,
    }
    return {
        "schema_version": "source_trust_observation.v0",
        "record_type": "source_trust_observation",
        "scout_run_id": _stable_id("scout_run_hint", [item.get("candidate_id") for item in candidates]),
        "observation_id": _stable_id("source_trust_observation", source_family, observation_value),
        "candidate_refs": sorted({_candidate_id(item) for item in candidates if _candidate_id(item)}),
        "source_id": source_family,
        "source_family": source_family,
        "observation_kind": "candidate_source_family_cluster",
        "observation_value": observation_value,
        "relation_type": "source_lead_from_candidate",
        "relation_path": ["source_lead_from_candidate"],
        "confidence_label": _confidence_for_count(len(candidates)),
        "evidence_refs": [],
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_scout_workunit_seeds(
    discovery_trail: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_id = str(discovery_trail.get("seed_id") or "")
    relation_path = [str(item) for item in discovery_trail.get("relation_path", []) or []]
    suggested = ["verify_candidate_identity", "request_more_evidence"]
    if "same_source_family" in relation_path:
        suggested.append("inspect_source_family")
    if "same_collection" in relation_path:
        suggested.append("inspect_related_collection")
    if "same_archived_url" in relation_path:
        suggested.append("trace_archived_url")
    if "near_miss_cluster" in relation_path:
        suggested.append("compare_near_miss")
    if "duplicate_candidate" in relation_path:
        suggested.append("deduplicate_candidate_cluster")
    seeds = []
    for suggestion_type in sorted(set(suggested), key=WORKUNIT_SEED_TYPES.index):
        seeds.append(
            {
                "schema_version": "scout_workunit_seed.v0",
                "record_type": "scout_workunit_seed",
                "scout_run_id": str(discovery_trail.get("scout_run_id") or ""),
                "workunit_seed_id": _stable_id("scout_workunit_seed", seed_id, suggestion_type),
                "seed_type": suggestion_type,
                "suggestion_type": suggestion_type,
                "seed_id": seed_id,
                "candidate_refs": list(discovery_trail.get("candidate_refs") or []),
                "relation_type": "source_lead_from_candidate",
                "relation_path": relation_path,
                "creates_runtime_workunit": False,
                "confidence_label": "low",
                "evidence_refs": [],
                "limitations": _limitations(),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return seeds


def project_scout_results(
    scout_run: Mapping[str, Any],
    projection_profile: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    profile = str(projection_profile or "public_web")
    public_profile = profile == "public_web"
    relations = [dict(item) for item in scout_run.get("relations", []) if isinstance(item, Mapping)]
    related_paths = [dict(item) for item in scout_run.get("related_paths", []) if isinstance(item, Mapping)]
    workunit_seeds = [dict(item) for item in scout_run.get("workunit_seeds", []) if isinstance(item, Mapping)]
    trail = dict(scout_run.get("discovery_trail") or {})
    return {
        "schema_version": "scout_projection.v0",
        "record_type": "scout_projection",
        "projection_profile": profile,
        "scout_run_id": str(scout_run.get("scout_run_id") or trail.get("scout_run_id") or ""),
        "relation_count": len(relations),
        "related_paths_count": len(related_paths),
        "workunit_seed_count": len(workunit_seeds),
        "discovery_trail_ref": str(trail.get("trail_id") or ""),
        "source_trust_hint": _source_trust_hint(scout_run),
        "candidate_lane_extension": {
            "related_paths_count": len(related_paths),
            "discovery_trail_ref": str(trail.get("trail_id") or ""),
            "source_trust_hint": _source_trust_hint(scout_run),
            "workunit_seed_count": len(workunit_seeds),
        },
        "related_paths": [_public_related_path(item) for item in related_paths],
        "allowed_actions": ["inspect", "view_provenance", "read"]
        + ([] if public_profile else ["create_review_handoff", "create_workunit_seed_suggestion"]),
        "blocked_actions": [
            "accept",
            "promote",
            "download",
            "extract",
            "execute",
            "crawl",
            "live_source_call",
            "call_model_provider",
        ],
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def build_scout_boundary_report(
    scout_run: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    return {
        "schema_version": "scout_boundary_report.v0",
        "record_type": "scout_boundary_report",
        "scout_run_id": str(scout_run.get("scout_run_id") or ""),
        "candidate_refs": list(scout_run.get("candidate_refs") or []),
        "scout_outputs_are_not_truth": bool(merged_policy.get("scout_outputs_are_not_truth", True)),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def load_candidate_index_from_examples() -> dict[str, Any]:
    return sample_candidate_index()


def _relation_matches(seed: Mapping[str, Any], other: Mapping[str, Any]) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    if _text(seed.get("source_family")) and _text(seed.get("source_family")) == _text(other.get("source_family")):
        matches.append(("same_source_family", "candidates share a source family"))
    if _locator_host(seed) and _locator_host(seed) == _locator_host(other):
        matches.append(("same_source_locator", "candidates share a source locator host"))
    if _text(seed.get("domain_id")) and _text(seed.get("domain_id")) == _text(other.get("domain_id")):
        matches.append(("same_domain", "candidates share a domain pack"))
    if _platform(seed) and _platform(seed) == _platform(other):
        matches.append(("same_platform", "candidates share a platform hint"))
    if _format_family(seed) and _format_family(seed) == _format_family(other):
        matches.append(("same_format_family", "candidates share a format family hint"))
    if _filename_pattern(seed) and _filename_pattern(seed) == _filename_pattern(other):
        matches.append(("same_filename_pattern", "candidates share a filename/title pattern"))
    if _version_family(seed) and _version_family(seed) == _version_family(other):
        matches.append(("same_version_family", "candidates share a version family hint"))
    if _package_family(seed) and _package_family(seed) == _package_family(other):
        matches.append(("same_package_family", "candidates share a package family hint"))
    if _identifier_hint(seed) and _identifier_hint(seed) == _identifier_hint(other):
        matches.append(("same_identifier_hint", "candidates share an identifier hint"))
    if _near_miss(seed, other):
        matches.append(("near_miss_cluster", "candidates share partial query/title tokens"))
    if _dedupe_key(seed) and _dedupe_key(seed) == _dedupe_key(other):
        matches.append(("duplicate_candidate", "candidate fingerprints share a dedupe key"))
    if _locator_host(seed) == "archive.org" and _locator_host(other) == "archive.org":
        matches.append(("same_archived_url", "candidates are Archive.org detail paths"))
        matches.append(("provenance_chain", "candidate metadata can be reviewed as a provenance trail"))
    return matches


def _relation(seed: Mapping[str, Any], other: Mapping[str, Any], relation_type: str, reason: str) -> dict[str, Any]:
    from_ref = _candidate_id(seed)
    to_ref = _candidate_id(other)
    return {
        "schema_version": "scout_relation.v0",
        "record_type": "curator_relation",
        "scout_run_id": _stable_id("scout_run_hint", from_ref),
        "relation_id": _stable_id("scout_relation", from_ref, to_ref, relation_type),
        "candidate_refs": [from_ref, to_ref],
        "relation_type": relation_type,
        "from_ref": from_ref,
        "to_ref": to_ref,
        "relation_path": [relation_type],
        "confidence_label": "medium" if relation_type in {"same_source_family", "same_domain", "duplicate_candidate"} else "low",
        "evidence_refs": [],
        "explanation": reason,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def _candidate_list(candidate_index: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(candidate_index, Mapping):
        if isinstance(candidate_index.get("candidates"), list):
            values = candidate_index.get("candidates", [])
        elif isinstance(candidate_index.get("results"), list):
            values = candidate_index.get("results", [])
        else:
            values = []
    else:
        values = candidate_index
    return [dict(item) for item in values if isinstance(item, Mapping)]


def _resolve_seed(seed_candidate: Mapping[str, Any] | str, candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if isinstance(seed_candidate, Mapping):
        return dict(seed_candidate)
    seed_id = str(seed_candidate)
    for candidate in candidates:
        if _candidate_id(candidate) == seed_id:
            return dict(candidate)
    raise ValueError(f"seed candidate not found: {seed_id}")


def _related_candidates(relations: Sequence[Mapping[str, Any]], candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs = {str(item.get("to_ref") or "") for item in relations}
    return [dict(candidate) for candidate in candidates if _candidate_id(candidate) in refs]


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return str(candidate.get("candidate_id") or candidate.get("result_id") or "")


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _tokens(value: str) -> set[str]:
    return {item for item in re.findall(r"[a-z0-9][a-z0-9._-]*", value.casefold()) if len(item) > 2}


def _haystack(candidate: Mapping[str, Any]) -> str:
    return " ".join(
        [
            _text(candidate.get("title")),
            _text(candidate.get("description")),
            _text(candidate.get("matched_query")),
            _text(candidate.get("domain_id")),
            json.dumps(candidate.get("source_locator") or {}, sort_keys=True),
        ]
    ).casefold()


def _source_locator(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    locator = candidate.get("source_locator")
    return locator if isinstance(locator, Mapping) else {}


def _locator_url(candidate: Mapping[str, Any]) -> str:
    locator = _source_locator(candidate)
    return _text(locator.get("url") or locator.get("value") or locator.get("identifier"))


def _locator_host(candidate: Mapping[str, Any]) -> str:
    url = _locator_url(candidate)
    parsed = urlparse(url if "://" in url else f"https://{url}") if url else None
    host = parsed.netloc.casefold() if parsed else ""
    return host.removeprefix("www.")


def _platform(candidate: Mapping[str, Any]) -> str:
    text = _haystack(candidate)
    for term in ("windows 7", "windows xp", "mac os 8", "directx", "d-theater", "d-vhs"):
        if term in text:
            return term
    return ""


def _format_family(candidate: Mapping[str, Any]) -> str:
    text = _haystack(candidate)
    if "driver" in text:
        return "driver_support_media"
    if "sdk" in text or "installer" in text or "portable" in text or "utilities" in text:
        return "software_metadata"
    if "d-theater" in text or "d-vhs" in text or "demo tape" in text:
        return "frontier_media"
    return ""


def _filename_pattern(candidate: Mapping[str, Any]) -> str:
    title = _text(candidate.get("title")).casefold()
    tokens = [item for item in re.findall(r"[a-z0-9]+", title) if len(item) > 3]
    return "-".join(tokens[:2]) if len(tokens) >= 2 else ""


def _version_family(candidate: Mapping[str, Any]) -> str:
    match = re.search(r"\b(?:19|20)\d{2}\b|\b\d+(?:\.\d+){1,3}\b", _haystack(candidate))
    return match.group(0) if match else ""


def _package_family(candidate: Mapping[str, Any]) -> str:
    text = _haystack(candidate)
    if "directx" in text:
        return "directx"
    if "portable" in text or "utilities" in text:
        return "portable_utilities"
    if "stylewriter" in text:
        return "stylewriter"
    return ""


def _identifier_hint(candidate: Mapping[str, Any]) -> str:
    url = _locator_url(candidate)
    if not url:
        return ""
    return url.rstrip("/").rsplit("/", 1)[-1].casefold()


def _near_miss(seed: Mapping[str, Any], other: Mapping[str, Any]) -> bool:
    left = _tokens(_haystack(seed))
    right = _tokens(_haystack(other))
    if not left or not right:
        return False
    overlap = left & right
    return len(overlap) >= 2 and _candidate_id(seed) != _candidate_id(other)


def _dedupe_key(candidate: Mapping[str, Any]) -> str:
    direct = _text(candidate.get("dedupe_key"))
    if direct:
        return direct
    fingerprint = candidate.get("fingerprint")
    if isinstance(fingerprint, Mapping) and _text(fingerprint.get("dedupe_key")):
        return _text(fingerprint.get("dedupe_key"))
    return build_candidate_fingerprint(candidate).get("dedupe_key", "")


def _path_kind(relation_type: str) -> str:
    if relation_type in {"same_collection", "same_source_locator", "same_archived_url", "provenance_chain"}:
        return "related_source_path"
    if relation_type == "same_platform":
        return "related_platform"
    if relation_type == "same_format_family":
        return "related_format_family"
    if relation_type in {"same_package_family", "same_version_family"}:
        return "related_package_family"
    if relation_type == "source_lead_from_candidate":
        return "related_workunit_seed"
    return "related_candidate"


def _public_related_path(path: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "related_path_id": str(path.get("related_path_id") or ""),
        "path_kind": str(path.get("path_kind") or ""),
        "candidate_refs": list(path.get("candidate_refs") or []),
        "relation_type": str(path.get("relation_type") or ""),
        "confidence_label": str(path.get("confidence_label") or "low"),
        "review_required": True,
        "accepted_truth": False,
    }


def _source_trust_hint(scout_run: Mapping[str, Any]) -> str:
    observations = [item for item in scout_run.get("source_trust_observations", []) if isinstance(item, Mapping)]
    if not observations:
        return "source_trust_unobserved"
    observation = observations[0]
    value = observation.get("observation_value") if isinstance(observation.get("observation_value"), Mapping) else {}
    return f"{observation.get('source_family')}:candidate_count={value.get('candidate_count', 0)}"


def _confidence_for_count(count: int) -> str:
    if count >= 5:
        return "medium"
    if count >= 2:
        return "low"
    return "low"


def _limitations() -> list[str]:
    return [
        "scout_relation_expansion_only",
        "candidate_not_reviewed_truth",
        "review_required",
        "local_candidates_only",
        "no_live_source_call",
        "no_crawl",
        "no_download",
        "no_extraction",
        "no_model_provider",
        "no_auto_promotion",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "crawling_performed": False,
        "arbitrary_scraping_performed": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    forbidden_true = (
        "live_source_calls_enabled",
        "crawling_enabled",
        "arbitrary_scraping_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "public_mutation_enabled",
    )
    enabled = [key for key in forbidden_true if bool(policy.get(key))]
    if enabled:
        raise PermissionError(f"SCOUT policy enables forbidden behavior: {', '.join(enabled)}")


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"
