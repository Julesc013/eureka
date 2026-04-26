from __future__ import annotations

import re
from typing import Any

from runtime.engine.interfaces.public.query_plan import ResolutionTask


CURRENT_SOURCE_HINTS = (
    "internet_archive_recorded",
    "local_bundle_fixtures",
    "github_releases",
    "synthetic_fixture",
)

FUTURE_SOURCE_HINTS = (
    "wayback_memento_placeholder",
    "internet_archive_placeholder",
    "vendor_archive_future",
)

OLD_PLATFORM_SOFTWARE_EXCLUDES = (
    "operating_system_image",
    "os_iso_image",
    "operating_system_install_media",
    "generic_all_system_dump_without_member_index",
    "unrelated_support_cd_parent_without_relevant_member",
)


PLATFORM_HINTS: tuple[tuple[re.Pattern[str], dict[str, Any]], ...] = (
    (
        re.compile(r"\b(?:windows 7|win7|windows nt 6\.1|nt 6\.1)\b", re.IGNORECASE),
        {
            "family": "Windows NT",
            "version": "6.1",
            "marketing_alias": "Windows 7",
            "aliases": ["Win7", "Windows NT 6.1"],
        },
    ),
    (
        re.compile(r"\b(?:windows xp|winxp|xp|windows nt 5\.1|nt 5\.1)\b", re.IGNORECASE),
        {
            "family": "Windows NT",
            "version": "5.1",
            "marketing_alias": "Windows XP",
            "aliases": ["WinXP", "Windows NT 5.1"],
        },
    ),
    (
        re.compile(r"\b(?:windows 2000|win2k|windows nt 5\.0|nt 5\.0)\b", re.IGNORECASE),
        {
            "family": "Windows NT",
            "version": "5.0",
            "marketing_alias": "Windows 2000",
            "aliases": ["Win2k", "Windows NT 5.0"],
        },
    ),
    (
        re.compile(r"\b(?:windows 98|win98)\b", re.IGNORECASE),
        {
            "family": "Windows",
            "version": "4.1",
            "marketing_alias": "Windows 98",
            "platform_family": "Win9x",
            "aliases": ["Win98"],
        },
    ),
    (
        re.compile(r"\b(?:windows 95|win95)\b", re.IGNORECASE),
        {
            "family": "Windows",
            "version": "4.0",
            "marketing_alias": "Windows 95",
            "platform_family": "Win9x",
            "aliases": ["Win95"],
        },
    ),
    (
        re.compile(r"\b(?:classic mac os|mac os 9)\b", re.IGNORECASE),
        {
            "family": "Classic Mac OS",
            "version": "9",
            "marketing_alias": "Mac OS 9",
            "aliases": ["Classic Mac OS"],
        },
    ),
    (
        re.compile(r"\b(?:powerpc\s+)?(?:mac os x 10\.4|mac os x tiger|tiger)\b", re.IGNORECASE),
        {
            "family": "Mac OS X",
            "version": "10.4",
            "marketing_alias": "Mac OS X Tiger",
            "architecture": "PowerPC",
            "aliases": ["PowerPC Mac OS X 10.4"],
        },
    ),
    (
        re.compile(r"\b(?:mac os x 10\.6|snow leopard)\b", re.IGNORECASE),
        {
            "family": "Mac OS X",
            "version": "10.6",
            "marketing_alias": "Mac OS X Snow Leopard",
            "aliases": ["Snow Leopard"],
        },
    ),
)

SOFTWARE_NOUN_HINTS = (
    "app",
    "apps",
    "application",
    "applications",
    "software",
    "browser",
    "client",
    "utility",
    "utilities",
    "tool",
    "tools",
    "antivirus",
)

GENERIC_PRODUCT_CLASSES = {
    "app",
    "apps",
    "application",
    "applications",
    "browser",
    "client",
    "software",
    "tool",
    "tools",
    "utility",
    "utilities",
}


