from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_search_results_html(search_results: Mapping[str, Any]) -> str:
    query = _require_string(search_results.get("query"), "search_results.query", allow_empty=True)
    result_count = _require_int(search_results.get("result_count"), "search_results.result_count")
    results = _result_list(search_results.get("results"))
    absence = _optional_mapping(search_results.get("absence"), "search_results.absence")

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Compatibility Search</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Compatibility Search</h1>",
        "      <p>Compatibility-first deterministic search over the bounded demo corpus of governed synthetic fixtures and recorded GitHub releases.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/compare\">Compare two targets</a>",
        "        <a href=\"/subject\">List subject states</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Search the Corpus</h2>",
        "        <form method=\"get\" action=\"/search\">",
        "          <label for=\"q\">Bounded query</label>",
        f"          <input id=\"q\" name=\"q\" type=\"text\" value=\"{escape(query, quote=True)}\">",
        "          <button type=\"submit\">Search</button>",
        "        </form>",
        "      </section>",
    ]

    if query:
        parts.extend(
            [
                "      <section>",
                "        <h2>Search State</h2>",
                "        <dl>",
                f"          <dt>Query</dt><dd>{escape(query)}</dd>",
                f"          <dt>Result count</dt><dd>{result_count}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )
    else:
        parts.extend(
            [
                "      <section>",
                "        <h2>Search State</h2>",
                "        <p>Enter a bounded query to search the bounded demo corpus.</p>",
                "      </section>",
            ]
        )

    if results:
        parts.extend(
            [
                "      <section>",
                "        <h2>Results</h2>",
                "        <ul>",
            ]
        )
        for index, result in enumerate(results):
            target_ref = _require_string(result.get("target_ref"), f"results[{index}].target_ref")
            object_summary = _require_mapping(result.get("object"), f"results[{index}].object")
            object_id = _require_string(object_summary.get("id"), f"results[{index}].object.id")
            object_label = _require_string(
                object_summary.get("label") or object_id,
                f"results[{index}].object.label",
                allow_empty=False,
            )
            resolved_resource_id = _optional_string(
                result.get("resolved_resource_id"),
                f"results[{index}].resolved_resource_id",
            )
            source = _optional_mapping(result.get("source"), f"results[{index}].source")
            link = "/?target_ref=" + quote(target_ref, safe="")
            item = (
                "          <li>"
                f"<a href=\"{escape(link, quote=True)}\">{escape(object_label)}</a> "
                f"<span>({escape(target_ref)})</span>"
            )
            if source is not None:
                source_label = _require_string(
                    source.get("label") or source.get("family"),
                    f"results[{index}].source.label",
                )
                item += f" <span>[source: {escape(source_label)}]</span>"
            member_path = _optional_string(object_summary.get("member_path"), f"results[{index}].object.member_path")
            member_kind = _optional_string(object_summary.get("member_kind"), f"results[{index}].object.member_kind")
            parent_target_ref = _optional_string(
                object_summary.get("parent_target_ref"),
                f"results[{index}].object.parent_target_ref",
            )
            if member_path is not None:
                item += f" <span>[member: {escape(member_path)}]</span>"
            if member_kind is not None:
                item += f" <span>[kind: {escape(member_kind)}]</span>"
            if parent_target_ref is not None:
                item += f" <span>[parent: {escape(parent_target_ref)}]</span>"
            primary_lane = _optional_string(result.get("primary_lane"), f"results[{index}].primary_lane") or _optional_string(
                object_summary.get("primary_lane"),
                f"results[{index}].object.primary_lane",
            )
            user_cost_score = result.get("user_cost_score")
            if not isinstance(user_cost_score, int):
                user_cost_score = object_summary.get("user_cost_score")
            usefulness_summary = _optional_string(
                result.get("usefulness_summary"),
                f"results[{index}].usefulness_summary",
            ) or _optional_string(
                object_summary.get("usefulness_summary"),
                f"results[{index}].object.usefulness_summary",
            )
            if primary_lane is not None:
                item += f" <span>[lane: {escape(primary_lane)}]</span>"
            if isinstance(user_cost_score, int):
                item += f" <span>[user cost: {user_cost_score}]</span>"
            if usefulness_summary is not None:
                item += f" <span>[why: {escape(usefulness_summary)}]</span>"
            evidence = _optional_evidence_list(result.get("evidence"), f"results[{index}].evidence")
            if evidence:
                item += f" <span>[evidence: {escape(_compact_evidence_text(evidence[0]))}]</span>"
            if resolved_resource_id is not None:
                item += f" <span>[{escape(resolved_resource_id)}]</span>"
            item += "</li>"
            parts.append(item)
        parts.extend(
            [
                "        </ul>",
                "      </section>",
            ]
        )
    elif absence is not None:
        absence_code = _require_string(absence.get("code"), "absence.code")
        absence_message = _require_string(absence.get("message"), "absence.message")
        absence_link = "/absence/search?q=" + quote(query, safe="")
        parts.extend(
            [
                "      <section>",
                "        <h2>No Results</h2>",
                f"        <p><strong>{escape(absence_code)}</strong>: {escape(absence_message)}</p>",
                f"        <p><a href=\"{escape(absence_link, quote=True)}\">Explain this search miss</a></p>",
                "      </section>",
            ]
        )

    parts.extend(
        [
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _result_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("search_results.results must be a list.")
    results: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"search_results.results[{index}] must be an object.")
        results.append(item)
    return results


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object when provided.")
    return value


def _optional_evidence_list(value: Any, field_name: str) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    evidence: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        evidence.append(item)
    return evidence


def _require_string(value: Any, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _compact_evidence_text(entry: Mapping[str, Any]) -> str:
    claim_kind = _require_string(entry.get("claim_kind"), "evidence.claim_kind")
    asserted_by = _optional_string(entry.get("asserted_by_label"), "evidence.asserted_by_label") or _require_string(
        entry.get("asserted_by_family"),
        "evidence.asserted_by_family",
    )
    return f"{claim_kind} via {asserted_by}"
