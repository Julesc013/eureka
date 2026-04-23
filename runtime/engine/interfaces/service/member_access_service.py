from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

from runtime.engine.interfaces.public.member_access import MemberAccessRequest

if TYPE_CHECKING:
    from runtime.engine.members.member_access import MemberAccessResult


class MemberAccessService(Protocol):
    def read_member(self, request: MemberAccessRequest) -> MemberAccessResult:
        """Read one bounded member from one bounded fetched representation."""
