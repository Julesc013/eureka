from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping


SCHEMA_VERSION = "query_to_source_action_plan.v0"
PLANNER_ID = "eureka_query_to_source_action_planner_v0"

INTENTS = (
    "find_exact_artifact",
    "find_software",
    "find_driver_or_support_media",
    "find_frontier_resolution_media",
    "find_manual_or_document",
    "find_source_release_or_package",
    "identify_provenance",
    "broad_research_need",
    "ambiguous_query",
)

DOMAIN_PACKS = (
    "legacy_software",
    "driver_support_media",
    "frontier_resolution_media",
    "manuals_docs_scans",
    "package_source_release",
    "web_archive_trace",
    "general_archive_metadata",
)

SOURCE_FAMILIES = (
    "internet_archive_metadata",
    "wayback_cdx_metadata",
    "github_releases_metadata",
    "software_heritage_metadata",
    "package_registry_metadata",
    "open_library_metadata",
    "wikidata_metadata",
    "manual_source_pack",
)

_SOFTWARE_TERMS = {
    "app",
    "apps",
    "application",
    "applications",
    "browser",
    "client",
    "directx",
    "exe",
    "installer",
    "offline installer",
    "portable",
    "sdk",
    "software",
    "tool",
    "tools",
    "utilities",
    "utility",
}
_DRIVER_TERMS = {
    "driver",
    "drivers",
    "firmware",
    "inf",
    "printer",
    "support cd",
    "stylewriter",
}
_FRONTIER_MEDIA_TERMS = {
    "d-theater",
    "d theater",
    "d-vhs",
    "d vhs",
    "demo tape",
    "hd demo",
    "hi-vision",
    "hi vision",
    "high definition demo",
    "muse",
}
_MANUAL_TERMS = {"datasheet", "documentation", "guide", "manual", "pdf", "scan", "service manual"}
_PACKAGE_TERMS = {
    "crate",
    "github",
    "npm",
    "package",
    "pypi",
    "release",
    "repository",
    "source code",
    "tar.gz",
}
_PROVENANCE_TERMS = {
    "archived url",
    "dead url",
    "original source",
    "provenance",
    "trace",
    "wayback",
    "where did",
}
_AMBIGUOUS_TERMS = {
    "app",
    "apps",
    "best",
    "download",
    "file",
    "files",
    "good",
    "old",
    "software",
    "stuff",
    "thing",
    "tools",
}

_DOMAIN_SOURCES = {
    "legacy_software": (
        "internet_archive_metadata",
        "github_releases_metadata",
        "package_registry_metadata",
        "manual_source_pack",
    ),
    "driver_support_media": (
        "internet_archive_metadata",
        "wayback_cdx_metadata",
        "manual_source_pack",
    ),
    "frontier_resolution_media": (
        "internet_archive_metadata",
        "wayback_cdx_metadata",
        "wikidata_metadata",
        "manual_source_pack",
    ),
    "manuals_docs_scans": (
        "internet_archive_metadata",
        "open_library_metadata",
        "manual_source_pack",
    ),
    "package_source_release": (
        "github_releases_metadata",
        "software_heritage_metadata",
        "package_registry_metadata",
        "internet_archive_metadata",
    ),
    "web_archive_trace": (
        "wayback_cdx_metadata",
        "internet_archive_metadata",
        "manual_source_pack",
    ),
    "general_archive_metadata": (
        "internet_archive_metadata",
        "manual_source_pack",
    ),
}


