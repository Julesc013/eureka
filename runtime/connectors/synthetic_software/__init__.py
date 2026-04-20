"""Synthetic software connector for the Eureka bootstrap ingestion boundary."""

from runtime.connectors.synthetic_software.fixture_connector import SyntheticSoftwareConnector
from runtime.connectors.synthetic_software.fixture_source import (
    DEFAULT_SYNTHETIC_FIXTURE_PATH,
    load_synthetic_source_records,
)

__all__ = [
    "DEFAULT_SYNTHETIC_FIXTURE_PATH",
    "SyntheticSoftwareConnector",
    "load_synthetic_source_records",
]
