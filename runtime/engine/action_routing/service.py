from __future__ import annotations

from runtime.engine.action_routing.action_plan import (
    ACCESS_REPRESENTATION_ACTION_ID,
    COMPARE_TARGET_ACTION_ID,
    EXPORT_RESOLUTION_BUNDLE_ACTION_ID,
    EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
    INSPECT_BUNDLE_ACTION_ID,
    INSPECT_PRIMARY_REPRESENTATION_ACTION_ID,
    LIST_SUBJECT_STATES_ACTION_ID,
    STORE_RESOLUTION_BUNDLE_ACTION_ID,
    STORE_RESOLUTION_MANIFEST_ACTION_ID,
    ActionPlanEntry,
)
from runtime.engine.compatibility import CompatibilityReason
from runtime.engine.compatibility.service import DeterministicCompatibilityService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public.action_plan import ActionPlanRequest, ActionPlanResult
from runtime.engine.interfaces.public.compatibility import CompatibilityRequest
from runtime.engine.interfaces.public.resolution import Notice, ResolutionRequest
from runtime.engine.interfaces.service import (
    ActionPlanService,
    CompatibilityService,
    ResolutionService,
)
from runtime.engine.representations import RepresentationSummary
from runtime.engine.resolve import ExactMatchResolutionService
from runtime.engine.states.subject_states import subject_key_for_target_ref
from runtime.engine.strategy import StrategyProfile, resolve_bootstrap_strategy_profile


