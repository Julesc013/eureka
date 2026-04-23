from __future__ import annotations

from dataclasses import replace

from runtime.engine.compatibility import CompatibilityReason, HostProfile
from runtime.engine.compatibility.service import DeterministicCompatibilityService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.handoff.representation_selection import RepresentationSelectionEntry
from runtime.engine.interfaces.public.compatibility import CompatibilityRequest
from runtime.engine.interfaces.public.representation_selection import (
    RepresentationSelectionRequest,
    RepresentationSelectionResult,
)
from runtime.engine.interfaces.public.representations import RepresentationsRequest
from runtime.engine.interfaces.public.resolution import Notice, ResolutionRequest
from runtime.engine.interfaces.service import (
    CompatibilityService,
    RepresentationSelectionService,
    RepresentationsService,
    ResolutionService,
)
from runtime.engine.representations import RepresentationSummary
from runtime.engine.representations.service import DeterministicRepresentationsService
from runtime.engine.resolve import ExactMatchResolutionService
from runtime.engine.strategy import StrategyProfile, resolve_bootstrap_strategy_profile


class DeterministicRepresentationSelectionService(RepresentationSelectionService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        *,
        resolution_service: ResolutionService | None = None,
        representations_service: RepresentationsService | None = None,
        compatibility_service: CompatibilityService | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)
        self._representations_service = representations_service or DeterministicRepresentationsService(
            catalog,
            resolution_service=self._resolution_service,
        )
        self._compatibility_service = compatibility_service or DeterministicCompatibilityService(
            catalog,
            resolution_service=self._resolution_service,
        )

    def select_representation(
        self,
        request: RepresentationSelectionRequest,
    ) -> RepresentationSelectionResult:
        strategy_profile = resolve_bootstrap_strategy_profile(request.strategy_id)
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
        if outcome.status != "completed" or outcome.result is None:
            return RepresentationSelectionResult(
                status="blocked",
                target_ref=request.target_ref,
                strategy_profile=strategy_profile,
                notices=outcome.notices,
            )

        representations_result = self._representations_service.list_representations(
            RepresentationsRequest.from_parts(request.target_ref)
        )
        if representations_result.status != "available":
            return RepresentationSelectionResult(
                status="blocked",
                target_ref=request.target_ref,
                resolved_resource_id=outcome.result.resolved_resource_id,
                primary_object=outcome.result.primary_object,
                source=outcome.result.source,
                evidence=outcome.result.evidence,
                strategy_profile=strategy_profile,
                notices=representations_result.notices,
            )

        host_profile = None
        compatibility_status = None
        compatibility_reasons: tuple[CompatibilityReason, ...] = ()
        if request.host_profile_id is not None:
            compatibility = self._compatibility_service.evaluate_compatibility(
                CompatibilityRequest.from_parts(request.target_ref, request.host_profile_id)
            )
            host_profile = compatibility.host_profile
            if compatibility.status != "evaluated":
                return RepresentationSelectionResult(
                    status="blocked",
                    target_ref=request.target_ref,
                    resolved_resource_id=outcome.result.resolved_resource_id,
                    primary_object=outcome.result.primary_object,
                    source=outcome.result.source,
                    evidence=outcome.result.evidence,
                    strategy_profile=strategy_profile,
                    host_profile=host_profile,
                    notices=compatibility.notices,
                )
            compatibility_status = compatibility.compatibility_status
            compatibility_reasons = compatibility.reasons

        entries = tuple(
            _entry_from_representation(
                representation,
                strategy_profile=strategy_profile,
                host_profile=host_profile,
                compatibility_status=compatibility_status,
            )
            for representation in representations_result.representations
        )
        preferred_representation_id, adjusted_entries = _promote_preferred_representation(
            entries,
            strategy_profile=strategy_profile,
            host_profile=host_profile,
        )
        return RepresentationSelectionResult(
            status="available",
            target_ref=request.target_ref,
            resolved_resource_id=outcome.result.resolved_resource_id,
            primary_object=outcome.result.primary_object,
            source=outcome.result.source,
            evidence=outcome.result.evidence,
            strategy_profile=strategy_profile,
            host_profile=host_profile,
            compatibility_status=compatibility_status,
            compatibility_reasons=compatibility_reasons,
            preferred_representation_id=preferred_representation_id,
            selections=adjusted_entries,
            notices=outcome.result.notices,
        )


