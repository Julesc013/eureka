"""Bootstrap web surface package for the Eureka workbench slice."""

from surfaces.web.server import (
    WorkbenchWsgiApp,
    render_bundle_inspection_page,
    render_resolution_workspace_page,
    render_search_results_page,
)
from surfaces.web.workbench import (
    render_bundle_inspection_html,
    render_resolution_workspace_html,
    render_search_results_html,
)

__all__ = [
    "WorkbenchWsgiApp",
    "render_bundle_inspection_html",
    "render_bundle_inspection_page",
    "render_resolution_workspace_html",
    "render_resolution_workspace_page",
    "render_search_results_html",
    "render_search_results_page",
]
