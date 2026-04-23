"""Bootstrap gateway package for the Eureka thin slice."""

from runtime.gateway.bootstrap import (
    build_demo_action_plan_public_api,
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_representations_public_api,
    build_demo_search_public_api,
    build_demo_stored_exports_public_api,
    build_demo_subject_states_public_api,
)

__all__ = [
    "build_demo_action_plan_public_api",
    "build_demo_absence_public_api",
    "build_demo_comparison_public_api",
    "build_demo_compatibility_public_api",
    "build_demo_resolution_actions_public_api",
    "build_demo_resolution_bundle_inspection_public_api",
    "build_demo_resolution_jobs_public_api",
    "build_demo_representations_public_api",
    "build_demo_search_public_api",
    "build_demo_stored_exports_public_api",
    "build_demo_subject_states_public_api",
]
