"""Audit helpers for deterministic local worker runs."""

from .results import LocalWorkerResult


def build_worker_audit_event(result: LocalWorkerResult):
    if result.audit_event is not None:
        return result.audit_event
    return result.with_audit_event().audit_event
