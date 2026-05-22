"""Offline H14 rollup wrapper for build_h14_h0_h13_scorecard_summary_preview."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.rollup_dry_run_common import build_h14_h0_h13_scorecard_summary_preview


def build(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any] | None = None):
    return build_h14_h0_h13_scorecard_summary_preview(rollup_inputs, policy_bundle or {})


def rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any] | None = None):
    return build(rollup_inputs, policy_bundle)
