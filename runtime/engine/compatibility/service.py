from __future__ import annotations

from runtime.engine.compatibility import (
    CompatibilityReason,
    CompatibilityVerdict,
    HostProfile,
    resolve_bootstrap_host_profile,
)
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public.compatibility import CompatibilityRequest, CompatibilityResult
from runtime.engine.interfaces.public.resolution import Notice, ResolutionRequest
from runtime.engine.interfaces.service import CompatibilityService, ResolutionService
from runtime.engine.resolve import ExactMatchResolutionService


class DeterministicCompatibilityService(CompatibilityService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        *,
        resolution_service: ResolutionService | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)

    def evaluate_compatibility(self, request: CompatibilityRequest) -> CompatibilityResult:
        host_profile = resolve_bootstrap_host_profile(request.host_profile_id)
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
        if outcome.status != "completed" or outcome.result is None:
            return CompatibilityResult(
                status="blocked",
                target_ref=request.target_ref,
                host_profile=host_profile,
                notices=outcome.notices,
            )

        record = self._catalog.find_by_target_ref(request.target_ref)
        if record is None:
            return CompatibilityResult(
                status="blocked",
                target_ref=request.target_ref,
                host_profile=host_profile,
                notices=(
                    Notice(
                        code="target_ref_not_found",
                        severity="warning",
                        message=f"No bounded record matched target_ref '{request.target_ref}'.",
                    ),
                ),
            )

        verdict = _evaluate_record_against_host(record.compatibility_requirements, host_profile)
        return CompatibilityResult(
            status="evaluated",
            target_ref=request.target_ref,
            host_profile=host_profile,
            compatibility_status=verdict.compatibility_status,
            resolved_resource_id=outcome.result.resolved_resource_id,
            primary_object=outcome.result.primary_object,
            source=outcome.result.source,
            reasons=verdict.reasons,
            next_steps=verdict.next_steps,
            notices=outcome.result.notices,
        )


def _evaluate_record_against_host(requirements, host_profile: HostProfile) -> CompatibilityVerdict:
    if requirements is None or not requirements.has_constraints():
        return CompatibilityVerdict(
            compatibility_status="unknown",
            reasons=(
                CompatibilityReason(
                    code="compatibility_requirements_missing",
                    message="This bounded record does not currently carry compatibility requirements.",
                ),
            ),
            next_steps=(
                "Inspect known representations and evidence directly.",
                "Try another bounded target with recorded compatibility hints.",
            ),
        )

    incompatible_reasons: list[CompatibilityReason] = []
    unknown_reasons: list[CompatibilityReason] = []
    positive_reasons: list[CompatibilityReason] = []

    if requirements.required_os_families:
        if host_profile.os_family not in requirements.required_os_families:
            incompatible_reasons.append(
                CompatibilityReason(
                    code="os_family_not_supported",
                    message=(
                        f"Host os_family '{host_profile.os_family}' is not in the bounded required_os_families: "
                        f"{', '.join(requirements.required_os_families)}."
                    ),
                )
            )
        else:
            positive_reasons.append(
                CompatibilityReason(
                    code="os_family_supported",
                    message=(
                        f"Host os_family '{host_profile.os_family}' matches the bounded required_os_families."
                    ),
                )
            )

    if requirements.required_architectures:
        if host_profile.architecture not in requirements.required_architectures:
            incompatible_reasons.append(
                CompatibilityReason(
                    code="architecture_not_supported",
                    message=(
                        f"Host architecture '{host_profile.architecture}' is not in the bounded required_architectures: "
                        f"{', '.join(requirements.required_architectures)}."
                    ),
                )
            )
        else:
            positive_reasons.append(
                CompatibilityReason(
                    code="architecture_supported",
                    message=(
                        f"Host architecture '{host_profile.architecture}' matches the bounded required_architectures."
                    ),
                )
            )

    if requirements.required_runtime_families:
        if host_profile.runtime_family is None:
            unknown_reasons.append(
                CompatibilityReason(
                    code="runtime_family_not_checked",
                    message="This bootstrap host profile preset does not include a runtime_family value to check.",
                )
            )
        elif host_profile.runtime_family not in requirements.required_runtime_families:
            incompatible_reasons.append(
                CompatibilityReason(
                    code="runtime_family_not_supported",
                    message=(
                        f"Host runtime_family '{host_profile.runtime_family}' is not in the bounded required_runtime_families: "
                        f"{', '.join(requirements.required_runtime_families)}."
                    ),
                )
            )
        else:
            positive_reasons.append(
                CompatibilityReason(
                    code="runtime_family_supported",
                    message=(
                        f"Host runtime_family '{host_profile.runtime_family}' matches the bounded required_runtime_families."
                    ),
                )
            )

    if requirements.required_features:
        missing_features = tuple(
            feature for feature in requirements.required_features if feature not in host_profile.features
        )
        if missing_features:
            incompatible_reasons.append(
                CompatibilityReason(
                    code="required_features_missing",
                    message=(
                        "The host profile is missing the bounded required features: "
                        f"{', '.join(missing_features)}."
                    ),
                )
            )
        else:
            positive_reasons.append(
                CompatibilityReason(
                    code="required_features_present",
                    message="All bounded required features are present in the host profile.",
                )
            )

    if incompatible_reasons:
        return CompatibilityVerdict(
            compatibility_status="incompatible",
            reasons=tuple(incompatible_reasons),
            next_steps=(
                "Try another bootstrap host profile preset.",
                "Inspect known representations before any manual action.",
            ),
        )

    if unknown_reasons:
        return CompatibilityVerdict(
            compatibility_status="unknown",
            reasons=tuple(unknown_reasons + positive_reasons),
            next_steps=(
                "Inspect known representations and evidence directly.",
                "Add bounded runtime or feature hints before treating this verdict as final.",
            ),
        )

    if positive_reasons:
        return CompatibilityVerdict(
            compatibility_status="compatible",
            reasons=tuple(positive_reasons),
            next_steps=(
                "Inspect known representations before any manual action.",
            ),
        )

    return CompatibilityVerdict(
        compatibility_status="unknown",
        reasons=(
            CompatibilityReason(
                code="compatibility_not_evaluated",
                message="The bounded compatibility requirements did not yield a decisive verdict.",
            ),
        ),
        next_steps=(
            "Inspect known representations and evidence directly.",
        ),
    )
