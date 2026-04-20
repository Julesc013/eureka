from __future__ import annotations

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import ObjectSummary


def normalized_record_to_object_summary(record: NormalizedResolutionRecord) -> ObjectSummary:
    return ObjectSummary(
        id=record.object_id,
        kind=record.object_kind,
        label=record.object_label,
    )
