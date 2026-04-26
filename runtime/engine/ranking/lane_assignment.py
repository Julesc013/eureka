from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from runtime.engine.ranking.result_lane import (
    BEST_DIRECT_ANSWER,
    COMMUNITY,
    DOCUMENTATION,
    INSIDE_BUNDLES,
    INSTALLABLE_OR_USABLE_NOW,
    MENTIONS_OR_TRACES,
    OTHER,
    PRESERVATION,
)


@dataclass(frozen=True)
class ResultUsefulnessSummary:
    result_lanes: tuple[str, ...]
    primary_lane: str
    user_cost_score: int
    user_cost_reasons: tuple[str, ...]
    usefulness_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_lanes": list(self.result_lanes),
            "primary_lane": self.primary_lane,
            "user_cost_score": self.user_cost_score,
            "user_cost_reasons": list(self.user_cost_reasons),
            "usefulness_summary": self.usefulness_summary,
        }


def assign_result_usefulness(
    record: Any,
    *,
    suppression_hints: tuple[str, ...] = (),
) -> ResultUsefulnessSummary:
    fields = _RecordFields(record)
    lanes: list[str] = []
    reasons: list[str] = []
    score = 9

    if _is_os_media_suppressed(fields, suppression_hints):
        lanes.append(OTHER)
        reasons.extend(("os_media_suppressed_for_app_intent", "wrong_object_type"))
        return _summary(lanes, 8, reasons)

    record_kind = fields.text("record_kind")
    member_kind = fields.text("member_kind")
    source_family = fields.text("source_family")
    representation_kind = fields.text("representation_kind")

    if record_kind == "synthetic_member":
        lanes.append(INSIDE_BUNDLES)
        if fields.text("parent_target_ref") or fields.text("parent_representation_id"):
            reasons.append("inner_member_has_parent_lineage")
        if fields.text("member_path"):
            reasons.append("member_has_path")
        if fields.sequence("action_hints"):
            reasons.append("action_available")
            if _has_preview_or_readback(fields.sequence("action_hints")):
                reasons.append("member_has_preview_or_readback_action")
        if fields.sequence("evidence"):
            reasons.append("source_evidence_present")
        if _has_compatibility_evidence(fields):
            reasons.append("compatibility_evidence_present")
            if member_kind == "driver" and _has_claim_type(fields, "driver_for_hardware"):
                reasons.append("driver_platform_match")
            if _has_documentation_only_compatibility(fields):
                reasons.append("documentation_only_compatibility_evidence")
        elif _has_compatibility_hint(fields):
            reasons.append("compatibility_hint_present")
        if member_kind in {"readme", "documentation", "compatibility_note", "manifest"}:
            lanes.append(DOCUMENTATION)
            reasons.append("documentation_only")
            score = 5
        elif member_kind in {"driver", "utility", "installer_like"}:
            lanes.extend((BEST_DIRECT_ANSWER, INSTALLABLE_OR_USABLE_NOW))
            score = 1
        else:
            score = 2
        return _summary(lanes, score, reasons)

    if record_kind == "member":
        lanes.append(INSIDE_BUNDLES)
        if fields.text("member_path"):
            reasons.append("member_has_path")
        reasons.append("member_listing_only")
        return _summary(lanes, 2, reasons)

    if record_kind == "representation":
        if _looks_like_bundle_or_media(fields, representation_kind):
            lanes.extend((INSIDE_BUNDLES, PRESERVATION))
            reasons.append("parent_bundle_context_only")
            return _summary(lanes, 3, reasons)
        lanes.append(INSTALLABLE_OR_USABLE_NOW)
        reasons.append("direct_representation_present")
        if fields.sequence("evidence"):
            reasons.append("source_evidence_present")
        return _summary(lanes, 2, reasons)

    if record_kind == "resolved_object":
        if source_family == "local_bundle_fixtures":
            lanes.extend((INSIDE_BUNDLES, PRESERVATION))
            reasons.append("parent_bundle_context_only")
            if fields.sequence("evidence"):
                reasons.append("source_evidence_present")
            return _summary(lanes, 4, reasons)
        if source_family == "internet_archive_recorded":
            lanes.append(PRESERVATION)
            reasons.append("preservation_source")
            if fields.sequence("evidence"):
                reasons.append("source_evidence_present")
            return _summary(lanes, 3, reasons)
        if source_family == "github_releases":
            lanes.extend((COMMUNITY, INSTALLABLE_OR_USABLE_NOW))
            reasons.append("community_release_source")
            if fields.sequence("evidence"):
                reasons.append("source_evidence_present")
            return _summary(lanes, 2, reasons)
        lanes.append(INSTALLABLE_OR_USABLE_NOW)
        if fields.sequence("evidence"):
            reasons.append("source_evidence_present")
        return _summary(lanes, 2, reasons or ["direct_bounded_record"])

    if record_kind == "evidence":
        lanes.append(MENTIONS_OR_TRACES)
        reasons.append("mention_only")
        if fields.sequence("evidence"):
            reasons.append("source_evidence_present")
        return _summary(lanes, 6, reasons)

    if record_kind == "source_record":
        lanes.append(OTHER)
        reasons.append("source_inventory_record")
        return _summary(lanes, 9, reasons)

    if source_family == "internet_archive_recorded":
        lanes.append(PRESERVATION)
        reasons.append("preservation_source")
        score = 4
    elif source_family == "github_releases":
        lanes.append(COMMUNITY)
        reasons.append("community_release_source")
        score = 4
    elif fields.sequence("evidence"):
        lanes.append(MENTIONS_OR_TRACES)
        reasons.append("source_evidence_present")
        score = 6
    else:
        lanes.append(OTHER)
        reasons.append("compatibility_unknown")
    return _summary(lanes, score, reasons)


