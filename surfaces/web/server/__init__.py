"""Server-facing helpers for the bootstrap Eureka web workbench."""

from surfaces.web.server.workbench_server import (
    WorkbenchWsgiApp,
    render_bundle_inspection_page,
    render_resolution_workspace_page,
    render_search_results_page,
)

__all__ = [
    "WorkbenchWsgiApp",
    "render_bundle_inspection_page",
    "render_resolution_workspace_page",
    "render_search_results_page",
]
