from __future__ import annotations

from runtime.engine.core.fixture_catalog import FixtureEntry
from runtime.engine.interfaces.public import ObjectSummary


def fixture_entry_to_object_summary(entry: FixtureEntry) -> ObjectSummary:
    return ObjectSummary(
        id=entry.object_record["id"],
        kind=entry.object_record.get("kind"),
        label=entry.object_record.get("label"),
    )
