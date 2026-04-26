from __future__ import annotations

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import SourceSummary


_BOOTSTRAP_SOURCE_IDS_BY_FAMILY = {
    "synthetic_fixture": "synthetic-fixtures",
    "github_releases": "github-releases-recorded-fixtures",
    "internet_archive_recorded": "internet-archive-recorded-fixtures",
    "local_bundle_fixtures": "local-bundle-fixtures",
}


def normalized_record_to_source_summary(record: NormalizedResolutionRecord) -> SourceSummary:
    return SourceSummary(
        source_id=_BOOTSTRAP_SOURCE_IDS_BY_FAMILY.get(record.source_family),
        family=record.source_family,
        label=record.source_family_label,
        locator=record.access_path_locator or record.source_locator,
    )
