"""Future disabled agent research report schema contract."""

from typing import Any, Mapping

from .errors import AgentResearchValidationError
from .records import AgentResearchReportSchema


REQUIRED_REPORT_FIELDS = (
    "report_id",
    "task_id",
    "search_hunt_id",
    "search_need_id",
    "candidate_aliases",
    "candidate_source_leads",
    "candidate_dead_urls",
    "candidate_wayback_paths",
    "candidate_extraction_targets",
    "candidate_workunits",
    "absence_explanation_draft",
    "confidence_notes",
    "limitations",
    "forbidden_claims_absent",
    "review_required",
    "public_index_mutation_performed",
    "master_index_mutation_performed",
)

FORBIDDEN_REPORT_CLAIMS = (
    "verified_truth_claims",
    "rights_clearance",
    "malware_safety_certification",
    "automatic_index_mutation",
    "automatic_source_approval",
)


def build_agent_research_report_schema() -> AgentResearchReportSchema:
    return AgentResearchReportSchema(
        schema_version="agent_research_report_schema.v0",
        required_fields=REQUIRED_REPORT_FIELDS,
        review_required=True,
        candidate_only=True,
        public_index_mutation_performed=False,
        master_index_mutation_performed=False,
        forbidden_claims=FORBIDDEN_REPORT_CLAIMS,
    )


def validate_agent_research_report_shape(report: Mapping[str, Any]) -> Mapping[str, Any]:
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            raise AgentResearchValidationError(f"agent research report missing field: {field}")
    return report


def validate_candidate_only_report(report: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_agent_research_report_shape(report)
    if report.get("review_required") is not True:
        raise AgentResearchValidationError("agent research report must require review")
    if report.get("forbidden_claims_absent") is not True:
        raise AgentResearchValidationError("agent research report must record forbidden_claims_absent=true")
    if report.get("public_index_mutation_performed") is not False:
        raise AgentResearchValidationError("agent research report must not mutate public index")
    if report.get("master_index_mutation_performed") is not False:
        raise AgentResearchValidationError("agent research report must not mutate master index")
    for claim in FORBIDDEN_REPORT_CLAIMS:
        if report.get(claim) not in (None, False):
            raise AgentResearchValidationError(f"forbidden report claim: {claim}")
    return report
