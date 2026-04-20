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
        "      <p>Compatibility-first deterministic search over the governed synthetic software corpus.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
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
                "        <p>Enter a bounded query to search the governed synthetic software corpus.</p>",
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
            link = "/?target_ref=" + quote(target_ref, safe="")
            item = (
                "          <li>"
                f"<a href=\"{escape(link, quote=True)}\">{escape(object_label)}</a> "
                f"<span>({escape(target_ref)})</span>"
                "</li>"
            )
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
        parts.extend(
            [
                "      <section>",
                "        <h2>No Results</h2>",
                f"        <p><strong>{escape(absence_code)}</strong>: {escape(absence_message)}</p>",
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
