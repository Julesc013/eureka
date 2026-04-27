from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import re
from typing import Any, Iterable, Mapping


CREATED_BY_SLICE = "compatibility_evidence_pack_v0"


@dataclass(frozen=True)
class PlatformRef:
    family: str
    name: str
    version: str | None = None
    marketing_alias: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {
            "family": self.family,
            "name": self.name,
        }
        if self.version is not None:
            payload["version"] = self.version
        if self.marketing_alias is not None:
            payload["marketing_alias"] = self.marketing_alias
        return payload


@dataclass(frozen=True)
class CompatibilityEvidenceRecord:
    evidence_id: str
    subject_target_ref: str
    source_id: str | None
    source_family: str
    source_label: str | None
    evidence_kind: str
    claim_type: str
    platform: PlatformRef | None
    architecture: str
    confidence: str
    evidence_text: str | None
    locator: str
    subject_resolved_resource_id: str | None = None
    created_by_slice: str = CREATED_BY_SLICE

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "evidence_id": self.evidence_id,
            "subject_target_ref": self.subject_target_ref,
            "source_family": self.source_family,
            "evidence_kind": self.evidence_kind,
            "claim_type": self.claim_type,
            "architecture": self.architecture,
            "confidence": self.confidence,
            "locator": self.locator,
            "created_by_slice": self.created_by_slice,
        }
        if self.subject_resolved_resource_id is not None:
            payload["subject_resolved_resource_id"] = self.subject_resolved_resource_id
        if self.source_id is not None:
            payload["source_id"] = self.source_id
        if self.source_label is not None:
            payload["source_label"] = self.source_label
        if self.platform is not None:
            payload["platform"] = self.platform.to_dict()
        if self.evidence_text is not None:
            payload["evidence_text"] = self.evidence_text
        return payload


@dataclass(frozen=True)
class CompatibilityEvidenceVerdict:
    target_ref: str
    verdict: str
    evidence_records: tuple[CompatibilityEvidenceRecord, ...] = ()
    reasons: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "fixture evidence only",
        "no install or runtime execution was performed",
    )
    created_by_slice: str = CREATED_BY_SLICE

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_ref": self.target_ref,
            "verdict": self.verdict,
            "evidence_records": [record.to_dict() for record in self.evidence_records],
            "reasons": list(self.reasons),
            "limitations": list(self.limitations),
            "created_by_slice": self.created_by_slice,
        }


def normalize_platform(value: str) -> PlatformRef | None:
    normalized = re.sub(r"[^a-z0-9.]+", " ", value.casefold()).strip()
    if not normalized:
        return None
    for patterns, platform in _PLATFORM_ALIASES:
        if any(pattern in normalized for pattern in patterns):
            return platform
    return None


def attach_compatibility_evidence(record: Any) -> Any:
    evidence_records = extract_compatibility_evidence(record)
    return replace(record, compatibility_evidence=evidence_records)


def extract_compatibility_evidence(record: Any) -> tuple[CompatibilityEvidenceRecord, ...]:
    items: list[CompatibilityEvidenceRecord] = []
    target_ref = _text(record, "target_ref") or ""
    source_family = _text(record, "source_family") or "unknown"
    source_label = _text(record, "source_family_label")
    source_id = _source_id(source_family)
    subject_resolved_resource_id = _text(record, "object_id")
    member_path = _text(record, "member_path")
    member_kind = _text(record, "member_kind")

    if member_path:
        items.extend(
            _records_from_text(
                record,
                text=member_path,
                evidence_kind="file_path",
                locator=member_path,
                preferred_claim_type=_claim_type_for_member(member_path, member_kind),
                confidence="medium" if _looks_specific(member_path) else "low",
            )
        )

    for evidence in _iter_evidence(record):
        claim_kind = _text(evidence, "claim_kind") or "unknown"
        claim_value = _text(evidence, "claim_value") or ""
        evidence_kind = _text(evidence, "evidence_kind") or "unknown"
        locator = _text(evidence, "evidence_locator") or member_path or target_ref
        if not _could_contain_compatibility(claim_kind, claim_value, evidence_kind, locator):
            continue
        items.extend(
            _records_from_text(
                record,
                text=claim_value,
                evidence_kind=_compatibility_evidence_kind(claim_kind, evidence_kind),
                locator=locator,
                preferred_claim_type=_claim_type_for_evidence(
                    claim_kind,
                    evidence_kind,
                    claim_value,
                    member_kind,
                ),
                confidence=_confidence_for_evidence(claim_kind, evidence_kind, claim_value),
            )
        )

    unique: dict[tuple[str, str, str, str], CompatibilityEvidenceRecord] = {}
    for item in items:
        platform_name = item.platform.name if item.platform is not None else "unknown"
        key = (item.locator, item.claim_type, platform_name, item.evidence_kind)
        unique.setdefault(key, item)
    return tuple(sorted(unique.values(), key=lambda item: item.evidence_id))