def _entry_from_representation(
    representation: RepresentationSummary,
    *,
    strategy_profile: StrategyProfile,
    host_profile: HostProfile | None,
    compatibility_status: str | None,
) -> RepresentationSelectionEntry:
    status = "available"
    reason_codes = ["representation_available"]
    reason_messages = [
        "This bounded representation remains available for inspection or manual follow-on work."
    ]
    if _is_payload_representation(representation):
        if compatibility_status == "incompatible":
            status = "unsuitable"
            reason_codes = ["host_incompatible_for_payload_representation"]
            reason_messages = [
                "The current host profile is incompatible with this target, so this payload-like representation is not a suitable bounded fit now."
            ]
        elif compatibility_status == "unknown":
            status = "unknown"
            reason_codes = ["compatibility_unknown_for_payload_representation"]
            reason_messages = [
                "The current host profile does not yield a decisive compatibility verdict, so this payload-like representation remains explicitly unknown."
            ]
        elif host_profile is not None and _has_host_hints(representation):
            if _representation_matches_host_hint(representation, host_profile):
                reason_codes = ["representation_matches_host_hint"]
                reason_messages = [
                    "The bounded host hint inferred from this representation matches the selected host profile."
                ]
            else:
                status = "unsuitable"
                reason_codes = ["representation_host_hint_mismatch"]
                reason_messages = [
                    "The bounded host hint inferred from this representation does not match the selected host profile."
                ]
        elif host_profile is None:
            reason_codes = ["payload_representation_without_host_profile"]
            reason_messages = [
                "No host profile was supplied, so this payload-like representation remains available without a stronger suitability claim."
            ]
    elif _is_metadata_representation(representation):
        if strategy_profile.strategy_id == "preserve" and _is_checksum_representation(representation):
            reason_codes = ["preservation_sidecar_available"]
            reason_messages = [
                "This bounded checksum-like representation remains available as a preservation-oriented sidecar."
            ]
        else:
            reason_codes = ["metadata_representation_available"]
            reason_messages = [
                "This bounded metadata-like representation remains available for inspection and explanation."
            ]

    return RepresentationSelectionEntry(
        representation_id=representation.representation_id,
        representation_kind=representation.representation_kind,
        label=representation.label,
        selection_status=status,
        reason_codes=tuple(reason_codes),
        reason_messages=tuple(reason_messages),
        source_family=representation.source_family,
        source_label=representation.source_label,
        source_locator=representation.source_locator,
        access_kind=representation.access_kind,
        access_locator=representation.access_locator,
        content_type=representation.content_type,
        byte_length=representation.byte_length,
        is_direct=representation.is_direct,
        host_profile_id=host_profile.host_profile_id if host_profile is not None else None,
        strategy_id=strategy_profile.strategy_id,
    )


def _promote_preferred_representation(
    entries: tuple[RepresentationSelectionEntry, ...],
    *,
    strategy_profile: StrategyProfile,
    host_profile: HostProfile | None,
) -> tuple[str | None, tuple[RepresentationSelectionEntry, ...]]:
    available_entries = [
        entry for entry in entries if entry.selection_status == "available"
    ]
    if not available_entries:
        return None, entries

    preferred_entry = min(
        available_entries,
        key=lambda entry: _preference_rank(entry, strategy_profile, host_profile),
    )
    preferred_reason_code, preferred_reason_message = _preferred_reason(
        preferred_entry,
        strategy_profile,
        host_profile,
    )
    adjusted_entries = tuple(
        replace(
            entry,
            selection_status="preferred",
            reason_codes=(preferred_reason_code, *entry.reason_codes),
            reason_messages=(preferred_reason_message, *entry.reason_messages),
        )
        if entry.representation_id == preferred_entry.representation_id
        else entry
        for entry in entries
    )
    return preferred_entry.representation_id, adjusted_entries


def _preference_rank(
    entry: RepresentationSelectionEntry,
    strategy_profile: StrategyProfile,
    host_profile: HostProfile | None,
) -> tuple[int, int, int, str]:
    label = entry.label.casefold()
    if strategy_profile.strategy_id == "inspect":
        return (
            0 if _entry_is_view_or_inspect(entry) else 1,
            0 if not entry.is_direct else 1,
            0 if _entry_is_metadata_like(entry) else 1,
            entry.representation_id,
        )
    if strategy_profile.strategy_id == "preserve":
        return (
            0 if _entry_is_checksum_like(entry) else 1,
            0 if _entry_is_metadata_like(entry) else 1,
            0 if _entry_is_view_or_inspect(entry) else 1,
            entry.representation_id,
        )
    if strategy_profile.strategy_id == "acquire":
        return (
            0 if _entry_is_payload_like(entry) else 1,
            0 if host_profile is not None and _entry_matches_host_hint(entry, host_profile) else 1,
            0 if entry.is_direct else 1,
            entry.representation_id,
        )
    if strategy_profile.strategy_id == "compare":
        return (
            0 if _entry_is_view_or_inspect(entry) else 1,
            0 if _entry_is_metadata_like(entry) else 1,
            0 if not entry.is_direct else 1,
            label,
        )
    return (1, 1, 1, entry.representation_id)


