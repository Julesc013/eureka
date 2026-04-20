"""Bootstrap web surface package for the Eureka workbench slice."""

from surfaces.web.server import WorkbenchWsgiApp, render_resolution_workspace_page
from surfaces.web.workbench import render_resolution_workspace_html

__all__ = [
    "WorkbenchWsgiApp",
    "render_resolution_workspace_html",
    "render_resolution_workspace_page",
]
