from __future__ import annotations

import hashlib
import re
from urllib.parse import quote


_ARTIFACT_ID_PATTERN = re.compile(r"^(?P<algorithm>sha256):(?P<hex>[0-9a-f]{64})$")


def artifact_id_for_bytes(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def artifact_id_to_object_relpath(artifact_id: str) -> str:
    algorithm, hex_digest = _split_artifact_id(artifact_id)
    return f"objects/{algorithm}/{hex_digest[:2]}/{hex_digest[2:]}"


def artifact_id_to_metadata_relpath(artifact_id: str) -> str:
    algorithm, hex_digest = _split_artifact_id(artifact_id)
    return f"metadata/{algorithm}--{hex_digest}.json"


def target_ref_to_index_relpath(target_ref: str) -> str:
    normalized_target_ref = target_ref.strip()
    if not normalized_target_ref:
        raise ValueError("target_ref must be a non-empty string.")
    return f"indexes/by-target/{quote(normalized_target_ref, safe='')}.json"


def _split_artifact_id(artifact_id: str) -> tuple[str, str]:
    match = _ARTIFACT_ID_PATTERN.fullmatch(artifact_id)
    if match is None:
        raise ValueError("artifact_id must match 'sha256:<64 lowercase hex characters>'.")
    return match.group("algorithm"), match.group("hex")
