from __future__ import annotations

import re
from typing import Any

from runtime.engine.interfaces.public.query_plan import ResolutionTask


WINDOWS_PLATFORM_HINTS = (
    (
        re.compile(r"\bwindows 7\b", re.IGNORECASE),
        {
            "os_family": "Windows NT",
            "os_version": "6.1",
            "marketing_alias": "Windows 7",
        },
    ),
    (
        re.compile(r"\b(?:windows xp|xp)\b", re.IGNORECASE),
        {
            "os_family": "Windows NT",
            "os_version": "5.1",
            "marketing_alias": "Windows XP",
        },
    ),
    (
        re.compile(r"\b(?:windows 98|win98)\b", re.IGNORECASE),
        {
            "os_family": "Windows",
            "os_version": "4.1",
            "marketing_alias": "Windows 98",
            "platform_family": "Win9x",
        },
    ),
    (
        re.compile(r"\bwindows 2000\b", re.IGNORECASE),
        {
            "os_family": "Windows NT",
            "os_version": "5.0",
            "marketing_alias": "Windows 2000",
        },
    ),
)

MAC_PLATFORM_HINTS = (
    (
        re.compile(r"\bmac os 9\b", re.IGNORECASE),
        {
            "os_family": "Mac OS",
            "os_version": "9",
            "marketing_alias": "Mac OS 9",
        },
    ),
)

SOFTWARE_NOUN_HINTS = (
    "apps",
    "software",
    "browser",
    "client",
    "utility",
)


def plan_query_by_rules(raw_query: str) -> ResolutionTask:
    normalized_query = _normalize_query(raw_query)
    platform = _extract_platform_constraints(normalized_query)

    latest_release_task = _plan_latest_compatible_release(raw_query, normalized_query, platform)
    if latest_release_task is not None:
        return latest_release_task

    driver_task = _plan_driver_query(raw_query, normalized_query, platform)
    if driver_task is not None:
        return driver_task

    documentation_task = _plan_documentation_query(raw_query, normalized_query, platform)
    if documentation_task is not None:
        return documentation_task

    article_task = _plan_article_query(raw_query, normalized_query, platform)
    if article_task is not None:
        return article_task

    vague_software_task = _plan_vague_software_query(raw_query, normalized_query, platform)
    if vague_software_task is not None:
        return vague_software_task

    platform_software_task = _plan_platform_software_query(raw_query, normalized_query, platform)
    if platform_software_task is not None:
        return platform_software_task

    return ResolutionTask(
        raw_query=raw_query,
        task_kind="generic_search",
        object_type="unknown",
        constraints={},
        prefer=(),
        exclude=(),
        action_hints=("inspect",),
        source_hints=(),
        planner_confidence="low",
        planner_notes=(
            "No bounded Query Planner v0 family matched; keep the request as a generic deterministic search.",
        ),
    )


def _plan_latest_compatible_release(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    match = re.fullmatch(
        r"latest\s+(.+?)\s+before\s+(.+?)\s+support ended",
        normalized_query,
    )
    if match is None:
        return None
    product_hint = _title_case_phrase(match.group(1))
    support_context = match.group(2).strip()
    constraints = _base_constraints(platform)
    constraints["product_hint"] = product_hint
    constraints["support_window_hint"] = f"latest before {support_context} support ended"
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_software_release",
        object_type="software_release",
        constraints=constraints,
        prefer=(
            "versioned_release_artifact",
            "release_notes_with_support_window",
            "compatibility_evidence",
        ),
        exclude=(
            "latest_overall_without_platform_evidence",
            "operating_system_image",
        ),
        action_hints=("inspect", "compare_versions", "download", "export_manifest"),
        source_hints=("github_releases",),
        planner_confidence="high",
        planner_notes=(
            "Recognized a latest-compatible release query.",
            "Current retrieval remains bounded deterministic search; planner output is stored for later reuse.",
        ),
    )


def _plan_driver_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    match = re.fullmatch(r"driver\s+for\s+(.+)", normalized_query)
    if match is None:
        return None
    hardware_or_platform = _strip_platform_tokens(match.group(1).strip())
    constraints = _base_constraints(platform)
    if hardware_or_platform:
        constraints["hardware_hint"] = _restore_hardware_case(raw_query, hardware_or_platform)
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_driver",
        object_type="driver",
        constraints=constraints,
        prefer=(
            "driver_package",
            "support_bundle_member",
            "documentation_with_driver_locator",
        ),
        exclude=(
            "generic_advice_only",
            "unrelated_full_os_media",
        ),
        action_hints=("inspect", "download", "export_manifest"),
        source_hints=(),
        planner_confidence="high" if hardware_or_platform or platform else "medium",
        planner_notes=(
            "Recognized a driver lookup query.",
            "Hardware and platform hints remain bounded extracted constraints only.",
        ),
    )


def _plan_documentation_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    match = re.fullmatch(r"manual\s+for\s+(.+)", normalized_query)
    if match is None:
        return None
    subject_hint = match.group(1).strip()
    constraints = _base_constraints(platform)
    constraints["document_hint"] = "manual"
    constraints["product_hint"] = _restore_subject_case(raw_query, subject_hint)
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_documentation",
        object_type="documentation",
        constraints=constraints,
        prefer=("manual_pdf_or_scan", "documentation_record", "citeable_scan"),
        exclude=("generic_forum_post",),
        action_hints=("inspect", "view_read", "cite", "export_manifest"),
        source_hints=(),
        planner_confidence="high",
        planner_notes=(
            "Recognized a manual or documentation lookup query.",
        ),
    )


