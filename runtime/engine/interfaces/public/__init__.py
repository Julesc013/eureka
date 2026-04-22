"""Public engine request and result shapes for the Eureka thin slice."""

from runtime.engine.provenance import EvidenceSummary
from runtime.engine.interfaces.public.absence import (
    AbsenceNearMatch,
    AbsenceReport,
    ResolveAbsenceRequest,
    SearchAbsenceRequest,
)
from runtime.engine.interfaces.public.comparison import (
    ComparisonAgreement,
    ComparisonDisagreement,
    ComparisonRequest,
    ComparisonResult,
    ComparisonSide,
)
from runtime.engine.interfaces.public.resolution import (
    Notice,
    ObjectSummary,
    ResolutionRequest,
    ResolutionResult,
    SourceSummary,
)
from runtime.engine.interfaces.public.representations import (
    RepresentationsRequest,
    RepresentationsResult,
)
from runtime.engine.interfaces.public.search import SearchRequest, SearchResponse, SearchResultEntry
from runtime.engine.interfaces.public.subject_states import (
    SubjectStateSummary,
    SubjectStatesRequest,
    SubjectStatesResult,
    SubjectSummary,
)

__all__ = [
    "EvidenceSummary",
    "AbsenceNearMatch",
    "AbsenceReport",
    "ResolveAbsenceRequest",
    "SearchAbsenceRequest",
    "ComparisonAgreement",
    "ComparisonDisagreement",
    "ComparisonRequest",
    "ComparisonResult",
    "ComparisonSide",
    "Notice",
    "ObjectSummary",
    "ResolutionRequest",
    "ResolutionResult",
    "SourceSummary",
    "RepresentationsRequest",
    "RepresentationsResult",
    "SearchRequest",
    "SearchResponse",
    "SearchResultEntry",
    "SubjectStateSummary",
    "SubjectStatesRequest",
    "SubjectStatesResult",
    "SubjectSummary",
]
