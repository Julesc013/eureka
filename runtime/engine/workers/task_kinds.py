from __future__ import annotations


VALIDATE_SOURCE_REGISTRY_TASK_KIND = "validate_source_registry"
BUILD_LOCAL_INDEX_TASK_KIND = "build_local_index"
QUERY_LOCAL_INDEX_TASK_KIND = "query_local_index"
VALIDATE_ARCHIVE_RESOLUTION_EVALS_TASK_KIND = "validate_archive_resolution_evals"


SUPPORTED_LOCAL_TASK_KINDS = (
    VALIDATE_SOURCE_REGISTRY_TASK_KIND,
    BUILD_LOCAL_INDEX_TASK_KIND,
    QUERY_LOCAL_INDEX_TASK_KIND,
    VALIDATE_ARCHIVE_RESOLUTION_EVALS_TASK_KIND,
)


_TASK_KIND_ALIASES = {
    "validate-source-registry": VALIDATE_SOURCE_REGISTRY_TASK_KIND,
    "build-local-index": BUILD_LOCAL_INDEX_TASK_KIND,
    "query-local-index": QUERY_LOCAL_INDEX_TASK_KIND,
    "validate-archive-resolution-evals": VALIDATE_ARCHIVE_RESOLUTION_EVALS_TASK_KIND,
}


def normalize_task_kind(task_kind: str) -> str:
    normalized = task_kind.strip()
    if not normalized:
        return ""
    return _TASK_KIND_ALIASES.get(normalized, normalized)


def task_kind_cli_name(task_kind: str) -> str:
    normalized = normalize_task_kind(task_kind)
    return normalized.replace("_", "-")
