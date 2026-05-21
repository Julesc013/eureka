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
    "IA-",
    "DEV-AND-IA-",
    "REPO-LAYOUT-",
    "WORKBENCH-",
    "SEARCH-INTERACTION-",
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
    return ""


def queue_has_task(root: Path, task_id: str) -> bool:
    return bool(queue_task_status(root, task_id))


def queue_task_completed(root: Path, task_id: str) -> bool:
    return queue_task_status(root, task_id) == "completed"


def queue_task_available(root: Path, task_id: str) -> bool:
    return queue_task_status(root, task_id) in {"queued", "completed", "needs_review"}


def queue_current_or_advanced(root: Path, completed_task_id: str, expected_current: str) -> bool:
    current = current_recommended_task(root)
    if current == expected_current:
        return True
    if is_later_control_or_handoff(current) and queue_task_completed(root, completed_task_id):
        return True
    return bool(current) and queue_task_completed(root, completed_task_id) and queue_has_task(root, expected_current)


def latest_packet_current_or_advanced(root: Path, completed_task_id: str, expected_task: str) -> bool:
    packet = read_repo_text(root, TASK_PACKET)
    current = current_recommended_task(root)
    if expected_task in packet:
        return True
    if queue_task_completed(root, completed_task_id) and packet_mentions_later_control_or_handoff(packet):
        return True
    return bool(current) and current in packet and queue_task_completed(root, completed_task_id)


def is_later_control_or_handoff(task_id: str) -> bool:
    return any(task_id.startswith(prefix) for prefix in LATER_CONTROL_OR_HANDOFF_PREFIXES)


def packet_mentions_later_control_or_handoff(packet: str) -> bool:
    return any(prefix in packet for prefix in LATER_CONTROL_OR_HANDOFF_PREFIXES)