def classify_intent(raw_query: str) -> dict[str, Any]:
    normalized = _normalize_query(raw_query)
    lowered = normalized.casefold()
    token_count = len(_tokens(lowered))

    if not normalized:
        return _intent("ambiguous_query", "low", ["empty query has no searchable intent"])

    if token_count <= 2 and _token_set(lowered).issubset(_AMBIGUOUS_TERMS):
        return _intent(
            "ambiguous_query",
            "low",
            ["query is too broad to route safely without more artifact or domain detail"],
        )

    if _contains_any(lowered, _FRONTIER_MEDIA_TERMS):
        return _intent(
            "find_frontier_resolution_media",
            "high",
            ["frontier-resolution media terms were detected"],
        )

    if _contains_any(lowered, _DRIVER_TERMS):
        return _intent(
            "find_driver_or_support_media",
            "high",
            ["driver/support-media terms were detected"],
        )

    if _contains_any(lowered, _MANUAL_TERMS):
        return _intent(
            "find_manual_or_document",
            "high",
            ["manual, document, or scan terms were detected"],
        )

    if _contains_any(lowered, _PROVENANCE_TERMS):
        return _intent(
            "identify_provenance",
            "medium",
            ["provenance or web-archive trace terms were detected"],
        )

    if _looks_exact_artifact(lowered):
        return _intent(
            "find_exact_artifact",
            "high",
            ["named artifact, version, date, or installer terms were detected"],
        )

    if _contains_any(lowered, _PACKAGE_TERMS):
        return _intent(
            "find_source_release_or_package",
            "medium",
            ["source release or package registry terms were detected"],
        )

    if _contains_any(lowered, _SOFTWARE_TERMS):
        return _intent(
            "find_software",
            "medium",
            ["software or utility terms were detected"],
        )

    if token_count >= 6:
        return _intent(
            "broad_research_need",
            "medium",
            ["query has enough detail for a broad metadata research plan"],
        )

    return _intent(
        "ambiguous_query",
        "low",
        ["no bounded domain signals were strong enough for a narrow source plan"],
    )


def plan_query_to_source_actions(raw_query: str) -> dict[str, Any]:
    normalized = _normalize_query(raw_query)
    intent = classify_intent(normalized)
    domain_pack = _select_domain_pack(normalized, intent["intent"])
    source_families = _source_families_for_domain(domain_pack, intent["intent"])
    suppressions = _candidate_suppressions(normalized, domain_pack, intent["intent"])
    rewrites = _source_query_rewrites(normalized, domain_pack, intent["intent"], suppressions)
    actions = [
        _source_action_plan(normalized, domain_pack, intent["intent"], family, rewrites)
        for family in source_families
    ]
    lane_plans = _result_lane_plans(domain_pack, intent["intent"])
    work_units = _work_units(normalized, domain_pack, intent["intent"], source_families)
    review_handoff = _review_handoff_plan(normalized, domain_pack, intent["intent"])
    plan_id = _stable_id("query_source_plan", normalized, intent["intent"], domain_pack, rewrites)
    explanation = _explanation_packet(
        plan_id=plan_id,
        normalized_query=normalized,
        intent=intent,
        domain_pack=domain_pack,
        source_families=source_families,
        rewrites=rewrites,
        suppressions=suppressions,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "planner_id": PLANNER_ID,
        "plan_id": plan_id,
        "raw_query": str(raw_query or ""),
        "normalized_query": normalized,
        "intent": intent["intent"],
        "intent_confidence": intent["confidence"],
        "intent_reasons": list(intent["reasons"]),
        "domain_pack": domain_pack,
        "source_families": list(source_families),
        "source_query_rewrites": rewrites,
        "candidate_suppressions": suppressions,
        "candidate_lane_expectations": lane_plans,
        "source_actions": actions,
        "work_units": work_units,
        "result_lane_plans": lane_plans,
        "review_handoff_plans": [review_handoff],
        "explanation": explanation,
        "safety": _safety_packet(),
        "non_claims": _non_claims(),
    }


def archive_org_metadata_query(plan_or_query: Mapping[str, Any] | str) -> str:
    if isinstance(plan_or_query, Mapping):
        rewrites = plan_or_query.get("source_query_rewrites")
        if isinstance(rewrites, Mapping):
            rewrite = rewrites.get("archive_org_metadata")
            if isinstance(rewrite, str) and rewrite.strip():
                return rewrite.strip()[:500]
        query = str(plan_or_query.get("normalized_query") or "")
        return query[:500]
    return archive_org_metadata_query(plan_query_to_source_actions(str(plan_or_query)))


def _select_domain_pack(normalized_query: str, intent: str) -> str:
    lowered = normalized_query.casefold()
    if intent == "find_frontier_resolution_media":
        return "frontier_resolution_media"
    if intent == "find_driver_or_support_media":
        return "driver_support_media"
    if intent == "find_manual_or_document":
        return "manuals_docs_scans"
    if intent == "find_source_release_or_package":
        return "package_source_release"
    if intent == "identify_provenance":
        return "web_archive_trace"
    if intent in {"find_exact_artifact", "find_software"}:
        if "source code" in lowered or "github" in lowered or "package" in lowered:
            return "package_source_release"
        return "legacy_software"
    return "general_archive_metadata"


