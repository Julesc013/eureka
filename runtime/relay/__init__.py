"""Localhost-only read-only relay helpers for fixture snapshots.

D-BUNDLE-02 relay code is a compatibility projection over explicit fixture
snapshots. It does not start a server on import and does not perform live
source access, downloads, uploads, execution, or index mutation.
"""

from __future__ import annotations

from runtime.relay.snapshot_relay import (
    build_relay_boundary_report,
    build_relay_from_snapshot,
    build_relay_health_packet,
    build_relay_manifest,
    build_relay_record_index,
    project_relay_response,
    query_relay_snapshot,
)

__all__ = [
    "build_relay_boundary_report",
    "build_relay_from_snapshot",
    "build_relay_health_packet",
    "build_relay_manifest",
    "build_relay_record_index",
    "project_relay_response",
    "query_relay_snapshot",
]

