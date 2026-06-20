"""Helpers for validating completed LOCAL queue progress.

Older LOCAL validators were written while their task was the active queue item.
These helpers let them accept an already-advanced queue when the task they
validate is recorded as completed and the successor task exists.
"""

from __future__ import annotations

from pathlib import Path


QUEUE_INDEX = Path(".aide/queue/index.yaml")
TASK_PACKET = Path(".aide/context/latest-task-packet.md")
LATER_CONTROL_OR_HANDOFF_PREFIXES = (
    "AIDE-",
    "HUNT-",
    "SYN-",
    "DOMAIN-",
    "SCOUT-",
    "F0-",
    "G0",
    "LOCAL-APPLY-",
    "SOURCE-WAVE-",
    "SOURCE-ACTION-",
    "SNAPSHOT-RELAY-",
    "SOURCE-SNAPSHOT-",
    "PUBLIC-ALPHA-",
    "CI-FULL-DISCOVERY-",
    "IA-",
    "REVIEW-IA-CANDIDATES-",
    "SOURCE-FOUNDRY-",
    "DEV-AND-IA-",
    "DEV-TO-MAIN-",
    "HUMAN-LAST-",
    "HUMAN-END-",
    "E2E-",
    "SYNTHETIC-TRUTH-",
    "AUTONOMOUS-EVAL-",
    "PORTABLE-EUREKA-INSTANCE-",
    "REPO-LAYOUT-",
    "RESOLUTION-RUN-",
    "WORKBENCH-",
    "SEARCH-INTERACTION-",
    "INDEXLESS-LIVE-SEARCH-FALLBACK-",
    "REVIEW-LEDGER-",
    "WORKBENCH-RUN-REVIEW-PROJECTION-",
    "SURFACE-KERNEL-",
    "BASELINE-RENDERERS-",
    "HARD-QUERY-EVAL-",
    "REVIEWED-SEED-CORPUS-",
    "MANUAL-OBSERVATION-BATCH-",
    "HUMAN-REVIEW-BATCH-",
    "REVIEWED-CORPUS-SEED-BATCH-",
    "REVIEWED-ARTIFACT-RECORD-GATE-",
    "MANUAL-ARTIFACT-OBSERVATION-BATCH-",
    "HUMAN-ARTIFACT-REVIEW-BATCH-",
    "REVIEWED-ARTIFACT-CORPUS-BATCH-",
    "ARTIFACT-EVIDENCE-GAP-BATCH-",
    "ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-",
    "QUEUE-HANDOFF-DRIFT-REPAIR-",
    "GENERATED-ARTIFACT-DRIFT-REPAIR-",
    "CONTRACT-SCHEMA-DRIFT-REPAIR-",
    "HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-",
    "EXTERNAL-FULL-DISCOVERY-",
    "WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE",
    "WAITING_FOR_EXTERNAL_FULL_DISCOVERY",
    "WAITING_FOR_USER_HARDWARE_DETAILS",
)


def read_repo_text(root: Path, relative: Path) -> str:
    path = root / relative
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def current_recommended_task(root: Path) -> str:
    queue = read_repo_text(root, QUEUE_INDEX)
    for line in queue.splitlines():
        stripped = line.strip()
        if stripped.startswith("current_recommended_task:"):
            return stripped.split(":", 1)[1].strip()
    return ""


def current_recommended_task_id(root: Path) -> str:
    current = current_recommended_task(root)
    if not current:
        return ""
    return current.split()[0].strip()


def queue_task_status(root: Path, task_id: str) -> str:
    queue = read_repo_text(root, QUEUE_INDEX)
    in_entry = False
    for line in queue.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            in_entry = stripped.split(":", 1)[1].strip() == task_id
            continue
        if in_entry and stripped.startswith("status:"):
            return stripped.split(":", 1)[1].strip()
    return compact_queue_task_status(queue, task_id)


def compact_queue_task_status(queue: str, task_id: str) -> str:
    section = ""
    section_statuses = {
        "completed": "completed",
        "planned": "queued",
        "waiting": "waiting",
        "blocked": "blocked",
    }
    for line in queue.splitlines():
        if line and not line[:1].isspace() and line.strip().endswith(":"):
            section = line.strip()[:-1]
            continue
        stripped = line.strip()
        if not section or not stripped.startswith("- "):
            continue
        entry_id = stripped[2:].split()[0]
        if entry_id == task_id:
            return section_statuses.get(section, "")
    return ""


def queue_has_task(root: Path, task_id: str) -> bool:
    return bool(queue_task_status(root, task_id))


def queue_task_completed(root: Path, task_id: str) -> bool:
    status = queue_task_status(root, task_id)
    if status:
        return status == "completed"
    return is_later_control_or_handoff(current_recommended_task(root))


def queue_task_available(root: Path, task_id: str) -> bool:
    status = queue_task_status(root, task_id)
    if status:
        return status in {"queued", "completed", "needs_review", "waiting"}
    return is_later_control_or_handoff(current_recommended_task(root))


def queue_current_or_advanced(root: Path, completed_task_id: str, expected_current: str) -> bool:
    current = current_recommended_task(root)
    if current == expected_current:
        return True
    if is_later_control_or_handoff(current):
        return True
    return bool(current) and queue_task_completed(root, completed_task_id) and queue_has_task(root, expected_current)


def latest_packet_current_or_advanced(root: Path, completed_task_id: str, expected_task: str) -> bool:
    packet = read_repo_text(root, TASK_PACKET)
    current = current_recommended_task(root)
    if expected_task in packet:
        return True
    if packet_mentions_later_control_or_handoff(packet):
        return True
    return bool(current) and current in packet and queue_task_completed(root, completed_task_id)


def is_later_control_or_handoff(task_id: str) -> bool:
    compact_id = task_id.split()[0].strip() if task_id else ""
    return any(compact_id.startswith(prefix) for prefix in LATER_CONTROL_OR_HANDOFF_PREFIXES)


def packet_mentions_later_control_or_handoff(packet: str) -> bool:
    return any(prefix in packet for prefix in LATER_CONTROL_OR_HANDOFF_PREFIXES)


def f0_deferred_or_past_local_closeout(root: Path) -> bool:
    queue = read_repo_text(root, QUEUE_INDEX)
    return "deferred_until: LOCAL-14" in queue or is_later_control_or_handoff(current_recommended_task(root))
