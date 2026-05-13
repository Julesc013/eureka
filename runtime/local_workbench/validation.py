"""Validation helpers for local workbench HTML."""

from .errors import LocalWorkbenchValidationError


FORBIDDEN_SNIPPETS = (
    "<script",
    "javascript:",
    "method=\"post\"",
    "formmethod=\"post\"",
    "method='post'",
    "formmethod='post'",
)
FORBIDDEN_CONTROL_WORDS = (
    "review mutation",
    "create workunit",
    "run probe",
    "rebuild index",
    "enable lan",
    "install",
    "execute",
    "upload",
    "download",
)
FORBIDDEN_CLAIMS = (
    "production ready",
    "public launch ready",
    "globally complete",
    "exhaustive coverage",
    "legal approval",
    "rights cleared",
    "malware safe",
    "installability certified",
    "source truth accepted",
    "evidence truth accepted",
    "master index mutated",
    "deployment performed",
)


def validate_html_safe(text: str) -> str:
    lowered = text.lower()
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in lowered:
            raise LocalWorkbenchValidationError(f"forbidden html snippet: {snippet}")
    return text


def validate_no_mutation_controls(html: str) -> str:
    lowered = html.lower()
    for word in FORBIDDEN_CONTROL_WORDS:
        if word in lowered:
            raise LocalWorkbenchValidationError(f"forbidden mutation control: {word}")
    return html


def validate_no_external_assets(html: str) -> str:
    lowered = html.lower()
    for marker in ("src=\"http://", "src=\"https://", "href=\"http://", "href=\"https://"):
        if marker in lowered:
            raise LocalWorkbenchValidationError(f"external asset reference: {marker}")
    return html


def validate_required_accessibility_markers(html: str) -> str:
    lowered = html.lower()
    required = ("<title>", "<html lang=\"en\"", "<main>", "<nav")
    for marker in required:
        if marker not in lowered:
            raise LocalWorkbenchValidationError(f"missing accessibility marker: {marker}")
    if "<form" in lowered and "<label" not in lowered:
        raise LocalWorkbenchValidationError("forms require labels")
    return html


def validate_no_forbidden_claims(html: str) -> str:
    lowered = html.lower()
    for claim in FORBIDDEN_CLAIMS:
        if claim in lowered:
            raise LocalWorkbenchValidationError(f"forbidden claim: {claim}")
    return html


def validate_local_workbench_page(html: str) -> str:
    validate_html_safe(html)
    validate_no_mutation_controls(html)
    validate_no_external_assets(html)
    validate_no_forbidden_claims(html)
    validate_required_accessibility_markers(html)
    return html
