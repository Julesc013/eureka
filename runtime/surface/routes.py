"""Internal route identities for SurfaceKernel projections."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SurfaceRoute:
    route_id: str
    view_family: str
    public_allowed: bool
    operator_allowed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "view_family": self.view_family,
            "public_allowed": self.public_allowed,
            "operator_allowed": self.operator_allowed,
        }


SURFACE_ROUTES: dict[str, SurfaceRoute] = {
    "search": SurfaceRoute("search", "public_search", True, True),
    "resolution_run": SurfaceRoute("resolution_run", "resolution_run", True, True),
    "object": SurfaceRoute("object", "object", True, True),
    "candidate": SurfaceRoute("candidate", "candidate", True, True),
    "need": SurfaceRoute("need", "need", True, True),
    "source": SurfaceRoute("source", "source", True, True),
    "evidence": SurfaceRoute("evidence", "evidence", True, True),
    "status": SurfaceRoute("status", "status", True, True),
    "about": SurfaceRoute("about", "about", True, True),
    "method": SurfaceRoute("method", "method", True, True),
    "workbench_run_review": SurfaceRoute("workbench_run_review", "workbench_run_review", False, True),
}


def resolve_surface_route(route_id: str) -> SurfaceRoute:
    normalized = str(route_id or "").strip()
    route = SURFACE_ROUTES.get(normalized)
    if route is None:
        return SurfaceRoute(normalized or "unknown", "unknown", False, False)
    return route
