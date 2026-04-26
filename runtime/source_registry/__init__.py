"""Runtime loader for governed Source Registry v0 records."""

from runtime.source_registry.registry import (
    DEFAULT_SOURCE_INVENTORY_DIR,
    SourceRegistry,
    load_source_registry,
)
from runtime.source_registry.source_capability import (
    SOURCE_CAPABILITY_FIELDS,
    SourceCapabilityRecord,
)
from runtime.source_registry.source_coverage import (
    COVERAGE_DEPTHS,
    COVERAGE_DEPTH_RANKS,
    SOURCE_COVERAGE_FIELDS,
    SourceCoverageRecord,
)
from runtime.source_registry.source_record import (
    ConnectorRecord,
    DuplicateSourceIdError,
    ExtractionPolicyRecord,
    LiveAccessRecord,
    MalformedSourceRecordError,
    MissingRequiredFieldError,
    SourceInventoryNotFoundError,
    SourceRecord,
    SourceRecordNotFoundError,
    SourceRegistryError,
)

__all__ = [
    "ConnectorRecord",
    "COVERAGE_DEPTHS",
    "COVERAGE_DEPTH_RANKS",
    "DEFAULT_SOURCE_INVENTORY_DIR",
    "DuplicateSourceIdError",
    "ExtractionPolicyRecord",
    "LiveAccessRecord",
    "MalformedSourceRecordError",
    "MissingRequiredFieldError",
    "SOURCE_CAPABILITY_FIELDS",
    "SOURCE_COVERAGE_FIELDS",
    "SourceCapabilityRecord",
    "SourceCoverageRecord",
    "SourceInventoryNotFoundError",
    "SourceRecord",
    "SourceRecordNotFoundError",
    "SourceRegistry",
    "SourceRegistryError",
    "load_source_registry",
]
