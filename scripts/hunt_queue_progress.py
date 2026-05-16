"""Helpers for validating completed HUNT queue progress.

Older HUNT validators were written while their successor task was the active
queue item. These helpers let them keep validating their own artifacts after
the queue has advanced to post-HUNT handoff tasks.
"""

from __future__ import annotations

from pathlib import Path


QUEUE_INDEX = Path(".aide/queue/index.yaml")
TASK_PACKET = Path(".aide/context/latest-task-packet.md")
POST_HUNT_TASKS = {
    "SYN-00",
    "F0-00",
    "HUNT-REMEDIATION",
    "HUNT-REMEDIATION-CONTINUE",
    "HUNT-TO-MAIN-PROMOTION-REVIEW",
}


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
    return ""


def queue_has_task(root: Path, task_id: str) -> bool:
    return bool(queue_task_status(root, task_id))


def queue_task_completed(root: Path, task_id: str) -> bool:
    return queue_task_status(root, task_id) == "completed"


def hunt_closeout_completed(root: Path) -> bool:
    return queue_task_completed(root, "HUNT-12")


def hunt_queue_current_or_advanced(root: Path, completed_task_id: str, expected_current: str) -> bool:
    current = current_recommended_task(root)
    current_id = current_recommended_task_id(root)
    if current == expected_current or current_id == expected_current:
        return True
    if not current or not queue_task_completed(root, completed_task_id) or not queue_has_task(root, expected_current):
        return False
    return hunt_closeout_completed(root) or queue_has_task(root, current_id)


def hunt_latest_packet_current_or_advanced(root: Path, completed_task_id: str, expected_task: str) -> bool:
    packet = read_repo_text(root, TASK_PACKET)
    current = current_recommended_task(root)
    current_id = current_recommended_task_id(root)
    if expected_task in packet:
        return True
    if not queue_task_completed(root, completed_task_id):
        return False
    return (bool(current) and current in packet) or (bool(current_id) and current_id in packet) or hunt_closeout_completed(root)


def post_hunt_current_allowed(root: Path) -> bool:
    current_id = current_recommended_task_id(root)
    return current_id in POST_HUNT_TASKS and hunt_closeout_completed(root)