def _preferred_reason(
    entry: RepresentationSelectionEntry,
    strategy_profile: StrategyProfile,
    host_profile: HostProfile | None,
) -> tuple[str, str]:
    if strategy_profile.strategy_id == "inspect":
        return (
            "strategy_inspect_prefers_metadata_review",
            "The active inspect strategy prefers a bounded metadata-like representation for source review before any more direct handoff.",
        )
    if strategy_profile.strategy_id == "preserve":
        if _entry_is_checksum_like(entry):
            return (
                "strategy_preserve_prefers_preservation_sidecar",
                "The active preserve strategy prefers a checksum-like preservation sidecar when one is known.",
            )
        return (
            "strategy_preserve_prefers_reviewable_representation",
            "The active preserve strategy prefers a reviewable bounded representation before any more direct path.",
        )
    if strategy_profile.strategy_id == "acquire":
        if (
            _entry_is_payload_like(entry)
            and host_profile is not None
            and _entry_matches_host_hint(entry, host_profile)
        ):
            return (
                "strategy_acquire_prefers_host_fit_payload",
                "The active acquire strategy prefers the bounded payload representation that best fits the selected host profile.",
            )
        if _entry_is_payload_like(entry):
            return (
                "strategy_acquire_prefers_direct_payload",
                "The active acquire strategy prefers the most direct bounded payload representation currently available.",
            )
        return (
            "strategy_acquire_falls_back_to_reviewable_representation",
            "No stronger bounded payload fit is currently available, so the acquire strategy falls back to a reviewable representation without implying execution.",
        )
    if strategy_profile.strategy_id == "compare":
        return (
            "strategy_compare_prefers_reviewable_representation",
            "The active compare strategy prefers a reviewable bounded representation that keeps alternatives visible.",
        )
    return (
        "preferred_representation_selected",
        "This bounded representation is the preferred fit under the current bootstrap selection rules.",
    )


def _is_metadata_representation(representation: RepresentationSummary) -> bool:
    if representation.access_kind in {"view", "inspect"}:
        return True
    return _is_checksum_representation(representation)


def _is_payload_representation(representation: RepresentationSummary) -> bool:
    return representation.is_direct and not _is_checksum_representation(representation)


def _entry_is_metadata_like(entry: RepresentationSelectionEntry) -> bool:
    if entry.access_kind in {"view", "inspect"}:
        return True
    return _entry_is_checksum_like(entry)


def _entry_is_payload_like(entry: RepresentationSelectionEntry) -> bool:
    return entry.is_direct and not _entry_is_checksum_like(entry)


def _entry_is_view_or_inspect(entry: RepresentationSelectionEntry) -> bool:
    return entry.access_kind in {"view", "inspect"}


def _is_checksum_representation(representation: RepresentationSummary) -> bool:
    label = representation.label.casefold()
    content_type = (representation.content_type or "").casefold()
    return "checksum" in label or label.endswith(".sha256") or content_type == "text/plain"


def _entry_is_checksum_like(entry: RepresentationSelectionEntry) -> bool:
    label = entry.label.casefold()
    content_type = (entry.content_type or "").casefold()
    return "checksum" in label or label.endswith(".sha256") or content_type == "text/plain"


def _has_host_hints(representation: RepresentationSummary) -> bool:
    label = representation.label.casefold()
    locator = (representation.access_locator or "").casefold()
    return any(
        token in label or token in locator
        for token in (
            "windows",
            "linux",
            "darwin",
            "macos",
            "osx",
            "amd64",
            "x86_64",
            "arm64",
            "aarch64",
        )
    )


def _representation_matches_host_hint(
    representation: RepresentationSummary,
    host_profile: HostProfile,
) -> bool:
    combined = f"{representation.label} {representation.access_locator or ''}".casefold()
    return _matches_os_hint(combined, host_profile.os_family) and _matches_arch_hint(
        combined,
        host_profile.architecture,
    )


def _entry_matches_host_hint(
    entry: RepresentationSelectionEntry,
    host_profile: HostProfile,
) -> bool:
    combined = f"{entry.label} {entry.access_locator or ''}".casefold()
    return _matches_os_hint(combined, host_profile.os_family) and _matches_arch_hint(
        combined,
        host_profile.architecture,
    )


def _matches_os_hint(value: str, os_family: str) -> bool:
    token_groups = {
        "windows": ("windows", "win32", "win64", ".msi", ".exe"),
        "linux": ("linux",),
        "macos": ("darwin", "macos", "osx", "apple"),
    }
    hints = token_groups.get(os_family, ())
    if not hints:
        return True
    other_hints = {
        token
        for family, family_hints in token_groups.items()
        if family != os_family
        for token in family_hints
    }
    if any(hint in value for hint in hints):
        return True
    return not any(hint in value for hint in other_hints)


def _matches_arch_hint(value: str, architecture: str) -> bool:
    token_groups = {
        "x86_64": ("x86_64", "amd64", "x64"),
        "arm64": ("arm64", "aarch64"),
    }
    hints = token_groups.get(architecture, ())
    if not hints:
        return True
    other_hints = {
        token
        for arch, arch_hints in token_groups.items()
        if arch != architecture
        for token in arch_hints
    }
    if any(hint in value for hint in hints):
        return True
    return not any(hint in value for hint in other_hints)
