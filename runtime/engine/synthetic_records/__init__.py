"""Deterministic synthetic records derived from bounded fixture evidence."""

from runtime.engine.synthetic_records.member_record import SyntheticMemberRecord
from runtime.engine.synthetic_records.member_record_synthesis import (
    augment_catalog_with_synthetic_member_records,
    synthesize_member_normalized_records,
    synthesize_member_records,
    synthetic_member_target_ref,
)

__all__ = [
    "SyntheticMemberRecord",
    "augment_catalog_with_synthetic_member_records",
    "synthesize_member_normalized_records",
    "synthesize_member_records",
    "synthetic_member_target_ref",
]
