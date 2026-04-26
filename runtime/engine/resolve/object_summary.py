from __future__ import annotations

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import ObjectSummary


def normalized_record_to_object_summary(record: NormalizedResolutionRecord) -> ObjectSummary:
    return ObjectSummary(
        id=record.object_id,
        kind=record.object_kind,
        label=record.object_label,
        record_kind=record.record_kind if record.record_kind != "resolved_object" else None,
        parent_target_ref=record.parent_target_ref,
        parent_resolved_resource_id=record.parent_resolved_resource_id,
        parent_representation_id=record.parent_representation_id,
        parent_object_label=record.parent_object_label,
        member_path=record.member_path,
        member_label=record.member_label,
        member_kind=record.member_kind,
        media_type=record.media_type,
        size_bytes=record.size_bytes,
        content_hash=record.content_hash,
        action_hints=record.action_hints,
    )
