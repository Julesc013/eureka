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
    "DOMAIN-00",
    "SCOUT-SCHEMA-00",
    "F0-00",
    "G0",
    "AIDE-BATCH-DOMAIN-FOUNDATION-01",
    "AIDE-BATCH-SCOUT-SCHEMA-01",
    "AIDE-BATCH-F0-FOUNDATION-01",
    "AIDE-BATCH-G0-QUALITY-FOUNDATION-01",
    "AIDE-BATCH-RUN-KERNEL-01",
    "HUNT-REMEDIATION",
    "HUNT-REMEDIATION-CONTINUE",
    "HUNT-TO-MAIN-PROMOTION-REVIEW",
    "IA-BUNDLE-01",
    "IA-BUNDLE-02",
    "IA-BUNDLE-03",
    "DEV-AND-IA-PROMOTION-BLOCKER-01",
    "DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW",
    "REPO-LAYOUT-CANON-01",
    "WORKBENCH-FOUNDATION-00",
    "SEARCH-INTERACTION-00",
    "WORKBENCH-RESULT-LANES-01",
    "IA-HUNT-BRIDGE-00",
    "RESOLUTION-RUN-KERNEL-00",
    "WORKBENCH-LIVE-RUN-01",
    "IA-LIVE-METADATA-LANE-01",
    "WORKBENCH-REVIEW-PROMOTE-01",
    "LOCAL-APPLY-GATE-01",
    "WORKBENCH-LOCAL-LOOP-CLOSEOUT-01",
    "DEV-TO-MAIN-PROMOTION-REVIEW-02",
    "SOURCE-ACTION-KERNEL-00",
    "SOURCE-WAVE-00",
    "SNAPSHOT-RELAY-00",
    "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01",
    "DEV-TO-MAIN-PROMOTION-REVIEW-03",
    "CI-FULL-DISCOVERY-HARNESS-00",
    "PUBLIC-ALPHA-READONLY-00",
    "PUBLIC-ALPHA-HOSTING-READINESS-00",
    "PUBLIC-ALPHA-READONLY-CLOSEOUT-01",
    "DEV-TO-MAIN-PROMOTION-REVIEW-04",
    "PUBLIC-ALPHA-LAUNCH-CANDIDATE-00",
    "PUBLIC-ALPHA-DEPLOY-DRY-RUN-00",
    "DEV-TO-MAIN-PROMOTION-REVIEW-05",
    "PUBLIC-ALPHA-LAUNCH-00",
    "PUBLIC-DEMAND-SIGNAL-00",
    "PUBLIC-SOURCE-REQUEST-QUEUE-00",
    "NATIVE-SNAPSHOT-CLIENT-00",
    "INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT",
    "INDEXLESS-LIVE-SEARCH-FALLBACK-00",
    "REVIEW-LEDGER-00",
    "WORKBENCH-RUN-REVIEW-PROJECTION-00",
    "SURFACE-KERNEL-00",
    "BASELINE-RENDERERS-00",
    "HARD-QUERY-EVAL-00",
    "REVIEWED-SEED-CORPUS-00",
    "MANUAL-OBSERVATION-BATCH-00",
    "HUMAN-REVIEW-BATCH-00",
    "REVIEWED-CORPUS-SEED-BATCH-01",
    "MANUAL-OBSERVATION-BATCH-01",
    "HUMAN-REVIEW-BATCH-01",
    "REVIEWED-CORPUS-SEED-BATCH-02",
    "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-01",
    "ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01",
    "QUEUE-HANDOFF-DRIFT-REPAIR-01",
    "SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01",
    "GENERATED-ARTIFACT-DRIFT-REPAIR-01",
    "CONTRACT-SCHEMA-DRIFT-REPAIR-01",
    "SOURCE-SNAPSHOT-FAILURE-REPAIR-01",
    "EXTERNAL-FULL-DISCOVERY-RERUN-02",
    "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-02",
    "SOURCE-SNAPSHOT-RELEASE-GATE-CLOSEOUT-02",
    "REVIEWED-ARTIFACT-RECORD-GATE-00",
    "MANUAL-ARTIFACT-OBSERVATION-BATCH-00",
    "HUMAN-ARTIFACT-REVIEW-BATCH-00",
    "REVIEWED-ARTIFACT-CORPUS-BATCH-01",
    "ARTIFACT-EVIDENCE-GAP-BATCH-00",
    "MANUAL-ARTIFACT-OBSERVATION-BATCH-01",
    "HUMAN-ARTIFACT-REVIEW-BATCH-01",
    "REVIEWED-ARTIFACT-RECORD-GATE-02",
    "EXTERNAL-FULL-DISCOVERY-RERUN-03",
    "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-03",
    "HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-03",
    "EXTERNAL-FULL-DISCOVERY-RERUN-04",
    "PUBLIC-ALPHA-READINESS-00",
    "DEV-TO-MAIN-PROMOTION-PREFLIGHT-07",
}
POST_HUNT_TASK_PREFIXES = (
    "ARTIFACT-EVIDENCE-GAP-BATCH-",
    "EXTERNAL-FULL-DISCOVERY-RERUN-",
    "HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-",
    "HUMAN-ARTIFACT-REVIEW-BATCH-",
    "MANUAL-ARTIFACT-OBSERVATION-BATCH-",
    "REVIEWED-ARTIFACT-CORPUS-BATCH-",
    "REVIEWED-ARTIFACT-RECORD-GATE-",
    "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-",
    "SOURCE-SNAPSHOT-RELEASE-GATE-CLOSEOUT-",
    "WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE",
    "WAITING_FOR_EXTERNAL_FULL_DISCOVERY",
    "WAITING_FOR_USER_HARDWARE_DETAILS",
)
POST_HUNT_COMPLETION_MARKERS = {
    "HUNT-12",
    "HUNT-REMEDIATION",
    "HUNT-REMEDIATION-CONTINUE",
    "HUNT-TO-MAIN-PROMOTION-REVIEW",
    "DEV-TO-MAIN-PROMOTION-REVIEW-02",
    "SOURCE-ACTION-KERNEL-00",
    "SOURCE-WAVE-00",
    "SNAPSHOT-RELAY-00",
    "CI-FULL-DISCOVERY-HARNESS-00",
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
    return bool(queue_task_status(root, task_id)) or post_hunt_current_allowed(root)


def queue_task_completed(root: Path, task_id: str) -> bool:
    status = queue_task_status(root, task_id)
    if status:
        return status == "completed"
    return post_hunt_current_allowed(root)


def hunt_closeout_completed(root: Path) -> bool:
    return any(queue_task_status(root, task_id) == "completed" for task_id in POST_HUNT_COMPLETION_MARKERS)


def hunt_queue_current_or_advanced(root: Path, completed_task_id: str, expected_current: str) -> bool:
    current = current_recommended_task(root)
    current_id = current_recommended_task_id(root)
    if current == expected_current or current_id == expected_current:
        return True
    if post_hunt_current_allowed(root):
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
    if post_hunt_current_allowed(root) and current_id and current_id in packet:
        return True
    if not queue_task_completed(root, completed_task_id):
        return False
    return (bool(current) and current in packet) or (bool(current_id) and current_id in packet) or hunt_closeout_completed(root)


def post_hunt_current_allowed(root: Path) -> bool:
    current_id = current_recommended_task_id(root)
    return (current_id in POST_HUNT_TASKS or current_id_starts_with_post_hunt_prefix(current_id)) and hunt_closeout_completed(root)


def current_id_starts_with_post_hunt_prefix(current_id: str) -> bool:
    return any(current_id.startswith(prefix) for prefix in POST_HUNT_TASK_PREFIXES)