def _source_families_for_domain(domain_pack: str, intent: str) -> tuple[str, ...]:
    if intent == "ambiguous_query":
        return ("internet_archive_metadata",)
    return _DOMAIN_SOURCES.get(domain_pack, ("internet_archive_metadata",))


def _source_query_rewrites(
    normalized_query: str,
    domain_pack: str,
    intent: str,
    suppressions: list[dict[str, Any]],
) -> dict[str, str]:
    archive_query = _archive_query(normalized_query, domain_pack, intent, suppressions)
    rewrites = {"archive_org_metadata": archive_query}
    if domain_pack in {"web_archive_trace", "frontier_resolution_media", "driver_support_media"}:
        rewrites["wayback_cdx_metadata"] = _plain_query(normalized_query, suppressions)
    if domain_pack == "package_source_release":
        rewrites["github_releases_metadata"] = _plain_query(normalized_query, suppressions)
        rewrites["software_heritage_metadata"] = _plain_query(normalized_query, suppressions)
        rewrites["package_registry_metadata"] = _plain_query(normalized_query, suppressions)
    if domain_pack == "manuals_docs_scans":
        rewrites["open_library_metadata"] = _plain_query(normalized_query, suppressions)
    if domain_pack == "frontier_resolution_media":
        rewrites["wikidata_metadata"] = _plain_query(normalized_query, suppressions)
    return rewrites


def _archive_query(
    normalized_query: str,
    domain_pack: str,
    intent: str,
    suppressions: list[dict[str, Any]],
) -> str:
    del intent
    base = _domain_archive_base(normalized_query, domain_pack)
    negative = _negative_terms(suppressions)
    return " ".join(part for part in (base, negative) if part).strip()[:500]


def _domain_archive_base(normalized_query: str, domain_pack: str) -> str:
    lowered = normalized_query.casefold()
    if domain_pack == "frontier_resolution_media":
        locality = '"New York" ' if "new york" in lowered else ""
        year = "1993 " if "1993" in lowered else ""
        return (
            f'(mediatype:movies OR mediatype:texts OR mediatype:collection) '
            f'{locality}{year}("D-Theater" OR "D-VHS" OR "D VHS" OR JVC OR '
            f'"Hi-Vision" OR MUSE OR "HD demo" OR "demo tape")'
        ).strip()
    if domain_pack == "driver_support_media":
        product = _quoted_known_phrase(normalized_query, ("StyleWriter 2500", "Mac OS 8"))
        suffix = "(driver OR drivers OR firmware OR \"support cd\" OR printer)"
        return f"(mediatype:software OR mediatype:texts) {product} {suffix}".strip()
    if domain_pack == "manuals_docs_scans":
        return f"mediatype:texts ({_important_query_terms(normalized_query)} manual documentation scan pdf guide)"
    if domain_pack == "package_source_release":
        return f"({_important_query_terms(normalized_query)} source release package repository)"
    if domain_pack == "web_archive_trace":
        return f"({_important_query_terms(normalized_query)} provenance archived url wayback original source)"
    if domain_pack == "legacy_software":
        if "directx" in lowered and "june 2010" in lowered:
            return (
                'mediatype:software "DirectX SDK" "June 2010" '
                '("offline installer" OR redistributable OR installer OR SDK)'
            )
        platform = _platform_phrase(normalized_query)
        query_terms = _important_query_terms(normalized_query)
        return f"mediatype:software {platform}({query_terms} portable utilities utility software application installer)".strip()
    return f"({_important_query_terms(normalized_query)})"


def _candidate_suppressions(normalized_query: str, domain_pack: str, intent: str) -> list[dict[str, Any]]:
    del intent
    suppressions: list[dict[str, Any]] = []
    if domain_pack == "legacy_software":
        suppressions.append(
            _suppression(
                "suppress_os_images_for_software_queries",
                ["iso", "operating system image", "installation media", "windows 7 iso"],
                "Software and utility searches should not be satisfied by OS images.",
            )
        )
        if "portable" in normalized_query.casefold():
            suppressions.append(
                _suppression(
                    "suppress_install_media_when_portable_requested",
                    ["installer only", "setup disc", "install dvd"],
                    "Portable utility queries should prefer directly usable or portable utility metadata.",
                )
            )
    if domain_pack == "driver_support_media":
        suppressions.append(
            _suppression(
                "suppress_unrelated_driver_models",
                ["unrelated printer model", "laserwriter", "stylewriter 2400"],
                "Driver/support-media plans should avoid adjacent but different hardware models.",
            )
        )
    if domain_pack == "frontier_resolution_media":
        suppressions.append(
            _suppression(
                "suppress_generic_city_or_tourism_media",
                ["tourism", "city guide", "travel guide", "stock footage"],
                "Frontier-resolution media searches should avoid generic location media when a technical tape/source is requested.",
            )
        )
    if domain_pack == "package_source_release":
        suppressions.append(
            _suppression(
                "suppress_binary_only_when_source_requested",
                ["binary only", "installer only", "no source"],
                "Source-release plans should prefer source, package, or repository metadata.",
            )
        )
    return suppressions