def compatibility_evidence_verdict(record: Any) -> CompatibilityEvidenceVerdict:
    evidence_records = tuple(_evidence_records(record))
    target_ref = _text(record, "target_ref") or ""
    if not evidence_records:
        return CompatibilityEvidenceVerdict(
            target_ref=target_ref,
            verdict="unknown",
            reasons=("no_source_backed_compatibility_evidence",),
        )
    if any(item.claim_type == "does_not_work_on" for item in evidence_records):
        return CompatibilityEvidenceVerdict(
            target_ref=target_ref,
            verdict="incompatible",
            evidence_records=evidence_records,
            reasons=("incompatible_evidence_present",),
        )
    non_documentation = tuple(
        item
        for item in evidence_records
        if item.claim_type not in {"documentation_for_platform", "mentions_platform"}
        and item.evidence_kind not in {"manual", "readme"}
    )
    if non_documentation:
        return CompatibilityEvidenceVerdict(
            target_ref=target_ref,
            verdict="partial",
            evidence_records=evidence_records,
            reasons=("source_backed_compatibility_evidence_present",),
        )
    return CompatibilityEvidenceVerdict(
        target_ref=target_ref,
        verdict="documentation_only",
        evidence_records=evidence_records,
        reasons=("documentation_only_compatibility_evidence",),
    )


def compatibility_evidence_payloads(records: Iterable[CompatibilityEvidenceRecord]) -> tuple[dict[str, Any], ...]:
    return tuple(record.to_dict() for record in records)


def compatibility_summary(records: Iterable[CompatibilityEvidenceRecord]) -> str | None:
    evidence_records = tuple(records)
    if not evidence_records:
        return None
    parts: list[str] = []
    for item in evidence_records[:3]:
        platform = item.platform.name if item.platform is not None else "unknown platform"
        parts.append(f"{platform}: {item.claim_type} via {item.evidence_kind} ({item.confidence})")
    if len(evidence_records) > 3:
        parts.append(f"+{len(evidence_records) - 3} more")
    return "; ".join(parts)


def _records_from_text(
    record: Any,
    *,
    text: str,
    evidence_kind: str,
    locator: str,
    preferred_claim_type: str,
    confidence: str,
) -> tuple[CompatibilityEvidenceRecord, ...]:
    platforms = _platforms_in_text(text)
    if not platforms:
        return ()
    architecture = _architecture_in_text(text)
    records: list[CompatibilityEvidenceRecord] = []
    for platform in platforms:
        claim_type = preferred_claim_type
        if claim_type == "unknown":
            claim_type = "supports_platform" if "compat" in text.casefold() else "mentions_platform"
        records.append(
            CompatibilityEvidenceRecord(
                evidence_id=_evidence_id(
                    _text(record, "target_ref") or "",
                    locator,
                    evidence_kind,
                    platform.name,
                    claim_type,
                ),
                subject_target_ref=_text(record, "target_ref") or "",
                subject_resolved_resource_id=_text(record, "object_id"),
                source_id=_source_id(_text(record, "source_family") or "unknown"),
                source_family=_text(record, "source_family") or "unknown",
                source_label=_text(record, "source_family_label"),
                evidence_kind=evidence_kind,
                claim_type=claim_type,
                platform=platform,
                architecture=architecture,
                confidence=confidence,
                evidence_text=_snippet(text),
                locator=locator,
            )
        )
    return tuple(records)