def plan_query_by_rules(raw_query: str) -> ResolutionTask:
    normalized_query = _normalize_query(raw_query)
    platform = _extract_platform_constraints(normalized_query)

    latest_release_task = _plan_latest_compatible_release(raw_query, normalized_query, platform)
    if latest_release_task is not None:
        return latest_release_task

    member_task = _plan_member_or_container_query(raw_query, normalized_query, platform)
    if member_task is not None:
        return member_task

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
    before_support_match = re.fullmatch(
        r"(?:latest|last)\s+(.+?)\s+before\s+(.+?)\s+support ended",
        normalized_query,
    )
    direct_platform_match = re.fullmatch(
        r"(?:latest|last)\s+(.+?)\s+for\s+(.+)",
        normalized_query,
    )
    if before_support_match is None and direct_platform_match is None:
        return None

    product_phrase = (
        before_support_match.group(1)
        if before_support_match is not None
        else direct_platform_match.group(1)
    ).strip()
    constraints = _base_constraints(platform)
    _apply_product_or_function_hint(raw_query, product_phrase, constraints)
    constraints["temporal_goal"] = (
        "latest_before_support_drop"
        if before_support_match is not None
        else "latest_compatible"
    )
    if before_support_match is not None:
        support_context = before_support_match.group(2).strip()
        constraints["support_window_hint"] = f"latest before {support_context} support ended"
    constraints["compatibility_required"] = True
    constraints["platform_is_constraint"] = bool(platform)
    constraints["representation_hints"] = [
        "versioned_release_artifact",
        "release_notes",
        "installer",
        "portable_package",
    ]
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_latest_compatible_release",
        object_type="software_release",
        constraints=constraints,
        prefer=(
            "versioned_release_artifact",
            "release_notes_with_support_window",
            "compatibility_evidence",
        ),
        exclude=(
            "latest_overall_without_platform_evidence",
            *OLD_PLATFORM_SOFTWARE_EXCLUDES,
        ),
        action_hints=("inspect", "compare_versions", "fetch_if_available", "export_manifest"),
        source_hints=(
            "internet_archive_recorded",
            "github_releases",
            "wayback_memento_placeholder",
            "vendor_archive_future",
        ),
        planner_confidence="high" if platform else "medium",
        planner_notes=(
            "Recognized a latest-compatible release query.",
            "The planner does not claim the exact latest version; it records the temporal and platform constraints for later evidence checks.",
        ),
    )


def _plan_member_or_container_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    has_container_signal = any(
        signal in normalized_query
        for signal in (" inside ", " inside", "support cd", " iso", " zip", "bundle", "package")
    )
    has_distribution_signal = any(
        signal in normalized_query
        for signal in ("offline installer", "service pack download")
    )
    if not has_container_signal and not has_distribution_signal:
        return None

    member_type = _infer_member_type(normalized_query)
    if member_type is None and not has_distribution_signal:
        return None

    constraints = _base_constraints(platform)
    container_hint = _infer_container_hint(normalized_query)
    if container_hint is not None:
        constraints["container_hint"] = container_hint
    if member_type is not None:
        constraints["member_type_hint"] = member_type
    product_hint = _infer_named_product_hint(raw_query, normalized_query)
    if product_hint is not None:
        constraints["product_hint"] = product_hint
    function_hint = _infer_software_function_hint(normalized_query)
    if function_hint is not None:
        constraints["function_hint"] = function_hint
    constraints["representation_hints"] = _member_representation_hints(container_hint)
    constraints["member_discovery_hints"] = {
        "preserve_parent_lineage": True,
        "prefer_member_path": True,
        "member_preview": True,
    }
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_member_in_container",
        object_type="package_member",
        constraints=constraints,
        prefer=("member_record", "member_path", "parent_bundle_with_relevant_member", "compatibility_evidence"),
        exclude=("parent_container_only_without_member_trace", "generic_collection_without_member_index"),
        action_hints=("inspect_members", "decompose", "preview_member", "fetch_if_available", "export_manifest"),
        source_hints=("local_bundle_fixtures", "internet_archive_recorded", "internet_archive_placeholder"),
        planner_confidence="high" if container_hint or member_type else "medium",
        planner_notes=(
            "Recognized a member or container discovery query.",
            "Member-level target records are future work; this plan only emits bounded decomposition hints.",
        ),
    )