def _source_action_plan(
    normalized_query: str,
    domain_pack: str,
    intent: str,
    source_family: str,
    rewrites: Mapping[str, str],
) -> dict[str, Any]:
    execution_mode = "metadata_candidate_runtime" if source_family == "internet_archive_metadata" else "planned_future"
    return {
        "schema_version": "source_action_plan.v0",
        "source_family": source_family,
        "action_kind": "metadata_search",
        "query": _rewrite_for_source_family(rewrites, source_family) or normalized_query,
        "intent": intent,
        "domain_pack": domain_pack,
        "execution_mode": execution_mode,
        "transport_mode": "metadata_only_http" if source_family == "internet_archive_metadata" else "not_executed",
        "candidate_only": True,
        "review_required": True,
        "accepted_truth": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "index_mutation_performed": False,
        "limitations": _source_action_limitations(source_family, execution_mode),
    }


def _source_action_limitations(source_family: str, execution_mode: str) -> list[str]:
    base = ["metadata_only", "candidate_not_reviewed_truth", "no_download", "no_extraction", "no_auto_promotion"]
    if execution_mode == "planned_future":
        base.append("not_executed_in_public_search_v0")
    if source_family != "internet_archive_metadata":
        base.append("source_family_future_or_operator_scoped")
    return base


def _rewrite_for_source_family(rewrites: Mapping[str, str], source_family: str) -> str:
    if source_family == "internet_archive_metadata":
        return str(rewrites.get("archive_org_metadata") or "")
    return str(rewrites.get(source_family) or "")


def _result_lane_plans(domain_pack: str, intent: str) -> list[dict[str, Any]]:
    return [
        {
            "lane": "reviewed_local_results",
            "expected": True,
            "source": "controlled local index",
            "truth_status": "reviewed_only",
        },
        {
            "lane": "archive_org_metadata_candidates",
            "expected": True,
            "source": "internet_archive_metadata",
            "truth_status": "candidate_only",
            "review_required": True,
        },
        {
            "lane": "blocked_actions",
            "expected": True,
            "blocked_actions": ["download", "install_handoff", "execute", "upload", "extract"],
        },
        {
            "lane": "source_actions_planned",
            "expected": intent != "ambiguous_query",
            "domain_pack": domain_pack,
            "truth_status": "plan_only",
        },
    ]


def _work_units(
    normalized_query: str,
    domain_pack: str,
    intent: str,
    source_families: tuple[str, ...],
) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": "query_plan_work_unit.v0",
            "work_unit_id": _stable_id("query_work_unit", normalized_query, domain_pack, intent),
            "work_unit_type": "candidate_metadata_review",
            "query": normalized_query,
            "intent": intent,
            "domain_pack": domain_pack,
            "source_families": list(source_families),
            "operator_action": "review_candidates",
            "mutation_allowed": False,
            "review_required": True,
        }
    ]


def _review_handoff_plan(normalized_query: str, domain_pack: str, intent: str) -> dict[str, Any]:
    return {
        "schema_version": "review_handoff_plan.v0",
        "handoff_id": _stable_id("review_handoff", normalized_query, domain_pack, intent),
        "handoff_kind": "candidate_metadata_review",
        "candidate_states": ["new", "needs_review", "useful_lead", "near_miss", "rejected", "duplicate"],
        "accepted_reviewed_truth_created": False,
        "index_mutation_performed": False,
        "review_required": True,
        "notes": [
            "Candidate metadata can become a reviewed record only through a later explicit review task.",
            "This planner does not promote candidates or mutate public, local, or master indexes.",
        ],
    }