def _platforms_in_text(text: str) -> tuple[PlatformRef, ...]:
    seen: set[str] = set()
    platforms: list[PlatformRef] = []
    for token in _candidate_windows_tokens(text):
        platform = normalize_platform(token)
        if platform is not None and platform.name not in seen:
            platforms.append(platform)
            seen.add(platform.name)
    normalized = text.casefold()
    for _, platform in _PLATFORM_ALIASES:
        if platform.name in seen:
            continue
        if any(pattern in normalized for pattern in _patterns_for_platform(platform)):
            platforms.append(platform)
            seen.add(platform.name)
    return tuple(platforms)


def _candidate_windows_tokens(text: str) -> tuple[str, ...]:
    normalized = text.replace("_", " ").replace("-", " ")
    matches = re.findall(
        r"windows\s*(?:nt\s*)?(?:95|98|2000|xp|vista|7|5\.0|5\.1|6\.0|6\.1)",
        normalized,
        flags=re.I,
    )
    matches.extend(re.findall(r"win(?:95|98|2k|xp|vista|7|2000)", normalized, flags=re.I))
    matches.extend(re.findall(r"mac\s*os\s*(?:9|x\s*10\.4|x\s*10\.6)", normalized, flags=re.I))
    matches.extend(re.findall(r"(?:tiger|snow leopard|powerpc)", normalized, flags=re.I))
    return tuple(matches)


def _patterns_for_platform(platform: PlatformRef) -> tuple[str, ...]:
    return next(patterns for patterns, candidate in _PLATFORM_ALIASES if candidate == platform)


def _architecture_in_text(text: str) -> str:
    normalized = text.casefold()
    if "powerpc" in normalized or re.search(r"\bppc\b", normalized):
        return "ppc"
    if "x86_64" in normalized or "x64" in normalized or "amd64" in normalized:
        return "x64"
    if re.search(r"\bx86\b", normalized) or "win2000" in normalized or "windows 2000" in normalized:
        return "x86"
    return "unknown"


def _claim_type_for_member(member_path: str, member_kind: str | None) -> str:
    value = member_path.casefold()
    if member_kind == "driver" or "driver" in value or value.endswith(".inf"):
        return "driver_for_hardware"
    if member_kind in {"readme", "documentation", "compatibility_note"}:
        return "documentation_for_platform"
    if member_kind in {"utility", "installer_like"}:
        return "supports_platform"
    return "mentions_platform"


def _claim_type_for_evidence(
    claim_kind: str,
    evidence_kind: str,
    claim_value: str,
    member_kind: str | None,
) -> str:
    value = " ".join((claim_kind, evidence_kind, claim_value, member_kind or "")).casefold()
    if "does not work" in value or "not compatible" in value or "unsupported on" in value:
        return "does_not_work_on"
    if "driver" in value and ("thinkpad" in value or "wifi" in value or "wireless" in value):
        return "driver_for_hardware"
    if "readme" in value or "manual" in value or "documentation" in value:
        return "documentation_for_platform"
    if "required" in value or "requires" in value:
        return "requires"
    if "compatibility" in value or "platform" in value:
        return "supports_platform"
    return "mentions_platform"


def _compatibility_evidence_kind(claim_kind: str, evidence_kind: str) -> str:
    value = " ".join((claim_kind, evidence_kind)).casefold()
    if "compatibility_note" in value:
        return "compatibility_note"
    if "readme" in value:
        return "readme"
    if "manual" in value:
        return "manual"
    if "release" in value:
        return "release_notes"
    if "source_metadata" in value:
        return "source_metadata"
    if "file_listing" in value or "member_listing" in value:
        return "file_path"
    return evidence_kind if evidence_kind else "unknown"


def _confidence_for_evidence(claim_kind: str, evidence_kind: str, claim_value: str) -> str:
    value = " ".join((claim_kind, evidence_kind, claim_value)).casefold()
    if "compatibility_note" in value or "source_metadata" in value:
        return "medium"
    if "readme" in value or "release" in value:
        return "medium"
    if "windows" in value or "win" in value or "mac os" in value:
        return "low"
    return "unknown"