class _RecordFields:
    def __init__(self, value: Any) -> None:
        self._value = value

    def text(self, name: str) -> str | None:
        value = self._get(name)
        if isinstance(value, str) and value:
            return value
        return None

    def sequence(self, name: str) -> tuple[str, ...]:
        value = self._get(name)
        if isinstance(value, (list, tuple)):
            return tuple(str(item) for item in value if isinstance(item, str) and item)
        return ()

    def mapping_sequence(self, name: str) -> tuple[Mapping[str, Any], ...]:
        value = self._get(name)
        if isinstance(value, (list, tuple)):
            mappings: list[Mapping[str, Any]] = []
            for item in value:
                if isinstance(item, Mapping):
                    mappings.append(item)
                elif hasattr(item, "to_dict"):
                    payload = item.to_dict()
                    if isinstance(payload, Mapping):
                        mappings.append(payload)
            return tuple(mappings)
        return ()

    def _get(self, name: str) -> Any:
        if isinstance(self._value, Mapping):
            return self._value.get(name)
        return getattr(self._value, name, None)


def _summary(
    lanes: list[str],
    score: int,
    reasons: list[str],
) -> ResultUsefulnessSummary:
    unique_lanes = _unique(lanes) or (OTHER,)
    unique_reasons = _unique(reasons) or ("compatibility_unknown",)
    primary_lane = unique_lanes[0]
    return ResultUsefulnessSummary(
        result_lanes=unique_lanes,
        primary_lane=primary_lane,
        user_cost_score=score,
        user_cost_reasons=unique_reasons,
        usefulness_summary=(
            f"{_lane_label(primary_lane)}; user cost {score}; "
            f"why: {'; '.join(unique_reasons)}"
        ),
    )


def _unique(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            ordered.append(value)
            seen.add(value)
    return tuple(ordered)


def _lane_label(value: str) -> str:
    return value.replace("_", " ")


def _has_preview_or_readback(action_hints: tuple[str, ...]) -> bool:
    return any(item in {"read_member", "preview_member"} for item in action_hints)


def _has_compatibility_hint(fields: _RecordFields) -> bool:
    haystack = " ".join(
        item
        for item in (
            fields.text("label"),
            fields.text("summary"),
            fields.text("member_path"),
            fields.text("content_text"),
            " ".join(fields.sequence("evidence")),
        )
        if item
    ).casefold()
    return any(token in haystack for token in ("windows", "win", "mac os", "compatibility", "nt "))


def _has_compatibility_evidence(fields: _RecordFields) -> bool:
    return bool(fields.mapping_sequence("compatibility_evidence"))


def _has_claim_type(fields: _RecordFields, claim_type: str) -> bool:
    return any(item.get("claim_type") == claim_type for item in fields.mapping_sequence("compatibility_evidence"))


def _has_documentation_only_compatibility(fields: _RecordFields) -> bool:
    evidence_records = fields.mapping_sequence("compatibility_evidence")
    if not evidence_records:
        return False
    return all(
        item.get("claim_type") == "documentation_for_platform"
        or item.get("evidence_kind") in {"readme", "manual", "compatibility_note"}
        for item in evidence_records
    )


def _is_os_media_suppressed(fields: _RecordFields, suppression_hints: tuple[str, ...]) -> bool:
    normalized_hints = {hint.casefold() for hint in suppression_hints}
    if not (
        "operating_system_image" in normalized_hints
        or "os iso" in normalized_hints
        or "os_media" in normalized_hints
    ):
        return False
    return _looks_like_os_media(fields)


def _looks_like_os_media(fields: _RecordFields) -> bool:
    haystack = " ".join(
        item
        for item in (
            fields.text("label"),
            fields.text("summary"),
            fields.text("target_ref"),
            fields.text("representation_id"),
            fields.text("record_kind"),
            fields.text("object_kind"),
        )
        if item
    ).casefold()
    return any(token in haystack for token in ("operating system", "os image", "os iso", "windows 7 iso", "install media"))


def _looks_like_bundle_or_media(fields: _RecordFields, representation_kind: str | None) -> bool:
    haystack = " ".join(
        item
        for item in (
            representation_kind,
            fields.text("label"),
            fields.text("summary"),
            fields.text("representation_id"),
            fields.text("media_type"),
        )
        if item
    ).casefold()
    return any(token in haystack for token in ("bundle", "archive", "zip", "iso", "support cd", "fixture_archive"))
