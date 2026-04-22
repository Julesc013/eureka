from __future__ import annotations

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import SourceSummary


def normalized_record_to_source_summary(record: NormalizedResolutionRecord) -> SourceSummary:
    return SourceSummary(
        family=record.source_family,
        label=record.source_family_label,
        locator=record.access_path_locator or record.source_locator,
    )