def _could_contain_compatibility(
    claim_kind: str,
    claim_value: str,
    evidence_kind: str,
    locator: str,
) -> bool:
    haystack = " ".join((claim_kind, claim_value, evidence_kind, locator)).casefold()
    return any(
        token in haystack
        for token in (
            "windows",
            "win2000",
            "winxp",
            "win7",
            "win98",
            "win95",
            "winvista",
            "nt 5.0",
            "nt 5.1",
            "nt 6.0",
            "nt 6.1",
            "vista",
            "mac os",
            "powerpc",
            "tiger",
            "snow leopard",
            "compatibility",
            "platform",
            "thinkpad",
        )
    )


def _looks_specific(text: str) -> bool:
    value = text.casefold()
    return any(token in value for token in ("windows2000", "windows7", "win2000", "win7", "thinkpad", "driver"))


def _evidence_records(record: Any) -> tuple[CompatibilityEvidenceRecord, ...]:
    value = getattr(record, "compatibility_evidence", ())
    if isinstance(value, tuple):
        return tuple(item for item in value if isinstance(item, CompatibilityEvidenceRecord))
    return ()


def _iter_evidence(record: Any) -> tuple[Any, ...]:
    value = getattr(record, "evidence", ())
    if isinstance(value, tuple):
        return value
    return ()


def _text(value: Any, name: str) -> str | None:
    if isinstance(value, Mapping):
        item = value.get(name)
    else:
        item = getattr(value, name, None)
    if isinstance(item, str) and item:
        return item
    return None


def _source_id(source_family: str) -> str | None:
    return {
        "article_scan_recorded": "article-scan-recorded-fixtures",
        "synthetic_fixture": "synthetic-fixtures",
        "github_releases": "github-releases-recorded-fixtures",
        "internet_archive_recorded": "internet-archive-recorded-fixtures",
        "local_bundle_fixtures": "local-bundle-fixtures",
    }.get(source_family)


def _evidence_id(
    target_ref: str,
    locator: str,
    evidence_kind: str,
    platform_name: str,
    claim_type: str,
) -> str:
    digest = hashlib.sha256(
        "\n".join((target_ref, locator, evidence_kind, platform_name, claim_type)).encode("utf-8")
    ).hexdigest()
    return f"compat-evidence:sha256:{digest}"


def _snippet(value: str) -> str | None:
    normalized = " ".join(value.split())
    if not normalized:
        return None
    if len(normalized) <= 240:
        return normalized
    return normalized[:240]


_PLATFORM_ALIASES: tuple[tuple[tuple[str, ...], PlatformRef], ...] = (
    (("windows 7", "windows7", "windows nt 6.1", "nt 6.1", "win7"), PlatformRef("windows", "Windows 7", "NT 6.1", "Windows 7")),
    (("windows vista", "windowsvista", "windows nt 6.0", "nt 6.0", "vista", "winvista"), PlatformRef("windows", "Windows Vista", "NT 6.0", "Windows Vista")),
    (("windows xp", "windowsxp", "windows nt 5.1", "nt 5.1", "winxp"), PlatformRef("windows", "Windows XP", "NT 5.1", "Windows XP")),
    (("windows 2000", "windows2000", "windows nt 5.0", "nt 5.0", "win2000", "win2k"), PlatformRef("windows", "Windows 2000", "NT 5.0", "Windows 2000")),
    (("windows 98", "windows98", "win98"), PlatformRef("windows", "Windows 98", None, "Windows 98")),
    (("windows 95", "windows95", "win95"), PlatformRef("windows", "Windows 95", None, "Windows 95")),
    (("mac os 9", "classic mac os"), PlatformRef("macos", "Mac OS 9", None, "Mac OS 9")),
    (("mac os x 10.4", "tiger", "powerpc"), PlatformRef("macos", "Mac OS X 10.4", "10.4", "Tiger")),
    (("mac os x 10.6", "snow leopard"), PlatformRef("macos", "Mac OS X 10.6", "10.6", "Snow Leopard")),
)
