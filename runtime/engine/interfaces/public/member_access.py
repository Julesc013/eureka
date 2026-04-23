from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemberAccessRequest:
    target_ref: str
    representation_id: str
    member_path: str

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        representation_id: str,
        member_path: str,
    ) -> "MemberAccessRequest":
        normalized_target_ref = target_ref.strip()
        normalized_representation_id = representation_id.strip()
        normalized_member_path = member_path.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        if not normalized_representation_id:
            raise ValueError("representation_id must be a non-empty string.")
        if not normalized_member_path:
            raise ValueError("member_path must be a non-empty string.")
        return cls(
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            member_path=normalized_member_path,
        )