def _plan_article_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    match = re.fullmatch(
        r"article\s+about\s+(.+?)\s+in\s+(?:a\s+)?(\d{4})\s+magazine",
        normalized_query,
    )
    if match is not None:
        topic_hint = match.group(1).strip()
        year_hint = match.group(2)
    else:
        alternate_match = re.fullmatch(
            r"article\s+inside\s+(\d{4})\s+magazine\s+scan\s+about\s+(.+)",
            normalized_query,
        )
        if alternate_match is None:
            return None
        year_hint = alternate_match.group(1)
        topic_hint = alternate_match.group(2).strip()
    constraints = _base_constraints(platform)
    constraints["topic_hint"] = topic_hint
    constraints["date_year_hint"] = year_hint
    constraints["document_hint"] = "magazine"
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_document_article",
        object_type="document_article",
        constraints=constraints,
        prefer=("article_member", "page_range_hit", "ocr_text_snippet"),
        exclude=("whole_issue_only_without_article_trace",),
        action_hints=("inspect", "view_read", "cite", "export_manifest"),
        source_hints=(),
        planner_confidence="high",
        planner_notes=(
            "Recognized an article-inside-scan style query.",
        ),
    )


def _plan_vague_software_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    constraints = _base_constraints(platform)
    if "ftp client" in normalized_query and platform:
        constraints["function_hint"] = "ftp client"
        if "blue" in normalized_query:
            constraints["descriptor_hint"] = "blue"
        if "old" in normalized_query:
            constraints["temporal_style_hint"] = "old"
        return ResolutionTask(
            raw_query=raw_query,
            task_kind="find_software_release",
            object_type="software_release",
            constraints=constraints,
            prefer=("named_software_artifact", "descriptive_release_notes", "compatibility_evidence"),
            exclude=("generic_advice_only", "operating_system_image"),
            action_hints=("inspect", "download", "export_manifest"),
            source_hints=("github_releases",),
            planner_confidence="medium",
            planner_notes=(
                "Recognized a vague software identity query with platform and functional hints.",
            ),
        )

    if "software to" in normalized_query or "fix broken registry" in normalized_query:
        if "fix broken registry" in normalized_query:
            constraints["function_hint"] = "fix broken registry"
        elif "software to" in normalized_query:
            constraints["function_hint"] = normalized_query.partition("software to")[2].strip()
        return ResolutionTask(
            raw_query=raw_query,
            task_kind="find_software_release",
            object_type="software_release",
            constraints=constraints,
            prefer=("direct_software_artifact", "period_appropriate_utility", "compatibility_evidence"),
            exclude=("generic_advice_only", "modern_incompatible_release"),
            action_hints=("inspect", "download", "export_manifest"),
            source_hints=("synthetic", "github_releases") if platform else (),
            planner_confidence="medium",
            planner_notes=(
                "Recognized a functional software lookup query.",
            ),
        )
    return None


def _plan_platform_software_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    if not platform:
        return None
    if not any(term in normalized_query for term in SOFTWARE_NOUN_HINTS):
        return None
    constraints = _base_constraints(platform)
    function_hint = _infer_software_function_hint(normalized_query)
    if function_hint is not None:
        constraints["function_hint"] = function_hint
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="browse_software",
        object_type="software",
        constraints=constraints,
        prefer=("direct_software_artifact", "portable_package", "compatibility_evidence"),
        exclude=("operating_system_image", "full_os_iso"),
        action_hints=("inspect", "download", "export_manifest"),
        source_hints=("synthetic", "github_releases"),
        planner_confidence="high",
        planner_notes=(
            "Recognized a platform-scoped software browsing query.",
        ),
    )


def _infer_software_function_hint(normalized_query: str) -> str | None:
    if "browser" in normalized_query:
        return "browser"
    if "client" in normalized_query:
        return "client"
    return None


def _extract_platform_constraints(normalized_query: str) -> dict[str, Any]:
    for pattern, payload in WINDOWS_PLATFORM_HINTS + MAC_PLATFORM_HINTS:
        if pattern.search(normalized_query):
            return {"platform": dict(payload)}
    return {}


def _strip_platform_tokens(value: str) -> str:
    stripped = value
    for pattern, _payload in WINDOWS_PLATFORM_HINTS + MAC_PLATFORM_HINTS:
        stripped = pattern.sub("", stripped)
    stripped = re.sub(r"\s+", " ", stripped)
    return stripped.strip(" -")


def _normalize_query(raw_query: str) -> str:
    return re.sub(r"\s+", " ", raw_query.strip()).casefold()


def _title_case_phrase(value: str) -> str:
    if not value:
        return value
    return " ".join(part.capitalize() if part.islower() else part for part in value.split())


def _restore_subject_case(raw_query: str, normalized_fragment: str) -> str:
    match = re.search(re.escape(normalized_fragment), raw_query, re.IGNORECASE)
    if match is None:
        return _title_case_phrase(normalized_fragment)
    return raw_query[match.start() : match.end()]


def _restore_hardware_case(raw_query: str, normalized_fragment: str) -> str:
    return _restore_subject_case(raw_query, normalized_fragment)


def _base_constraints(platform: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in platform.items()}