def _plan_driver_query(
    raw_query: str,
    normalized_query: str,
    platform: dict[str, Any],
) -> ResolutionTask | None:
    if "driver" not in normalized_query:
        return None
    hardware_hint = _extract_hardware_hint(raw_query, normalized_query)
    if not hardware_hint and not platform:
        return None
    constraints = _base_constraints(platform)
    if hardware_hint:
        constraints["hardware_hint"] = hardware_hint
    constraints["representation_hints"] = [
        "driver_package",
        "INF",
        "support_media_member",
        "readme",
        "manual",
    ]
    constraints["member_discovery_hints"] = {
        "support_media_member": True,
        "prefer_inf_member": True,
    }
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_driver",
        object_type="driver",
        constraints=constraints,
        prefer=(
            "driver_package",
            "inf_member",
            "support_bundle_member",
            "documentation_with_driver_locator",
        ),
        exclude=(
            "generic_advice_only",
            "unrelated_full_os_media",
            "parent_support_cd_without_matching_driver_member",
        ),
        action_hints=("inspect", "inspect_members", "decompose", "fetch_if_available", "export_manifest"),
        source_hints=(
            "local_bundle_fixtures",
            "internet_archive_recorded",
            "wayback_memento_placeholder",
            "vendor_archive_future",
        ),
        planner_confidence="high" if hardware_hint and platform else "medium",
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
    if not any(term in normalized_query for term in ("manual", "readme", "resource kit", "documentation")):
        return None

    subject_hint: str | None = None
    document_hint = "documentation"
    manual_for_match = re.fullmatch(r"manual\s+for\s+(.+)", normalized_query)
    if manual_for_match is not None:
        subject_hint = _restore_subject_case(raw_query, manual_for_match.group(1).strip())
        document_hint = "manual"
    elif "hardware maintenance manual" in normalized_query:
        subject_hint = _restore_subject_case(
            raw_query,
            normalized_query.replace("hardware maintenance manual", "").strip(),
        )
        document_hint = "hardware maintenance manual"
    elif "resource kit" in normalized_query:
        subject_hint = _restore_subject_case(raw_query, normalized_query.replace("pdf", "").strip())
        document_hint = "resource kit"
    elif "readme" in normalized_query:
        subject_hint = _restore_subject_case(raw_query, normalized_query.replace("readme", "").strip())
        document_hint = "readme"

    if subject_hint is None:
        return None

    constraints = _base_constraints(platform)
    constraints["document_hint"] = document_hint
    constraints["product_hint"] = subject_hint
    constraints["representation_hints"] = ["manual", "PDF", "TXT", "README", "scan"]
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_documentation",
        object_type="documentation",
        constraints=constraints,
        prefer=("manual_pdf_or_scan", "documentation_record", "readme_member", "citeable_scan"),
        exclude=("generic_forum_post", "unattributed_summary"),
        action_hints=("inspect", "view_read", "cite", "export_manifest"),
        source_hints=("internet_archive_recorded", "internet_archive_placeholder", "wayback_memento_placeholder"),
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
    constraints["representation_hints"] = ["scan", "OCR", "page_range", "article_member"]
    constraints["member_discovery_hints"] = {
        "prefer_article_member": True,
        "preserve_issue_lineage": True,
    }
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="find_document_article",
        object_type="document_article",
        constraints=constraints,
        prefer=("article_member", "page_range_hit", "ocr_text_snippet"),
        exclude=("whole_issue_only_without_article_trace",),
        action_hints=("inspect", "view_read", "cite", "export_manifest"),
        source_hints=("internet_archive_placeholder",),
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
    function_hint = _infer_software_function_hint(normalized_query)
    descriptor_hint = _infer_descriptor_hint(normalized_query)
    uncertainty_notes: list[str] = []
    vague_signal = any(
        signal in normalized_query
        for signal in (
            "old ",
            "classic ",
            "blue",
            "software to",
            "fix broken registry",
            "registry repair",
            "compression",
            "disk editor",
        )
    )

    if "ftp client" in normalized_query:
        function_hint = "FTP client"
    elif "file transfer" in normalized_query:
        function_hint = "file transfer"
    elif "compression" in normalized_query:
        function_hint = "compression utility"
    elif "disk editor" in normalized_query:
        function_hint = "disk editor"
    elif "fix broken registry" in normalized_query or "registry repair" in normalized_query:
        function_hint = "registry repair"
    elif "software to" in normalized_query:
        function_hint = normalized_query.partition("software to")[2].strip()

    if function_hint is None:
        return None
    if not vague_signal:
        return None

    if not platform:
        if "windows" in normalized_query:
            constraints["platform"] = {"family": "Windows", "marketing_alias": "Windows (unspecified)"}
        elif "mac" in normalized_query:
            constraints["platform"] = {"family": "Mac", "marketing_alias": "Mac (unspecified)"}
        elif "dos" in normalized_query:
            constraints["platform"] = {"family": "DOS", "marketing_alias": "DOS"}

    constraints["function_hint"] = function_hint
    if descriptor_hint is not None:
        constraints["descriptor_hint"] = descriptor_hint
    if "old" in normalized_query or "classic" in normalized_query:
        constraints["temporal_style_hint"] = "old"
    uncertainty_notes.append("Vague identity query; exact software identity is not asserted by the planner.")
    constraints["uncertainty_notes"] = uncertainty_notes
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="identify_software",
        object_type="software",
        constraints=constraints,
        prefer=("named_software_artifact", "descriptive_release_notes", "compatibility_evidence"),
        exclude=("generic_advice_only", *OLD_PLATFORM_SOFTWARE_EXCLUDES),
        action_hints=("inspect_candidates", "compare", "search_documentation", "export_manifest"),
        source_hints=("internet_archive_recorded", "local_bundle_fixtures", "wayback_memento_placeholder"),
        planner_confidence="medium",
        planner_notes=tuple(uncertainty_notes),
    )


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
    constraints["platform_is_constraint"] = True
    constraints["target_object_hint"] = "software_for_platform"
    function_hint = _infer_software_function_hint(normalized_query)
    if function_hint is not None:
        constraints["function_hint"] = function_hint
    constraints["representation_hints"] = ["installer", "portable_package", "release_asset", "member_artifact"]
    return ResolutionTask(
        raw_query=raw_query,
        task_kind="browse_software",
        object_type="software",
        constraints=constraints,
        prefer=("direct_software_artifact", "portable_package", "compatibility_evidence"),
        exclude=OLD_PLATFORM_SOFTWARE_EXCLUDES,
        action_hints=("inspect", "fetch_if_available", "export_manifest"),
        source_hints=CURRENT_SOURCE_HINTS,
        planner_confidence="high",
        planner_notes=(
            "Recognized a platform-scoped software browsing query.",
            "The named operating system is treated as a compatibility constraint, not the requested object.",
        ),
    )


