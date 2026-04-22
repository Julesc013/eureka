"""Server-facing helpers for the bootstrap Eureka web workbench."""

from surfaces.web.server.api_routes import build_api_index_document
from surfaces.web.server.workbench_server import (
    WorkbenchWsgiApp,
    render_bundle_inspection_page,
    render_resolution_workspace_page,
    render_search_results_page,
)

__all__ = [
    "WorkbenchWsgiApp",
    "build_api_index_document",
    "render_bundle_inspection_page",
    "render_resolution_workspace_page",
    "render_search_results_page",
]
