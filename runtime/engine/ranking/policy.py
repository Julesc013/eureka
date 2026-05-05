from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from runtime.engine.ranking.errors import RankingDryRunError


ROOT = Path(__file__).resolve().parents[3]
APPROVED_EXAMPLE_ROOTS = (
    ROOT / "examples" / "public_search_ranking_dry_run",
    ROOT / "examples" / "evidence_weighted_ranking",
    ROOT / "examples" / "compatibility_aware_ranking",
)
AUDIT_ROOT = ROOT / "control" / "audits" / "public-search-ranking-local-dry-run-runtime-v0"

FORBIDDEN_CLI_FIELDS = {
    "--url",
    "--live-source",
    "--source-url",
    "--connector",
    "--source-cache-path",
    "--evidence-ledger-path",
    "--candidate-path",
    "--store-root",
    "--index-path",
    "--database",
    "--serve",
    "--hosted",
    "--write-public",
    "--mutate",
    "--publish",
    "--promote",
    "--suppress",
    "--telemetry",
    "--user-profile",
    "--ad-signal",
    "--model-provider",
    "--ai-rerank",
}

HARD_BOOLEANS = {
    "local_dry_run": True,
    "public_search_ranking_runtime_enabled": False,
    "public_search_response_changed": False,
    "public_search_order_changed": False,
    "public_search_routes_changed": False,
    "hosted_runtime_enabled": False,
    "hidden_scores_enabled": False,
    "hidden_suppression_performed": False,
    "result_suppression_enabled": False,
    "model_call_performed": False,
    "AI_reranking_performed": False,
    "telemetry_signal_used": False,
    "popularity_signal_used": False,
    "user_profile_signal_used": False,
    "ad_signal_used": False,
    "source_cache_read": False,
    "evidence_ledger_read": False,
    "source_cache_mutated": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "candidate_promotion_performed": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
    "live_source_called": False,
    "external_calls_performed": False,
    "credentials_used": False,
    "downloads_enabled": False,
    "installs_enabled": False,
    "execution_enabled": False,
}

URL_RE = re.compile(r"(?i)^(https?|ftp|file|data|javascript)://")
WINDOWS_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")
SECRET_KEY_RE = re.compile(r"(?i)(secret|token|api[_-]?key|password|credential)")
PRIVATE_PATH_RE = re.compile(r"(?i)(/users/|\\\\users\\\\|/home/|~[\\/]|appdata|\\.ssh|\\.aws)")

SIGNAL_KEYS = {
    "telemetry",
    "telemetry_signal",
    "user_profile",
    "user_profile_signal",
    "ad_signal",
    "model_signal",
    "model_provider",
    "ai_rerank",
    "popularity_signal",
}

SUPPRESSION_KEYS = {"suppress", "suppressed", "result_suppression", "hide_result"}

MUTATION_KEYS = {
    "mutate",
    "mutation",
    "public_search_order_changed",
    "public_search_response_changed",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "promote",
    "candidate_promotion_performed",
}


def validate_no_forbidden_cli_args(argv: list[str]) -> None:
    for arg in argv:
        if arg in FORBIDDEN_CLI_FIELDS:
            raise RankingDryRunError(f"forbidden argument rejected: {arg}")


def resolve_approved_root(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        raise RankingDryRunError("absolute example roots are not accepted")
    resolved = (ROOT / path).resolve()
    if not any(_is_relative_to(resolved, root.resolve()) for root in APPROVED_EXAMPLE_ROOTS):
        raise RankingDryRunError("example root is outside approved ranking dry-run roots")
    return resolved


def validate_output_path(path_text: str) -> Path:
    path = Path(path_text)
    resolved = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    temp_root = Path(__import__("tempfile").gettempdir()).resolve()
    if _is_relative_to(resolved, AUDIT_ROOT.resolve()) or _is_relative_to(resolved, temp_root):
        return resolved
    raise RankingDryRunError("output path must be under the P107 audit pack or the temp directory")


def validate_public_safe_record(record: Any) -> list[str]:
    warnings: list[str] = []
    _walk_public_safe(record, "$", warnings)
    return warnings


def assert_mutation_disabled() -> None:
    for key, value in HARD_BOOLEANS.items():
        if key == "local_dry_run":
            if value is not True:
                raise RankingDryRunError("local_dry_run must remain true")
        elif value is not False:
            raise RankingDryRunError(f"{key} must remain false")


def _walk_public_safe(value: Any, path: str, warnings: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lower_key = str(key).lower()
            if SECRET_KEY_RE.search(lower_key):
                raise RankingDryRunError(f"secret-like field detected at {path}.{key}")
            if lower_key in SIGNAL_KEYS and child not in (False, None, [], {}):
                raise RankingDryRunError(f"telemetry/profile/ad/model signal detected at {path}.{key}")
            if lower_key in SUPPRESSION_KEYS and child not in (False, None, [], {}):
                raise RankingDryRunError(f"result suppression claim detected at {path}.{key}")
            if lower_key in MUTATION_KEYS and child not in (False, None, [], {}):
                raise RankingDryRunError(f"mutation or promotion claim detected at {path}.{key}")
            _walk_public_safe(child, f"{path}.{key}", warnings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_public_safe(child, f"{path}[{index}]", warnings)
    elif isinstance(value, str):
        if URL_RE.match(value):
            raise RankingDryRunError(f"URL or live source value rejected at {path}")
        if WINDOWS_ABS_RE.match(value) or value.startswith("/") or PRIVATE_PATH_RE.search(value):
            raise RankingDryRunError(f"private or absolute path rejected at {path}")
        if SECRET_KEY_RE.search(value):
            raise RankingDryRunError(f"secret-like value rejected at {path}")
        if len(value) > 5000:
            warnings.append(f"long string at {path} was accepted as metadata but should stay bounded")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True

