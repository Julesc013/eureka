"""Runtime loader for governed Source Registry v0 records."""

from runtime.source_registry.registry import (
    DEFAULT_SOURCE_INVENTORY_DIR,
    SourceRegistry,
    load_source_registry,
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
    "DEFAULT_SOURCE_INVENTORY_DIR",
    "DuplicateSourceIdError",
    "ExtractionPolicyRecord",
    "LiveAccessRecord",
    "MalformedSourceRecordError",
    "MissingRequiredFieldError",
    "SourceInventoryNotFoundError",
    "SourceRecord",
    "SourceRecordNotFoundError",
    "SourceRegistry",
    "SourceRegistryError",
    "load_source_registry",
]