class DeterministicActionPlanService(ActionPlanService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        *,
        resolution_service: ResolutionService | None = None,
        compatibility_service: CompatibilityService | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)
        self._compatibility_service = compatibility_service or DeterministicCompatibilityService(
            catalog,
            resolution_service=self._resolution_service,
        )

    def plan_actions(self, request: ActionPlanRequest) -> ActionPlanResult:
        strategy_profile = resolve_bootstrap_strategy_profile(request.strategy_id)
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
        if outcome.status != "completed" or outcome.result is None:
            return ActionPlanResult(
                status="blocked",
                target_ref=request.target_ref,
                strategy_profile=strategy_profile,
                strategy_rationale=_strategy_rationale(strategy_profile),
                notices=outcome.notices,
            )

        record = self._catalog.find_by_target_ref(request.target_ref)
        if record is None:
            return ActionPlanResult(
                status="blocked",
                target_ref=request.target_ref,
                evidence=outcome.result.evidence,
                strategy_profile=strategy_profile,
                strategy_rationale=_strategy_rationale(strategy_profile),
                notices=(
                    Notice(
                        code="target_ref_not_found",
                        severity="warning",
                        message=f"No bounded record matched target_ref '{request.target_ref}'.",
                    ),
                ),
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
                return ActionPlanResult(
                    status="blocked",
                    target_ref=request.target_ref,
                    resolved_resource_id=outcome.result.resolved_resource_id,
                    primary_object=outcome.result.primary_object,
                    source=outcome.result.source,
                    evidence=outcome.result.evidence,
                    strategy_profile=strategy_profile,
                    strategy_rationale=_strategy_rationale(strategy_profile),
                    host_profile=host_profile,
                    notices=compatibility.notices,
                )
            compatibility_status = compatibility.compatibility_status
            compatibility_reasons = compatibility.reasons

        subject_key = subject_key_for_target_ref(request.target_ref)
        subject_state_count = _subject_state_count(self._catalog, subject_key)
        actions = _build_action_plan_entries(
            target_ref=request.target_ref,
            representations=outcome.result.representations,
            strategy_profile=strategy_profile,
            compatibility_status=compatibility_status,
            subject_key=subject_key,
            subject_state_count=subject_state_count,
            store_actions_enabled=request.store_actions_enabled,
        )
        return ActionPlanResult(
            status="planned",
            target_ref=request.target_ref,
            resolved_resource_id=outcome.result.resolved_resource_id,
            primary_object=outcome.result.primary_object,
            source=outcome.result.source,
            evidence=outcome.result.evidence,
            strategy_profile=strategy_profile,
            strategy_rationale=_strategy_rationale(
                strategy_profile,
                subject_key=subject_key,
                subject_state_count=subject_state_count,
            ),
            host_profile=host_profile,
            compatibility_status=compatibility_status,
            compatibility_reasons=compatibility_reasons,
            actions=actions,
            notices=outcome.result.notices,
        )


def _build_action_plan_entries(
    *,
    target_ref: str,
    representations: tuple[RepresentationSummary, ...],
    strategy_profile: StrategyProfile,
    compatibility_status: str | None,
    subject_key: str | None,
    subject_state_count: int,
    store_actions_enabled: bool,
) -> tuple[ActionPlanEntry, ...]:
    inspect_representation = _select_inspection_representation(representations)
    direct_representation = _select_direct_representation(representations)

    return (
        _inspection_action_entry(inspect_representation, compatibility_status, strategy_profile),
        _direct_access_action_entry(direct_representation, compatibility_status, strategy_profile),
        _subject_states_action_entry(subject_key, subject_state_count, strategy_profile),
        _compare_target_action_entry(target_ref, subject_key, subject_state_count, strategy_profile),
        _manifest_export_action_entry(compatibility_status, strategy_profile),
        _bundle_export_action_entry(compatibility_status, strategy_profile),
        _bundle_inspection_action_entry(),
        _store_manifest_action_entry(store_actions_enabled, strategy_profile),
        _store_bundle_action_entry(store_actions_enabled, strategy_profile),
    )


def _inspection_action_entry(
    representation: RepresentationSummary | None,
    compatibility_status: str | None,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if representation is None:
        return ActionPlanEntry(
            action_id=INSPECT_PRIMARY_REPRESENTATION_ACTION_ID,
            label="Inspect a known representation",
            kind="inspect_representation",
            status="unavailable",
            reason_codes=("inspection_representation_missing",),
            reason_messages=("No bounded inspectable or viewable representation is recorded for this target.",),
        )

    if strategy_profile.strategy_id == "inspect":
        status = "recommended"
        reason_codes = ("strategy_inspect_prefers_source_inspection",)
        reason_messages = (
            "The active inspect strategy keeps bounded source inspection and evidence-aware review as the preferred next step.",
        )
    elif compatibility_status == "compatible" and representation.is_direct:
        status = "available"
        reason_codes = ("compatible_direct_representation_available",)
        reason_messages = (
            "A compatible direct representation is available, so this safer inspection path remains available.",
        )
    elif compatibility_status == "compatible":
        status = "available"
        reason_codes = ("compatible_host_inspection_available",)
        reason_messages = (
            "The host is compatible and this bounded inspection path remains available before any manual action.",
        )
    elif compatibility_status == "incompatible":
        status = "recommended"
        reason_codes = ("inspect_when_host_incompatible",)
        reason_messages = (
            "The current host profile is incompatible, so inspecting a bounded source-backed path is the safest next step.",
        )
    elif compatibility_status == "unknown":
        status = "recommended"
        reason_codes = ("inspect_when_compatibility_unknown",)
        reason_messages = (
            "Compatibility is unknown for this host, so inspecting a bounded source-backed path is recommended first.",
        )
    else:
        status = "recommended"
        reason_codes = ("inspect_before_host_specific_choice",)
        reason_messages = (
            "No host profile was supplied, so inspecting a bounded source-backed path is recommended before any host-specific choice.",
        )

    kind = "view_source_page" if representation.access_kind == "view" else "inspect_representation"
    verb = "View" if representation.access_kind == "view" else "Inspect"
    return _representation_action_entry(
        action_id=INSPECT_PRIMARY_REPRESENTATION_ACTION_ID,
        label=f"{verb} {representation.label}",
        kind=kind,
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        representation=representation,
    )


def _direct_access_action_entry(
    representation: RepresentationSummary | None,
    compatibility_status: str | None,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if representation is None:
        return ActionPlanEntry(
            action_id=ACCESS_REPRESENTATION_ACTION_ID,
            label="Access a direct representation path",
            kind="access_representation",
            status="unavailable",
            reason_codes=("direct_representation_missing",),
            reason_messages=("No bounded direct representation access path is recorded for this target.",),
        )

    if compatibility_status == "incompatible":
        status = "unavailable"
        reason_codes = ("host_incompatible_for_direct_representation",)
        reason_messages = (
            "The current host profile is incompatible, so Eureka does not recommend direct representation use in this bootstrap slice.",
        )
    elif strategy_profile.strategy_id == "acquire" and compatibility_status == "compatible":
        status = "recommended"
        reason_codes = ("strategy_acquire_prefers_direct_representation",)
        reason_messages = (
            "The active acquire strategy and current compatible host profile make the direct representation path the preferred next step.",
        )
    elif strategy_profile.strategy_id == "acquire" and compatibility_status is None:
        status = "recommended"
        reason_codes = ("strategy_acquire_prefers_direct_representation_without_host_profile",)
        reason_messages = (
            "The active acquire strategy prefers the bounded direct representation path, but no host profile was supplied for compatibility evaluation.",
        )
    elif strategy_profile.strategy_id == "acquire" and compatibility_status == "unknown":
        status = "available"
        reason_codes = ("strategy_acquire_requires_more_compatibility_confidence",)
        reason_messages = (
            "The active acquire strategy prefers direct access, but compatibility is unknown for this host, so the path remains available without being promoted.",
        )
    elif strategy_profile.strategy_id in {"inspect", "preserve", "compare"}:
        status = "available"
        reason_codes = ("strategy_deprioritizes_direct_representation",)
        reason_messages = (
            "The active strategy keeps direct representation access available, but it does not prioritize it as the next bounded step.",
        )
    elif compatibility_status == "compatible":
        status = "recommended"
        reason_codes = ("compatible_host_for_direct_representation",)
        reason_messages = (
            "The current host profile is compatible with this bounded target, so the direct representation path is recommended.",
        )
    elif compatibility_status == "unknown":
        status = "available"
        reason_codes = ("compatibility_unknown_for_direct_representation",)
        reason_messages = (
            "Compatibility is unknown for this host, so the direct representation path remains available but not recommended.",
        )
    else:
        status = "available"
        reason_codes = ("host_profile_not_provided",)
        reason_messages = (
            "No host profile was supplied, so the direct representation path remains available but not recommended.",
        )

    return _representation_action_entry(
        action_id=ACCESS_REPRESENTATION_ACTION_ID,
        label=f"Access {representation.label}",
        kind="access_representation",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        representation=representation,
    )


def _subject_states_action_entry(
    subject_key: str | None,
    subject_state_count: int,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if subject_key is None:
        return ActionPlanEntry(
            action_id=LIST_SUBJECT_STATES_ACTION_ID,
            label="List known states for this subject",
            kind="list_subject_states",
            status="unavailable",
            reason_codes=("subject_key_unavailable",),
            reason_messages=("No bounded subject key could be derived for this target.",),
        )

    if strategy_profile.strategy_id == "compare" and subject_state_count > 1:
        status = "recommended"
        reason_codes = ("strategy_compare_prefers_subject_states",)
        reason_messages = (
            "The active compare strategy prefers listing bounded subject states because multiple states are known for this subject.",
        )
    else:
        status = "available"
        reason_codes = ("subject_states_available",)
        reason_messages = (
            f"A bounded subject-state listing is available for subject '{subject_key}' with {subject_state_count} known state(s).",
        )
    return ActionPlanEntry(
        action_id=LIST_SUBJECT_STATES_ACTION_ID,
        label=f"List known states for {subject_key}",
        kind="list_subject_states",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        parameter_hint=f"subject_key={subject_key}",
        subject_key=subject_key,
    )


def _compare_target_action_entry(
    target_ref: str,
    subject_key: str | None,
    subject_state_count: int,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if subject_key is None:
        return ActionPlanEntry(
            action_id=COMPARE_TARGET_ACTION_ID,
            label="Compare this target with another bounded target",
            kind="compare_target",
            status="unavailable",
            reason_codes=("comparison_subject_context_missing",),
            reason_messages=("No bounded subject context is available to guide a comparison-oriented next step.",),
        )

    if strategy_profile.strategy_id == "compare" and subject_state_count > 1:
        status = "recommended"
        reason_codes = ("strategy_compare_prefers_side_by_side_review",)
        reason_messages = (
            "The active compare strategy promotes side-by-side review because other bounded states exist for this subject.",
        )
    else:
        status = "available"
        reason_codes = ("comparison_available_with_second_target",)
        reason_messages = (
            "A bounded comparison route is available once a second target reference is supplied.",
        )
    return ActionPlanEntry(
        action_id=COMPARE_TARGET_ACTION_ID,
        label="Compare this target with another bounded target",
        kind="compare_target",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        parameter_hint=f"left={target_ref}&right=<second bounded target ref>",
        subject_key=subject_key,
    )


def _manifest_export_action_entry(
    compatibility_status: str | None,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if strategy_profile.strategy_id == "preserve":
        status = "recommended"
        reason_codes = ("strategy_preserve_prefers_manifest_export",)
        reason_messages = (
            "The active preserve strategy promotes deterministic manifest export as a bounded preservation step.",
        )
    elif compatibility_status in {"incompatible", "unknown"} or compatibility_status is None:
        status = "available"
        reason_codes = ("manifest_export_available_for_inspection",)
        reason_messages = (
            "A deterministic manifest export is available as a bounded inspection and evidence-preserving step.",
        )
    else:
        status = "available"
        reason_codes = ("manifest_export_available",)
        reason_messages = (
            "A deterministic manifest export is available for this resolved target.",
        )
    return ActionPlanEntry(
        action_id=EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
        label="Export resolution manifest",
        kind="export_manifest",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        parameter_hint="target_ref=<resolved target ref>",
    )


def _bundle_export_action_entry(
    compatibility_status: str | None,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if strategy_profile.strategy_id == "preserve":
        status = "recommended"
        reason_codes = ("strategy_preserve_prefers_bundle_export",)
        reason_messages = (
            "The active preserve strategy promotes deterministic bundle export as a bounded snapshot step.",
        )
    elif compatibility_status == "incompatible":
        status = "available"
        reason_codes = ("bundle_export_available_when_host_incompatible",)
        reason_messages = (
            "A deterministic bundle export remains available even when the current host is incompatible.",
        )
    elif compatibility_status == "unknown":
        status = "available"
        reason_codes = ("bundle_export_available_when_compatibility_unknown",)
        reason_messages = (
            "A deterministic bundle export remains available when compatibility is unknown.",
        )
    else:
        status = "available"
        reason_codes = ("bundle_export_available",)
        reason_messages = ("A deterministic bundle export is available for this resolved target.",)
    return ActionPlanEntry(
        action_id=EXPORT_RESOLUTION_BUNDLE_ACTION_ID,
        label="Export resolution bundle",
        kind="export_bundle",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        parameter_hint="target_ref=<resolved target ref>",
    )


def _bundle_inspection_action_entry() -> ActionPlanEntry:
    return ActionPlanEntry(
        action_id=INSPECT_BUNDLE_ACTION_ID,
        label="Inspect a previously exported bundle",
        kind="inspect_bundle",
        status="available",
        reason_codes=("bundle_inspection_requires_bundle_path",),
        reason_messages=(
            "Bundle inspection is available after exporting or reading a local deterministic bundle path.",
        ),
        parameter_hint="bundle_path=<local bundle path after export>",
    )


def _store_manifest_action_entry(
    store_actions_enabled: bool,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if not store_actions_enabled:
        return ActionPlanEntry(
            action_id=STORE_RESOLUTION_MANIFEST_ACTION_ID,
            label="Store resolution manifest locally",
            kind="store_manifest",
            status="unavailable",
            reason_codes=("store_context_not_configured",),
            reason_messages=(
                "No local store context was configured for this action-plan request.",
            ),
        )
    if strategy_profile.strategy_id == "preserve":
        status = "recommended"
        reason_codes = ("strategy_preserve_prefers_local_manifest_store",)
        reason_messages = (
            "The active preserve strategy promotes storing the manifest in the local deterministic export store.",
        )
    else:
        status = "available"
        reason_codes = ("local_store_available",)
        reason_messages = ("A local deterministic export store is available for this request.",)
    return ActionPlanEntry(
        action_id=STORE_RESOLUTION_MANIFEST_ACTION_ID,
        label="Store resolution manifest locally",
        kind="store_manifest",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        parameter_hint="store_root=<local deterministic store root>",
    )


def _store_bundle_action_entry(
    store_actions_enabled: bool,
    strategy_profile: StrategyProfile,
) -> ActionPlanEntry:
    if not store_actions_enabled:
        return ActionPlanEntry(
            action_id=STORE_RESOLUTION_BUNDLE_ACTION_ID,
            label="Store resolution bundle locally",
            kind="store_bundle",
            status="unavailable",
            reason_codes=("store_context_not_configured",),
            reason_messages=(
                "No local store context was configured for this action-plan request.",
            ),
        )
    if strategy_profile.strategy_id == "preserve":
        status = "recommended"
        reason_codes = ("strategy_preserve_prefers_local_bundle_store",)
        reason_messages = (
            "The active preserve strategy promotes storing the bundle in the local deterministic export store.",
        )
    else:
        status = "available"
        reason_codes = ("local_store_available",)
        reason_messages = ("A local deterministic export store is available for this request.",)
    return ActionPlanEntry(
        action_id=STORE_RESOLUTION_BUNDLE_ACTION_ID,
        label="Store resolution bundle locally",
        kind="store_bundle",
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        parameter_hint="store_root=<local deterministic store root>",
    )


def _representation_action_entry(
    *,
    action_id: str,
    label: str,
    kind: str,
    status: str,
    reason_codes: tuple[str, ...],
    reason_messages: tuple[str, ...],
    representation: RepresentationSummary,
) -> ActionPlanEntry:
    return ActionPlanEntry(
        action_id=action_id,
        label=label,
        kind=kind,
        status=status,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        representation_id=representation.representation_id,
        representation_label=representation.label,
        representation_kind=representation.representation_kind,
        access_kind=representation.access_kind,
        access_locator=representation.access_locator,
        source_family=representation.source_family,
        source_locator=representation.source_locator,
    )


def _subject_state_count(catalog: NormalizedCatalog, subject_key: str | None) -> int:
    if subject_key is None:
        return 0
    return sum(
        1
        for record in catalog.records
        if subject_key_for_target_ref(record.target_ref) == subject_key
    )


def _strategy_rationale(
    strategy_profile: StrategyProfile,
    *,
    subject_key: str | None = None,
    subject_state_count: int = 0,
) -> tuple[str, ...]:
    if strategy_profile.strategy_id == "inspect":
        return (
            "Inspect strategy keeps source-backed inspection and evidence-aware review at the front of the bounded plan.",
        )
    if strategy_profile.strategy_id == "preserve":
        return (
            "Preserve strategy emphasizes deterministic export and local-store steps without changing the resolved truth model.",
        )
    if strategy_profile.strategy_id == "acquire":
        return (
            "Acquire strategy emphasizes direct bounded access paths where representations and host signals allow it.",
        )
    if strategy_profile.strategy_id == "compare":
        if subject_key is not None and subject_state_count > 1:
            return (
                f"Compare strategy emphasizes subject-state listing and side-by-side review because {subject_state_count} bounded states are known for '{subject_key}'.",
            )
        return (
            "Compare strategy emphasizes side-by-side and timeline-oriented review when bounded comparison context is available.",
        )
    return ()


def _select_inspection_representation(
    representations: tuple[RepresentationSummary, ...],
) -> RepresentationSummary | None:
    if not representations:
        return None
    ordered = sorted(
        representations,
        key=lambda representation: (
            0 if representation.access_kind == "view" and not representation.is_direct else 1,
            0 if representation.access_kind == "inspect" and not representation.is_direct else 1,
            0 if not representation.is_direct else 1,
            0 if representation.access_locator is not None else 1,
            representation.representation_id,
        ),
    )
    return ordered[0]


def _select_direct_representation(
    representations: tuple[RepresentationSummary, ...],
) -> RepresentationSummary | None:
    direct = [
        representation
        for representation in representations
        if representation.is_direct and representation.access_locator is not None
    ]
    if not direct:
        return None
    direct.sort(key=lambda representation: representation.representation_id)
    return direct[0]
