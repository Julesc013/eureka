from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


_DEFAULT_HOST_PROFILE_PRESETS: tuple[dict[str, str], ...] = (
    {
        "host_profile_id": "windows-x86_64",
        "os_family": "windows",
        "architecture": "x86_64",
    },
    {
        "host_profile_id": "linux-x86_64",
        "os_family": "linux",
        "architecture": "x86_64",
    },
    {
        "host_profile_id": "macos-arm64",
        "os_family": "macos",
        "architecture": "arm64",
    },
)


def render_resolution_workspace_html(
    workbench_session: Mapping[str, Any],
    *,
    resolution_actions: Mapping[str, Any] | None = None,
    stored_exports: Mapping[str, Any] | None = None,
    host_profile_presets: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] = _DEFAULT_HOST_PROFILE_PRESETS,
) -> str:
    active_job = _require_mapping(workbench_session.get("active_job"), "workbench_session.active_job")
    target_ref = _require_string(active_job.get("target_ref"), "workbench_session.active_job.target_ref")
    status = _require_string(active_job.get("status"), "workbench_session.active_job.status")
    job_id = _require_string(active_job.get("job_id"), "workbench_session.active_job.job_id")
    resolved_resource_id = _optional_string(
        workbench_session.get("resolved_resource_id"),
        "workbench_session.resolved_resource_id",
    )

    selected_object = _optional_mapping(workbench_session.get("selected_object"), "workbench_session.selected_object")
    source = _optional_mapping(workbench_session.get("source"), "workbench_session.source")
    evidence = _evidence_list(workbench_session.get("evidence"))
    representations = _representation_list(workbench_session.get("representations"))
    notices = _notice_list(workbench_session.get("notices"))
    actions_model = _optional_mapping(resolution_actions, "resolution_actions")
    actions = _action_list(actions_model.get("actions")) if actions_model is not None else []
    action_notices = _notice_list(actions_model.get("notices")) if actions_model is not None else []
    stored_exports_model = _optional_mapping(stored_exports, "stored_exports")
    store_actions = (
        _action_list(stored_exports_model.get("store_actions"))
        if stored_exports_model is not None
        else []
    )
    stored_artifacts = (
        _stored_artifact_list(stored_exports_model.get("artifacts"))
        if stored_exports_model is not None
        else []
    )
    stored_export_notices = (
        _notice_list(stored_exports_model.get("notices"))
        if stored_exports_model is not None
        else []
    )

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Compatibility Workbench</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Compatibility Workbench</h1>",
        "      <p>Compatibility-first resolution workspace rendered from shared gateway and session contracts.</p>",
        "      <nav>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/compare\">Compare two targets</a>",
        "        <a href=\"/subject\">List subject states</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Resolve a Target</h2>",
        "        <form method=\"get\" action=\"/\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <button type=\"submit\">Resolve</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Search the Corpus</h2>",
        "        <form method=\"get\" action=\"/search\">",
        "          <label for=\"q\">Bounded query</label>",
        "          <input id=\"q\" name=\"q\" type=\"text\" value=\"\">",
        "          <button type=\"submit\">Search</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Job State</h2>",
        "        <dl>",
        f"          <dt>Target ref</dt><dd>{escape(target_ref)}</dd>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Job ID</dt><dd>{escape(job_id)}</dd>",
    ]
    if resolved_resource_id is not None:
        parts.append(f"          <dt>Resolved resource ID</dt><dd>{escape(resolved_resource_id)}</dd>")
    parts.extend(
        [
            "        </dl>",
        "      </section>",
        ]
    )
    if status == "blocked":
        absence_link = "/absence/resolve?target_ref=" + quote(target_ref, safe="")
        parts.extend(
            [
                "      <section>",
                "        <h2>Miss explanation</h2>",
                f"        <p><a href=\"{escape(absence_link, quote=True)}\">Explain this resolution miss</a></p>",
                "      </section>",
            ]
        )

    if selected_object is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Object</h2>",
                "        <dl>",
                f"          <dt>ID</dt><dd>{escape(_require_string(selected_object.get('id'), 'selected_object.id'))}</dd>",
            ]
        )
        object_kind = _optional_string(selected_object.get("kind"), "selected_object.kind")
        if object_kind is not None:
            parts.append(f"          <dt>Kind</dt><dd>{escape(object_kind)}</dd>")
        object_label = _optional_string(selected_object.get("label"), "selected_object.label")
        if object_label is not None:
            parts.append(f"          <dt>Label</dt><dd>{escape(object_label)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )
    else:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Object</h2>",
                "        <p>No selected object summary is available for this job.</p>",
                "      </section>",
            ]
        )

    if source is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Source</h2>",
                "        <dl>",
                f"          <dt>Family</dt><dd>{escape(_require_string(source.get('family'), 'source.family'))}</dd>",
            ]
        )
        source_label = _optional_string(source.get("label"), "source.label")
        if source_label is not None:
            parts.append(f"          <dt>Label</dt><dd>{escape(source_label)}</dd>")
        source_locator = _optional_string(source.get("locator"), "source.locator")
        if source_locator is not None:
            parts.append(f"          <dt>Origin</dt><dd>{escape(source_locator)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )

    if evidence:
        parts.extend(
            [
                "      <section>",
                "        <h2>Evidence</h2>",
                "        <ul>",
            ]
        )
        for entry in evidence:
            parts.append(f"          <li>{escape(_evidence_text(entry))}</li>")
        parts.extend(
            [
                "        </ul>",
                "      </section>",
            ]
        )

    parts.extend(
        [
            "      <section>",
            "        <h2>Known Representations/Access Paths</h2>",
        ]
    )
    if representations:
        parts.append("        <ul>")
        for entry in representations:
            parts.append("          <li>")
            parts.append(
                f"            <strong>{escape(_require_string(entry.get('label'), 'representation.label'))}</strong>"
            )
            parts.append("            <dl>")
            parts.append(
                f"              <dt>Representation kind</dt><dd>{escape(_require_string(entry.get('representation_kind'), 'representation.representation_kind'))}</dd>"
            )
            parts.append(
                f"              <dt>Access kind</dt><dd>{escape(_require_string(entry.get('access_kind'), 'representation.access_kind'))}</dd>"
            )
            parts.append(
                f"              <dt>Source family</dt><dd>{escape(_require_string(entry.get('source_family'), 'representation.source_family'))}</dd>"
            )
            source_label = _optional_string(entry.get("source_label"), "representation.source_label")
            if source_label is not None:
                parts.append(f"              <dt>Source label</dt><dd>{escape(source_label)}</dd>")
            content_type = _optional_string(entry.get("content_type"), "representation.content_type")
            if content_type is not None:
                parts.append(f"              <dt>Content type</dt><dd>{escape(content_type)}</dd>")
            byte_length = _optional_int(entry.get("byte_length"), "representation.byte_length")
            if byte_length is not None:
                parts.append(f"              <dt>Byte length</dt><dd>{byte_length}</dd>")
            access_locator = _optional_string(entry.get("access_locator"), "representation.access_locator")
            if access_locator is not None:
                parts.append(f"              <dt>Access locator</dt><dd>{escape(access_locator)}</dd>")
            source_locator = _optional_string(entry.get("source_locator"), "representation.source_locator")
            if source_locator is not None:
                parts.append(f"              <dt>Source locator</dt><dd>{escape(source_locator)}</dd>")
            is_direct = entry.get("is_direct")
            if isinstance(is_direct, bool):
                parts.append(f"              <dt>Direct</dt><dd>{escape(str(is_direct).lower())}</dd>")
            parts.append("            </dl>")
            parts.append("          </li>")
        parts.append("        </ul>")
    else:
        parts.append("        <p>No bounded representations or access paths are available for this target.</p>")
    parts.append("      </section>")

    parts.extend(
        [
            "      <section>",
            "        <h2>Actions</h2>",
        ]
    )
    available_actions = [action for action in actions if action["availability"] == "available"]
    if available_actions:
        parts.append("        <ul>")
        for action in available_actions:
            parts.append(
                "          "
                f"<li><a href=\"{escape(_require_string(action.get('href'), 'action.href'), quote=True)}\">"
                f"{escape(_require_string(action.get('label'), 'action.label'))}</a></li>"
            )
        parts.append("        </ul>")
    else:
        parts.append("        <p>No available actions are exposed for this target.</p>")

    unavailable_actions = [action for action in actions if action["availability"] != "available"]
    if unavailable_actions:
        parts.append("        <ul>")
        for action in unavailable_actions:
            parts.append(
                "          "
                f"<li>{escape(_require_string(action.get('label'), 'action.label'))} "
                f"({escape(_require_string(action.get('availability'), 'action.availability'))})</li>"
            )
        parts.append("        </ul>")

    if action_notices:
        parts.append("        <ul>")
        for notice in action_notices:
            code = _require_string(notice.get("code"), "action_notice.code")
            severity = _require_string(notice.get("severity"), "action_notice.severity")
            message = _optional_string(notice.get("message"), "action_notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if message is not None:
                item += f": {escape(message)}"
            item += "</li>"
            parts.append(item)
        parts.append("        </ul>")
    parts.append("      </section>")

    parts.extend(
        [
            "      <section>",
            "        <h2>Compatibility</h2>",
            "        <p>Evaluate this resolved target against one bounded bootstrap host profile preset.</p>",
        ]
    )
    if host_profile_presets:
        parts.append("        <ul>")
        for preset in host_profile_presets:
            if not isinstance(preset, Mapping):
                continue
            preset_id = _require_string(preset.get("host_profile_id"), "host_profile_preset.host_profile_id")
            os_family = _optional_string(preset.get("os_family"), "host_profile_preset.os_family")
            architecture = _optional_string(preset.get("architecture"), "host_profile_preset.architecture")
            href = (
                "/compatibility?target_ref="
                + quote(target_ref, safe="")
                + "&host="
                + quote(preset_id, safe="")
            )
            label = preset_id
            if os_family is not None and architecture is not None:
                label = f"{preset_id} ({os_family}, {architecture})"
            parts.append(
                "          "
                f"<li><a href=\"{escape(href, quote=True)}\">Check {escape(label)}</a></li>"
            )
        parts.append("        </ul>")
    else:
        parts.append("        <p>No bounded host profile presets are available in this bootstrap slice.</p>")
    parts.append("      </section>")

    if stored_exports_model is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Stored Exports</h2>",
            ]
        )

        available_store_actions = [action for action in store_actions if action["availability"] == "available"]
        if available_store_actions:
            parts.append("        <ul>")
            for action in available_store_actions:
                parts.append(
                    "          "
                    f"<li><a href=\"{escape(_require_string(action.get('href'), 'store_action.href'), quote=True)}\">"
                    f"{escape(_require_string(action.get('label'), 'store_action.label'))}</a></li>"
                )
            parts.append("        </ul>")
        else:
            parts.append("        <p>No local store actions are exposed for this target.</p>")

        unavailable_store_actions = [
            action for action in store_actions if action["availability"] != "available"
        ]
        if unavailable_store_actions:
            parts.append("        <ul>")
            for action in unavailable_store_actions:
                parts.append(
                    "          "
                    f"<li>{escape(_require_string(action.get('label'), 'store_action.label'))} "
                    f"({escape(_require_string(action.get('availability'), 'store_action.availability'))})</li>"
                )
            parts.append("        </ul>")

        if stored_artifacts:
            parts.append("        <ul>")
            for artifact in stored_artifacts:
                item = (
                    "          <li>"
                    f"{escape(_require_string(artifact.get('artifact_kind'), 'stored_artifact.artifact_kind'))}: "
                    f"<a href=\"{escape(_require_string(artifact.get('href'), 'stored_artifact.href'), quote=True)}\">"
                    f"{escape(_require_string(artifact.get('artifact_id'), 'stored_artifact.artifact_id'))}</a>"
                    f" ({escape(str(_require_int(artifact.get('byte_length'), 'stored_artifact.byte_length')))} bytes, "
                    f"{escape(_require_string(artifact.get('content_type'), 'stored_artifact.content_type'))})"
                )
                filename = _optional_string(artifact.get("filename"), "stored_artifact.filename")
                if filename is not None:
                    item += f" [{escape(filename)}]"
                artifact_resolved_resource_id = _optional_string(
                    artifact.get("resolved_resource_id"),
                    "stored_artifact.resolved_resource_id",
                )
                if artifact_resolved_resource_id is not None:
                    item += f" [resolved resource: {escape(artifact_resolved_resource_id)}]"
                item += "</li>"
                parts.append(item)
            parts.append("        </ul>")
        else:
            parts.append("        <p>No local stored exports are indexed for this target yet.</p>")

        if stored_export_notices:
            parts.append("        <ul>")
            for notice in stored_export_notices:
                code = _require_string(notice.get("code"), "stored_export_notice.code")
                severity = _require_string(notice.get("severity"), "stored_export_notice.severity")
                message = _optional_string(notice.get("message"), "stored_export_notice.message")
                item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
                if message is not None:
                    item += f": {escape(message)}"
                item += "</li>"
                parts.append(item)
            parts.append("        </ul>")
        parts.append("      </section>")

    if notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Notices</h2>",
                "        <ul>",
            ]
        )
        for notice in notices:
            code = _require_string(notice.get("code"), "notice.code")
            severity = _require_string(notice.get("severity"), "notice.severity")
            message = _optional_string(notice.get("message"), "notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if message is not None:
                item += f": {escape(message)}"
            item += "</li>"
            parts.append(item)
        parts.extend(
            [
                "        </ul>",
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


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("workbench_session.notices must be a list when provided.")
    notices: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"workbench_session.notices[{index}] must be an object.")
        notices.append(item)
    return notices


def _action_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("resolution_actions.actions must be a list when provided.")
    actions: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"resolution_actions.actions[{index}] must be an object.")
        actions.append(item)
    return actions


def _stored_artifact_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("stored_exports.artifacts must be a list when provided.")
    artifacts: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"stored_exports.artifacts[{index}] must be an object.")
        artifacts.append(item)
    return artifacts