def _extract_platform_constraints(normalized_query: str) -> dict[str, Any]:
    for pattern, payload in PLATFORM_HINTS:
        if pattern.search(normalized_query):
            return {"platform": dict(payload)}
    return {}


def _apply_product_or_function_hint(
    raw_query: str,
    product_phrase: str,
    constraints: dict[str, Any],
) -> None:
    normalized_product = product_phrase.strip()
    if not normalized_product:
        return
    if normalized_product in GENERIC_PRODUCT_CLASSES:
        constraints["function_hint"] = normalized_product
        return
    constraints["product_hint"] = _restore_subject_case(raw_query, normalized_product)


def _infer_named_product_hint(raw_query: str, normalized_query: str) -> str | None:
    if "directx 9.0c" in normalized_query:
        return "DirectX 9.0c"
    if "visual c++ 6" in normalized_query or "visual c++ 6.0" in normalized_query:
        return "Visual C++ 6.0"
    if "norton" in normalized_query:
        return "Norton"
    return None


def _infer_member_type(normalized_query: str) -> str | None:
    if "driver" in normalized_query or "inf" in normalized_query:
        return "driver"
    if "installer" in normalized_query or "service pack download" in normalized_query:
        return "installer"
    if "readme" in normalized_query:
        return "readme"
    if "app inside" in normalized_query:
        return "software"
    return None