def _explanation_packet(
    *,
    plan_id: str,
    normalized_query: str,
    intent: Mapping[str, Any],
    domain_pack: str,
    source_families: tuple[str, ...],
    rewrites: Mapping[str, str],
    suppressions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "query_plan_explanation_packet.v0",
        "plan_id": plan_id,
        "query": normalized_query,
        "intent": intent.get("intent"),
        "domain_pack": domain_pack,
        "summary": (
            "Deterministic query planner selected a domain pack, source families, "
            "metadata query rewrites, suppressions, and review-only candidate lanes."
        ),
        "factors": [
            {"factor": "intent", "value": intent.get("intent"), "reasons": list(intent.get("reasons") or [])},
            {"factor": "domain_pack", "value": domain_pack},
            {"factor": "source_families", "value": list(source_families)},
            {"factor": "archive_org_metadata_query", "value": rewrites.get("archive_org_metadata", "")},
            {"factor": "candidate_suppressions", "value": [item["suppression_id"] for item in suppressions]},
        ],
        "uncertainty": [
            "Archive.org metadata results are candidates only.",
            "A metadata match does not establish compatibility, rights, safety, or provenance truth.",
        ],
        "blocked": [
            "download",
            "install_handoff",
            "execute",
            "upload",
            "extract",
            "model_provider_call",
            "automatic_promotion",
        ],
    }


def _safety_packet() -> dict[str, bool]:
    return {
        "candidate_only": True,
        "review_required": True,
        "accepted_truth_created": False,
        "source_cache_mutated": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "install_handoff_enabled": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _non_claims() -> list[str]:
    return [
        "not_production_readiness",
        "not_public_launch_readiness",
        "not_accepted_truth",
        "not_rights_clearance",
        "not_malware_scan",
        "not_download_permission",
        "not_full_archive_exhaustiveness_claim",
    ]


def _negative_terms(suppressions: list[dict[str, Any]]) -> str:
    terms: list[str] = []
    for suppression in suppressions:
        for term in suppression.get("terms", []) or []:
            text = str(term).strip()
            if not text:
                continue
            terms.append(f'-"{text}"' if " " in text else f"-{text}")
    return " ".join(terms)


def _plain_query(normalized_query: str, suppressions: list[dict[str, Any]]) -> str:
    return " ".join(part for part in (normalized_query, _negative_terms(suppressions)) if part).strip()[:500]


def _suppression(suppression_id: str, terms: list[str], reason: str) -> dict[str, Any]:
    return {
        "suppression_id": suppression_id,
        "terms": terms,
        "reason": reason,
        "applies_to": ["candidate_results", "source_query_rewrites"],
    }


def _platform_phrase(query: str) -> str:
    lowered = query.casefold()
    if "windows 7" in lowered:
        return '"Windows 7" '
    if "windows xp" in lowered:
        return '"Windows XP" '
    if "mac os 8" in lowered:
        return '"Mac OS 8" '
    return ""


def _quoted_known_phrase(query: str, phrases: tuple[str, ...]) -> str:
    lowered = query.casefold()
    matches = [f'"{phrase}"' for phrase in phrases if phrase.casefold() in lowered]
    return " ".join(matches) if matches else _important_query_terms(query)


def _important_query_terms(query: str) -> str:
    stop = {"a", "an", "and", "best", "for", "from", "iso", "need", "not", "of", "or", "source", "the", "to"}
    terms = [token for token in _tokens(query) if token not in stop]
    if not terms:
        return query
    return " ".join(terms[:12])


def _looks_exact_artifact(lowered: str) -> bool:
    if re.search(r"\b\d+(?:\.\d+){1,3}\b", lowered):
        return True
    if re.search(r"\b(?:19|20)\d{2}\b", lowered) and _contains_any(lowered, _SOFTWARE_TERMS | _PACKAGE_TERMS):
        return True
    return any(term in lowered for term in (".exe", ".zip", "offline installer", "redistributable"))


def _contains_any(lowered: str, terms: set[str]) -> bool:
    return any(term in lowered for term in terms)


def _tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9.]+", value.casefold()) if token]


def _token_set(value: str) -> set[str]:
    return set(_tokens(value))


def _normalize_query(query: str) -> str:
    return " ".join(str(query or "").split())[:160]


def _intent(intent: str, confidence: str, reasons: list[str]) -> dict[str, Any]:
    return {"intent": intent, "confidence": confidence, "reasons": reasons}


def _stable_id(prefix: str, *parts: object) -> str:
    payload = json.dumps(parts, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"