def _evidence_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("workbench_session.evidence must be a list when provided.")
    evidence: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"workbench_session.evidence[{index}] must be an object.")
        evidence.append(item)
    return evidence


def _representation_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("workbench_session.representations must be a list when provided.")
    representations: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"workbench_session.representations[{index}] must be an object.")
        representations.append(item)
    return representations


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, field_name)


def _evidence_text(entry: Mapping[str, Any]) -> str:
    claim_kind = _require_string(entry.get("claim_kind"), "evidence.claim_kind")
    claim_value = _require_string(entry.get("claim_value"), "evidence.claim_value")
    asserted_by = _optional_string(entry.get("asserted_by_label"), "evidence.asserted_by_label") or _require_string(
        entry.get("asserted_by_family"),
        "evidence.asserted_by_family",
    )
    evidence_kind = _require_string(entry.get("evidence_kind"), "evidence.evidence_kind")
    evidence_locator = _require_string(entry.get("evidence_locator"), "evidence.evidence_locator")
    text = f"{claim_kind} = {claim_value} ({asserted_by}, {evidence_kind}, {evidence_locator})"
    asserted_at = _optional_string(entry.get("asserted_at"), "evidence.asserted_at")
    if asserted_at is not None:
        text += f" @ {asserted_at}"
    return text