def _infer_container_hint(normalized_query: str) -> str | None:
    if "support cd" in normalized_query:
        return "support_cd"
    if "iso" in normalized_query:
        return "ISO"
    if "zip" in normalized_query:
        return "ZIP"
    if "bundle" in normalized_query:
        return "bundle"
    if "package" in normalized_query or "service pack" in normalized_query:
        return "package"
    return None


def _member_representation_hints(container_hint: str | None) -> list[str]:
    hints = ["member_path", "member_hash", "member_content_type"]
    if container_hint is not None:
        hints.append(container_hint)
    hints.extend(["parent_lineage", "member_preview"])
    return hints


def _infer_descriptor_hint(normalized_query: str) -> str | None:
    descriptors: list[str] = []
    if "blue" in normalized_query:
        descriptors.append("blue")
    if "icon" in normalized_query:
        descriptors.append("icon")
    if "globe" in normalized_query:
        descriptors.append("globe")
    return " ".join(descriptors) if descriptors else None


def _extract_hardware_hint(raw_query: str, normalized_query: str) -> str:
    hardware = normalized_query
    hardware = re.sub(r"\bdriver\b", " ", hardware)
    hardware = re.sub(r"\bfor\b", " ", hardware)
    hardware = _strip_platform_tokens(hardware)
    hardware = re.sub(r"\s+", " ", hardware).strip(" -")
    if not hardware:
        return ""
    return _restore_hardware_case(raw_query, hardware)


def _strip_platform_tokens(value: str) -> str:
    stripped = value
    for pattern, _payload in PLATFORM_HINTS:
        stripped = pattern.sub("", stripped)
    stripped = re.sub(r"\s+", " ", stripped)
    return stripped.strip(" -")


def _infer_software_function_hint(normalized_query: str) -> str | None:
    if "registry" in normalized_query and ("repair" in normalized_query or "fix" in normalized_query):
        return "registry repair"
    if "browser" in normalized_query:
        return "browser"
    if "ftp client" in normalized_query:
        return "FTP client"
    if "client" in normalized_query:
        return "client"
    if "utilities" in normalized_query or "utility" in normalized_query:
        return "utility"
    if "antivirus" in normalized_query:
        return "antivirus"
    if "compression" in normalized_query:
        return "compression utility"
    if "disk editor" in normalized_query:
        return "disk editor"
    return None


def _normalize_query(raw_query: str) -> str:
    return re.sub(r"\s+", " ", raw_query.strip()).casefold()


def _title_case_phrase(value: str) -> str:
    if not value:
        return value
    return " ".join(part.capitalize() if part.islower() else part for part in value.split())


def _restore_subject_case(raw_query: str, normalized_fragment: str) -> str:
    normalized_fragment = normalized_fragment.strip()
    if not normalized_fragment:
        return normalized_fragment
    match = re.search(re.escape(normalized_fragment), raw_query, re.IGNORECASE)
    if match is None:
        return _title_case_phrase(normalized_fragment)
    return raw_query[match.start() : match.end()].strip()


def _restore_hardware_case(raw_query: str, normalized_fragment: str) -> str:
    return _restore_subject_case(raw_query, normalized_fragment)


def _base_constraints(platform: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in platform.items()}
