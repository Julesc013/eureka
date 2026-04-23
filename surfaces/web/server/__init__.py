"""Server-facing helpers for the bootstrap Eureka web workbench."""

from surfaces.web.server.api_routes import build_api_index_document
from surfaces.web.server.workbench_server import (
    WorkbenchWsgiApp,
    render_resolve_absence_page,
    render_search_absence_page,
    render_bundle_inspection_page,
    render_compatibility_page,
    render_comparison_page,
    render_representations_page,
    render_resolution_workspace_page,
    render_search_results_page,
    render_subject_states_page,
)

__all__ = [
    "WorkbenchWsgiApp",
    "build_api_index_document",
    "render_resolve_absence_page",
    "render_search_absence_page",
    "render_bundle_inspection_page",
    "render_compatibility_page",
    "render_comparison_page",
    "render_representations_page",
    "render_resolution_workspace_page",
    "render_search_results_page",
    "render_subject_states_page",
]
