use serde::{Deserialize, Serialize};
use serde_json::{json, Map, Value};
use std::error::Error;
use std::fmt;

const CURRENT_SOURCE_HINTS: &[&str] = &[
    "internet_archive_recorded",
    "local_bundle_fixtures",
    "github_releases",
    "synthetic_fixture",
];

const OLD_PLATFORM_SOFTWARE_EXCLUDES: &[&str] = &[
    "operating_system_image",
    "os_iso_image",
    "operating_system_install_media",
    "generic_all_system_dump_without_member_index",
    "unrelated_support_cd_parent_without_relevant_member",
];

const GENERIC_PRODUCT_CLASSES: &[&str] = &[
    "app",
    "apps",
    "application",
    "applications",
    "browser",
    "client",
    "software",
    "tool",
    "tools",
    "utility",
    "utilities",
];

const SOFTWARE_NOUN_HINTS: &[&str] = &[
    "app",
    "apps",
    "application",
    "applications",
    "software",
    "browser",
    "client",
    "utility",
    "utilities",
    "tool",
    "tools",
    "antivirus",
];

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ResolutionTask {
    pub raw_query: String,
    pub task_kind: String,
    pub object_type: String,
    pub constraints: Value,
    pub prefer: Vec<String>,
    pub exclude: Vec<String>,
    pub action_hints: Vec<String>,
    pub source_hints: Vec<String>,
    pub planner_confidence: String,
    pub planner_notes: Vec<String>,
}

impl ResolutionTask {
    fn new(
        raw_query: &str,
        task_kind: &str,
        object_type: &str,
        constraints: Value,
    ) -> Self {
        Self {
            raw_query: raw_query.to_string(),
            task_kind: task_kind.to_string(),
            object_type: object_type.to_string(),
            constraints,
            prefer: Vec::new(),
            exclude: Vec::new(),
            action_hints: Vec::new(),
            source_hints: Vec::new(),
            planner_confidence: "low".to_string(),
            planner_notes: Vec::new(),
        }
    }
}

#[derive(Debug, Eq, PartialEq)]
pub enum QueryPlannerError {
    EmptyRawQuery,
}

impl fmt::Display for QueryPlannerError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            QueryPlannerError::EmptyRawQuery => {
                write!(formatter, "raw_query must be a non-empty string.")
            }
        }
    }
}

impl Error for QueryPlannerError {}

pub fn plan_query(raw_query: &str) -> Result<ResolutionTask, QueryPlannerError> {
    let trimmed = raw_query.trim();
    if trimmed.is_empty() {
        return Err(QueryPlannerError::EmptyRawQuery);
    }
    let normalized_query = normalize_query(trimmed);
    let platform = extract_platform_constraints(&normalized_query);

    if let Some(task) = plan_latest_compatible_release(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }
    if let Some(task) = plan_member_or_container_query(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }
    if let Some(task) = plan_driver_query(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }
    if let Some(task) = plan_documentation_query(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }
    if let Some(task) = plan_article_query(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }
    if let Some(task) = plan_vague_software_query(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }
    if let Some(task) = plan_platform_software_query(trimmed, &normalized_query, &platform) {
        return Ok(task);
    }

    let mut task = ResolutionTask::new(trimmed, "generic_search", "unknown", json!({}));
    task.action_hints = strings(&["inspect"]);
    task.planner_confidence = "low".to_string();
    task.planner_notes = strings(&[
        "No bounded Query Planner v0 family matched; keep the request as a generic deterministic search.",
    ]);
    Ok(task)
}

pub fn query_plan_response(raw_query: &str) -> Value {
    match plan_query(raw_query) {
        Ok(task) => json!({
            "status_code": 200,
            "body": query_plan_envelope(&task),
        }),
        Err(QueryPlannerError::EmptyRawQuery) => json!({
            "status_code": 400,
            "body": {
                "status": "blocked",
                "query_plan": null,
                "notices": [{
                    "code": "raw_query_required",
                    "severity": "warning",
                    "message": "raw_query must be a non-empty string.",
                }],
                "raw_query": raw_query,
            },
        }),
    }
}

pub fn query_plan_envelope(task: &ResolutionTask) -> Value {
    json!({
        "status": "planned",
        "query_plan": task,
    })
}

fn plan_latest_compatible_release(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    let (product_phrase, support_context, temporal_goal) =
        if let Some(without_prefix) = strip_latest_prefix(normalized_query) {
            if let Some((product, rest)) = without_prefix.split_once(" before ") {
                if let Some(context) = rest.strip_suffix(" support ended") {
                    (product.trim(), Some(context.trim()), "latest_before_support_drop")
                } else if let Some((product, platform_phrase)) = without_prefix.split_once(" for ") {
                    (product.trim(), Some(platform_phrase.trim()), "latest_compatible")
                } else {
                    return None;
                }
            } else if let Some((product, _platform_phrase)) = without_prefix.split_once(" for ") {
                (product.trim(), None, "latest_compatible")
            } else {
                return None;
            }
        } else {
            return None;
        };

    let mut constraints = base_constraints(platform);
    apply_product_or_function_hint(raw_query, product_phrase, &mut constraints);
    constraints.insert(
        "temporal_goal".to_string(),
        Value::String(temporal_goal.to_string()),
    );
    if let Some(context) = support_context {
        constraints.insert(
            "support_window_hint".to_string(),
            Value::String(format!("latest before {} support ended", context)),
        );
    }
    constraints.insert("compatibility_required".to_string(), Value::Bool(true));
    constraints.insert(
        "platform_is_constraint".to_string(),
        Value::Bool(platform.is_some()),
    );
    constraints.insert(
        "representation_hints".to_string(),
        json!(["versioned_release_artifact", "release_notes", "installer", "portable_package"]),
    );

    let mut task = ResolutionTask::new(
        raw_query,
        "find_latest_compatible_release",
        "software_release",
        Value::Object(constraints),
    );
    task.prefer = strings(&[
        "versioned_release_artifact",
        "release_notes_with_support_window",
        "compatibility_evidence",
    ]);
    task.exclude = prefixed_strings(
        &["latest_overall_without_platform_evidence"],
        OLD_PLATFORM_SOFTWARE_EXCLUDES,
    );
    task.action_hints = strings(&[
        "inspect",
        "compare_versions",
        "fetch_if_available",
        "export_manifest",
    ]);
    task.source_hints = strings(&[
        "internet_archive_recorded",
        "github_releases",
        "wayback_memento_placeholder",
        "vendor_archive_future",
    ]);
    task.planner_confidence = if platform.is_some() { "high" } else { "medium" }.to_string();
    task.planner_notes = strings(&[
        "Recognized a latest-compatible release query.",
        "The planner does not claim the exact latest version; it records the temporal and platform constraints for later evidence checks.",
    ]);
    Some(task)
}

fn plan_member_or_container_query(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    let has_container_signal = contains_any(
        normalized_query,
        &[" inside ", " inside", "support cd", " iso", " zip", "bundle", "package"],
    );
    let has_distribution_signal =
        contains_any(normalized_query, &["offline installer", "service pack download"]);
    if !has_container_signal && !has_distribution_signal {
        return None;
    }

    let member_type = infer_member_type(normalized_query);
    if member_type.is_none() && !has_distribution_signal {
        return None;
    }

    let mut constraints = base_constraints(platform);
    let container_hint = infer_container_hint(normalized_query);
    if let Some(hint) = container_hint {
        constraints.insert("container_hint".to_string(), Value::String(hint.to_string()));
    }
    if let Some(member_type) = member_type {
        constraints.insert(
            "member_type_hint".to_string(),
            Value::String(member_type.to_string()),
        );
    }
    if let Some(product_hint) = infer_named_product_hint(normalized_query) {
        constraints.insert("product_hint".to_string(), Value::String(product_hint));
    }
    if let Some(function_hint) = infer_software_function_hint(normalized_query) {
        constraints.insert(
            "function_hint".to_string(),
            Value::String(function_hint.to_string()),
        );
    }
    constraints.insert(
        "representation_hints".to_string(),
        json!(member_representation_hints(container_hint)),
    );
    constraints.insert(
        "member_discovery_hints".to_string(),
        json!({
            "preserve_parent_lineage": true,
            "prefer_member_path": true,
            "member_preview": true,
        }),
    );

    let mut task = ResolutionTask::new(
        raw_query,
        "find_member_in_container",
        "package_member",
        Value::Object(constraints),
    );
    task.prefer = strings(&[
        "member_record",
        "member_path",
        "parent_bundle_with_relevant_member",
        "compatibility_evidence",
    ]);
    task.exclude = strings(&[
        "parent_container_only_without_member_trace",
        "generic_collection_without_member_index",
    ]);
    task.action_hints = strings(&[
        "inspect_members",
        "decompose",
        "preview_member",
        "fetch_if_available",
        "export_manifest",
    ]);
    task.source_hints = strings(&[
        "local_bundle_fixtures",
        "internet_archive_recorded",
        "internet_archive_placeholder",
    ]);
    task.planner_confidence = if container_hint.is_some() { "high" } else { "medium" }.to_string();
    task.planner_notes = strings(&[
        "Recognized a member or container discovery query.",
        "Member-level target records are future work; this plan only emits bounded decomposition hints.",
    ]);
    Some(task)
}

fn plan_driver_query(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    if !normalized_query.contains("driver") {
        return None;
    }
    let hardware_hint = extract_hardware_hint(raw_query, normalized_query);
    if hardware_hint.is_empty() && platform.is_none() {
        return None;
    }

    let mut constraints = base_constraints(platform);
    if !hardware_hint.is_empty() {
        constraints.insert("hardware_hint".to_string(), Value::String(hardware_hint));
    }
    constraints.insert(
        "representation_hints".to_string(),
        json!(["driver_package", "INF", "support_media_member", "readme", "manual"]),
    );
    constraints.insert(
        "member_discovery_hints".to_string(),
        json!({
            "support_media_member": true,
            "prefer_inf_member": true,
        }),
    );

    let mut task = ResolutionTask::new(raw_query, "find_driver", "driver", Value::Object(constraints));
    task.prefer = strings(&[
        "driver_package",
        "inf_member",
        "support_bundle_member",
        "documentation_with_driver_locator",
    ]);
    task.exclude = strings(&[
        "generic_advice_only",
        "unrelated_full_os_media",
        "parent_support_cd_without_matching_driver_member",
    ]);
    task.action_hints = strings(&[
        "inspect",
        "inspect_members",
        "decompose",
        "fetch_if_available",
        "export_manifest",
    ]);
    task.source_hints = strings(&[
        "local_bundle_fixtures",
        "internet_archive_recorded",
        "wayback_memento_placeholder",
        "vendor_archive_future",
    ]);
    task.planner_confidence = if platform.is_some() { "high" } else { "medium" }.to_string();
    task.planner_notes = strings(&[
        "Recognized a driver lookup query.",
        "Hardware and platform hints remain bounded extracted constraints only.",
    ]);
    Some(task)
}

fn plan_documentation_query(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    if !contains_any(normalized_query, &["manual", "readme", "resource kit", "documentation"]) {
        return None;
    }

    let (subject_hint, document_hint) =
        if let Some(subject) = normalized_query.strip_prefix("manual for ") {
            (restore_subject_case(raw_query, subject.trim()), "manual")
        } else if normalized_query.contains("hardware maintenance manual") {
            (
                restore_subject_case(
                    raw_query,
                    normalized_query.replace("hardware maintenance manual", "").trim(),
                ),
                "hardware maintenance manual",
            )
        } else if normalized_query.contains("resource kit") {
            (
                restore_subject_case(raw_query, normalized_query.replace("pdf", "").trim()),
                "resource kit",
            )
        } else if normalized_query.contains("readme") {
            (
                restore_subject_case(raw_query, normalized_query.replace("readme", "").trim()),
                "readme",
            )
        } else {
            return None;
        };

    if subject_hint.is_empty() {
        return None;
    }

    let mut constraints = base_constraints(platform);
    constraints.insert(
        "document_hint".to_string(),
        Value::String(document_hint.to_string()),
    );
    constraints.insert("product_hint".to_string(), Value::String(subject_hint));
    constraints.insert(
        "representation_hints".to_string(),
        json!(["manual", "PDF", "TXT", "README", "scan"]),
    );

    let mut task = ResolutionTask::new(
        raw_query,
        "find_documentation",
        "documentation",
        Value::Object(constraints),
    );
    task.prefer = strings(&[
        "manual_pdf_or_scan",
        "documentation_record",
        "readme_member",
        "citeable_scan",
    ]);
    task.exclude = strings(&["generic_forum_post", "unattributed_summary"]);
    task.action_hints = strings(&["inspect", "view_read", "cite", "export_manifest"]);
    task.source_hints = strings(&[
        "internet_archive_recorded",
        "internet_archive_placeholder",
        "wayback_memento_placeholder",
    ]);
    task.planner_confidence = "high".to_string();
    task.planner_notes = strings(&["Recognized a manual or documentation lookup query."]);
    Some(task)
}

fn plan_article_query(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    let (topic_hint, year_hint) =
        if let Some(rest) = normalized_query.strip_prefix("article about ") {
            let (topic, tail) = rest.split_once(" in ")?;
            let tail = tail.strip_suffix(" magazine")?;
            let year = tail.strip_prefix("a ").unwrap_or(tail).trim();
            (topic.trim().to_string(), year.to_string())
        } else if let Some(rest) = normalized_query.strip_prefix("article inside ") {
            let (year, topic) = rest.split_once(" magazine scan about ")?;
            (topic.trim().to_string(), year.trim().to_string())
        } else {
            return None;
        };

    if topic_hint.is_empty() || year_hint.is_empty() {
        return None;
    }

    let mut constraints = base_constraints(platform);
    constraints.insert("topic_hint".to_string(), Value::String(topic_hint));
    constraints.insert("date_year_hint".to_string(), Value::String(year_hint));
    constraints.insert("document_hint".to_string(), Value::String("magazine".to_string()));
    constraints.insert(
        "representation_hints".to_string(),
        json!(["scan", "OCR", "page_range", "article_member"]),
    );
    constraints.insert(
        "member_discovery_hints".to_string(),
        json!({
            "prefer_article_member": true,
            "preserve_issue_lineage": true,
        }),
    );

    let mut task = ResolutionTask::new(
        raw_query,
        "find_document_article",
        "document_article",
        Value::Object(constraints),
    );
    task.prefer = strings(&["article_member", "page_range_hit", "ocr_text_snippet"]);
    task.exclude = strings(&["whole_issue_only_without_article_trace"]);
    task.action_hints = strings(&["inspect", "view_read", "cite", "export_manifest"]);
    task.source_hints = strings(&["internet_archive_placeholder"]);
    task.planner_confidence = "high".to_string();
    task.planner_notes = strings(&["Recognized an article-inside-scan style query."]);
    Some(task)
}

fn plan_vague_software_query(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    let vague_signal = contains_any(
        normalized_query,
        &[
            "old ",
            "classic ",
            "blue",
            "software to",
            "fix broken registry",
            "registry repair",
            "compression",
            "disk editor",
        ],
    );
    let function_hint = infer_vague_function_hint(normalized_query)?;
    if !vague_signal {
        return None;
    }

    let mut constraints = base_constraints(platform);
    if platform.is_none() {
        if normalized_query.contains("windows") {
            constraints.insert(
                "platform".to_string(),
                json!({"family": "Windows", "marketing_alias": "Windows (unspecified)"}),
            );
        } else if normalized_query.contains("mac") {
            constraints.insert(
                "platform".to_string(),
                json!({"family": "Mac", "marketing_alias": "Mac (unspecified)"}),
            );
        } else if normalized_query.contains("dos") {
            constraints.insert(
                "platform".to_string(),
                json!({"family": "DOS", "marketing_alias": "DOS"}),
            );
        }
    }
    constraints.insert(
        "function_hint".to_string(),
        Value::String(function_hint.to_string()),
    );
    if let Some(descriptor_hint) = infer_descriptor_hint(normalized_query) {
        constraints.insert(
            "descriptor_hint".to_string(),
            Value::String(descriptor_hint.to_string()),
        );
    }
    if normalized_query.contains("old") || normalized_query.contains("classic") {
        constraints.insert(
            "temporal_style_hint".to_string(),
            Value::String("old".to_string()),
        );
    }
    constraints.insert(
        "uncertainty_notes".to_string(),
        json!(["Vague identity query; exact software identity is not asserted by the planner."]),
    );

    let mut task = ResolutionTask::new(
        raw_query,
        "identify_software",
        "software",
        Value::Object(constraints),
    );
    task.prefer = strings(&[
        "named_software_artifact",
        "descriptive_release_notes",
        "compatibility_evidence",
    ]);
    task.exclude = prefixed_strings(&["generic_advice_only"], OLD_PLATFORM_SOFTWARE_EXCLUDES);
    task.action_hints = strings(&[
        "inspect_candidates",
        "compare",
        "search_documentation",
        "export_manifest",
    ]);
    task.source_hints = strings(&[
        "internet_archive_recorded",
        "local_bundle_fixtures",
        "wayback_memento_placeholder",
    ]);
    task.planner_confidence = "medium".to_string();
    task.planner_notes = strings(&[
        "Vague identity query; exact software identity is not asserted by the planner.",
    ]);
    Some(task)
}

fn plan_platform_software_query(
    raw_query: &str,
    normalized_query: &str,
    platform: &Option<Value>,
) -> Option<ResolutionTask> {
    if platform.is_none() || !contains_any(normalized_query, SOFTWARE_NOUN_HINTS) {
        return None;
    }

    let mut constraints = base_constraints(platform);
    constraints.insert("platform_is_constraint".to_string(), Value::Bool(true));
    constraints.insert(
        "target_object_hint".to_string(),
        Value::String("software_for_platform".to_string()),
    );
    if let Some(function_hint) = infer_software_function_hint(normalized_query) {
        constraints.insert(
            "function_hint".to_string(),
            Value::String(function_hint.to_string()),
        );
    }
    constraints.insert(
        "representation_hints".to_string(),
        json!(["installer", "portable_package", "release_asset", "member_artifact"]),
    );

    let mut task = ResolutionTask::new(
        raw_query,
        "browse_software",
        "software",
        Value::Object(constraints),
    );
    task.prefer = strings(&[
        "direct_software_artifact",
        "portable_package",
        "compatibility_evidence",
    ]);
    task.exclude = strings(OLD_PLATFORM_SOFTWARE_EXCLUDES);
    task.action_hints = strings(&["inspect", "fetch_if_available", "export_manifest"]);
    task.source_hints = strings(CURRENT_SOURCE_HINTS);
    task.planner_confidence = "high".to_string();
    task.planner_notes = strings(&[
        "Recognized a platform-scoped software browsing query.",
        "The named operating system is treated as a compatibility constraint, not the requested object.",
    ]);
    Some(task)
}

fn extract_platform_constraints(normalized_query: &str) -> Option<Value> {
    if contains_any(
        normalized_query,
        &["windows 7", "win7", "windows nt 6.1", "nt 6.1"],
    ) {
        return Some(json!({
            "family": "Windows NT",
            "version": "6.1",
            "marketing_alias": "Windows 7",
            "aliases": ["Win7", "Windows NT 6.1"],
        }));
    }
    if contains_any(
        normalized_query,
        &["windows xp", "winxp", "windows nt 5.1", "nt 5.1"],
    ) || contains_word(normalized_query, "xp")
    {
        return Some(json!({
            "family": "Windows NT",
            "version": "5.1",
            "marketing_alias": "Windows XP",
            "aliases": ["WinXP", "Windows NT 5.1"],
        }));
    }
    if contains_any(
        normalized_query,
        &["windows 2000", "win2k", "windows nt 5.0", "nt 5.0"],
    ) {
        return Some(json!({
            "family": "Windows NT",
            "version": "5.0",
            "marketing_alias": "Windows 2000",
            "aliases": ["Win2k", "Windows NT 5.0"],
        }));
    }
    if contains_any(normalized_query, &["windows 98", "win98"]) {
        return Some(json!({
            "family": "Windows",
            "version": "4.1",
            "marketing_alias": "Windows 98",
            "platform_family": "Win9x",
            "aliases": ["Win98"],
        }));
    }
    if contains_any(normalized_query, &["windows 95", "win95"]) {
        return Some(json!({
            "family": "Windows",
            "version": "4.0",
            "marketing_alias": "Windows 95",
            "platform_family": "Win9x",
            "aliases": ["Win95"],
        }));
    }
    if contains_any(normalized_query, &["classic mac os", "mac os 9"]) {
        return Some(json!({
            "family": "Classic Mac OS",
            "version": "9",
            "marketing_alias": "Mac OS 9",
            "aliases": ["Classic Mac OS"],
        }));
    }
    if contains_any(
        normalized_query,
        &["powerpc mac os x 10.4", "mac os x 10.4", "mac os x tiger", "tiger"],
    ) {
        return Some(json!({
            "family": "Mac OS X",
            "version": "10.4",
            "marketing_alias": "Mac OS X Tiger",
            "architecture": "PowerPC",
            "aliases": ["PowerPC Mac OS X 10.4"],
        }));
    }
    if contains_any(normalized_query, &["mac os x 10.6", "snow leopard"]) {
        return Some(json!({
            "family": "Mac OS X",
            "version": "10.6",
            "marketing_alias": "Mac OS X Snow Leopard",
            "aliases": ["Snow Leopard"],
        }));
    }
    None
}

fn apply_product_or_function_hint(
    raw_query: &str,
    product_phrase: &str,
    constraints: &mut Map<String, Value>,
) {
    let normalized_product = product_phrase.trim();
    if normalized_product.is_empty() {
        return;
    }
    if GENERIC_PRODUCT_CLASSES.contains(&normalized_product) {
        constraints.insert(
            "function_hint".to_string(),
            Value::String(normalized_product.to_string()),
        );
        return;
    }
    constraints.insert(
        "product_hint".to_string(),
        Value::String(restore_subject_case(raw_query, normalized_product)),
    );
}

fn infer_named_product_hint(normalized_query: &str) -> Option<String> {
    if normalized_query.contains("directx 9.0c") {
        return Some("DirectX 9.0c".to_string());
    }
    if normalized_query.contains("visual c++ 6") || normalized_query.contains("visual c++ 6.0") {
        return Some("Visual C++ 6.0".to_string());
    }
    if normalized_query.contains("norton") {
        return Some("Norton".to_string());
    }
    None
}

fn infer_member_type(normalized_query: &str) -> Option<&'static str> {
    if normalized_query.contains("driver") || normalized_query.contains("inf") {
        return Some("driver");
    }
    if normalized_query.contains("installer") || normalized_query.contains("service pack download")
    {
        return Some("installer");
    }
    if normalized_query.contains("readme") {
        return Some("readme");
    }
    if normalized_query.contains("app inside") {
        return Some("software");
    }
    None
}

fn infer_container_hint(normalized_query: &str) -> Option<&'static str> {
    if normalized_query.contains("support cd") {
        return Some("support_cd");
    }
    if normalized_query.contains("iso") {
        return Some("ISO");
    }
    if normalized_query.contains("zip") {
        return Some("ZIP");
    }
    if normalized_query.contains("bundle") {
        return Some("bundle");
    }
    if normalized_query.contains("package") || normalized_query.contains("service pack") {
        return Some("package");
    }
    None
}

fn member_representation_hints(container_hint: Option<&str>) -> Vec<String> {
    let mut hints = strings(&["member_path", "member_hash", "member_content_type"]);
    if let Some(container_hint) = container_hint {
        hints.push(container_hint.to_string());
    }
    hints.extend(strings(&["parent_lineage", "member_preview"]));
    hints
}

fn infer_descriptor_hint(normalized_query: &str) -> Option<&'static str> {
    if normalized_query.contains("blue")
        && normalized_query.contains("icon")
        && normalized_query.contains("globe")
    {
        return Some("blue icon globe");
    }
    if normalized_query.contains("blue") && normalized_query.contains("icon") {
        return Some("blue icon");
    }
    if normalized_query.contains("blue") && normalized_query.contains("globe") {
        return Some("blue globe");
    }
    if normalized_query.contains("blue") {
        return Some("blue");
    }
    if normalized_query.contains("icon") {
        return Some("icon");
    }
    if normalized_query.contains("globe") {
        return Some("globe");
    }
    None
}

fn extract_hardware_hint(raw_query: &str, normalized_query: &str) -> String {
    let mut hardware = normalized_query.to_string();
    for token in [
        "driver",
        "for",
        "windows 7",
        "win7",
        "windows nt 6.1",
        "nt 6.1",
        "windows xp",
        "winxp",
        "windows nt 5.1",
        "nt 5.1",
        "windows 2000",
        "win2k",
        "windows nt 5.0",
        "nt 5.0",
        "windows 98",
        "win98",
        "windows 95",
        "win95",
    ] {
        hardware = hardware.replace(token, " ");
    }
    let hardware = collapse_spaces(&hardware);
    if hardware.is_empty() {
        return String::new();
    }
    restore_subject_case(raw_query, &hardware)
}

fn infer_software_function_hint(normalized_query: &str) -> Option<&'static str> {
    if normalized_query.contains("registry")
        && (normalized_query.contains("repair") || normalized_query.contains("fix"))
    {
        return Some("registry repair");
    }
    if normalized_query.contains("browser") {
        return Some("browser");
    }
    if normalized_query.contains("ftp client") {
        return Some("FTP client");
    }
    if normalized_query.contains("client") {
        return Some("client");
    }
    if normalized_query.contains("utilities") || normalized_query.contains("utility") {
        return Some("utility");
    }
    if normalized_query.contains("antivirus") {
        return Some("antivirus");
    }
    if normalized_query.contains("compression") {
        return Some("compression utility");
    }
    if normalized_query.contains("disk editor") {
        return Some("disk editor");
    }
    None
}

fn infer_vague_function_hint(normalized_query: &str) -> Option<String> {
    if normalized_query.contains("ftp client") {
        return Some("FTP client".to_string());
    }
    if normalized_query.contains("file transfer") {
        return Some("file transfer".to_string());
    }
    if normalized_query.contains("compression") {
        return Some("compression utility".to_string());
    }
    if normalized_query.contains("disk editor") {
        return Some("disk editor".to_string());
    }
    if normalized_query.contains("fix broken registry")
        || normalized_query.contains("registry repair")
    {
        return Some("registry repair".to_string());
    }
    if let Some((_prefix, function)) = normalized_query.split_once("software to") {
        let function = function.trim();
        if !function.is_empty() {
            return Some(function.to_string());
        }
    }
    infer_software_function_hint(normalized_query).map(str::to_string)
}

fn strip_latest_prefix(normalized_query: &str) -> Option<&str> {
    normalized_query
        .strip_prefix("latest ")
        .or_else(|| normalized_query.strip_prefix("last "))
}

fn base_constraints(platform: &Option<Value>) -> Map<String, Value> {
    let mut constraints = Map::new();
    if let Some(platform) = platform {
        constraints.insert("platform".to_string(), platform.clone());
    }
    constraints
}

fn normalize_query(raw_query: &str) -> String {
    collapse_spaces(&raw_query.trim().to_ascii_lowercase())
}

fn collapse_spaces(value: &str) -> String {
    value.split_whitespace().collect::<Vec<&str>>().join(" ")
}

fn contains_any(value: &str, needles: &[&str]) -> bool {
    needles.iter().any(|needle| value.contains(needle))
}

fn contains_word(value: &str, word: &str) -> bool {
    value
        .split(|character: char| !character.is_ascii_alphanumeric() && character != '.')
        .any(|part| part == word)
}

fn restore_subject_case(raw_query: &str, normalized_fragment: &str) -> String {
    let fragment = normalized_fragment.trim();
    if fragment.is_empty() {
        return String::new();
    }
    let raw_lower = raw_query.to_ascii_lowercase();
    let fragment_lower = fragment.to_ascii_lowercase();
    if let Some(start) = raw_lower.find(&fragment_lower) {
        let end = start + fragment_lower.len();
        return raw_query[start..end].trim().to_string();
    }
    title_case_phrase(fragment)
}

fn title_case_phrase(value: &str) -> String {
    value
        .split_whitespace()
        .map(|part| {
            if part.chars().all(|character| character.is_ascii_lowercase()) {
                let mut chars = part.chars();
                match chars.next() {
                    Some(first) => {
                        format!("{}{}", first.to_ascii_uppercase(), chars.collect::<String>())
                    }
                    None => String::new(),
                }
            } else {
                part.to_string()
            }
        })
        .collect::<Vec<String>>()
        .join(" ")
}

fn strings(items: &[&str]) -> Vec<String> {
    items.iter().map(|item| item.to_string()).collect()
}

fn prefixed_strings(first: &[&str], rest: &[&str]) -> Vec<String> {
    let mut values = strings(first);
    values.extend(strings(rest));
    values
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::path::PathBuf;

    #[test]
    fn windows_7_apps_treats_platform_as_constraint() {
        let task = plan_query("Windows 7 apps").unwrap();

        assert_eq!(task.task_kind, "browse_software");
        assert_eq!(task.object_type, "software");
        assert_eq!(
            task.constraints["platform"]["marketing_alias"],
            Value::String("Windows 7".to_string())
        );
        assert_eq!(task.constraints["platform_is_constraint"], Value::Bool(true));
        assert!(task
            .exclude
            .contains(&"operating_system_install_media".to_string()));
    }

    #[test]
    fn latest_firefox_xp_records_temporal_goal() {
        let task = plan_query("latest Firefox before XP support ended").unwrap();

        assert_eq!(task.task_kind, "find_latest_compatible_release");
        assert_eq!(
            task.constraints["product_hint"],
            Value::String("Firefox".to_string())
        );
        assert_eq!(
            task.constraints["temporal_goal"],
            Value::String("latest_before_support_drop".to_string())
        );
        assert_eq!(
            task.constraints["platform"]["marketing_alias"],
            Value::String("Windows XP".to_string())
        );
    }

    #[test]
    fn driver_query_records_hardware_and_member_hints() {
        let task = plan_query("driver for ThinkPad T42 Wi-Fi Windows 2000").unwrap();

        assert_eq!(task.task_kind, "find_driver");
        assert_eq!(
            task.constraints["hardware_hint"],
            Value::String("ThinkPad T42 Wi-Fi".to_string())
        );
        assert_eq!(
            task.constraints["platform"]["marketing_alias"],
            Value::String("Windows 2000".to_string())
        );
        assert_eq!(
            task.constraints["member_discovery_hints"]["prefer_inf_member"],
            Value::Bool(true)
        );
    }

    #[test]
    fn vague_software_identity_records_uncertainty() {
        let task = plan_query("old blue FTP client for XP").unwrap();

        assert_eq!(task.task_kind, "identify_software");
        assert_eq!(
            task.constraints["function_hint"],
            Value::String("FTP client".to_string())
        );
        assert_eq!(
            task.constraints["descriptor_hint"],
            Value::String("blue".to_string())
        );
        assert_eq!(
            task.constraints["platform"]["marketing_alias"],
            Value::String("Windows XP".to_string())
        );
    }

    #[test]
    fn article_query_records_member_scan_hints() {
        let task = plan_query("article about ray tracing in a 1994 magazine").unwrap();

        assert_eq!(task.task_kind, "find_document_article");
        assert_eq!(
            task.constraints["topic_hint"],
            Value::String("ray tracing".to_string())
        );
        assert_eq!(
            task.constraints["date_year_hint"],
            Value::String("1994".to_string())
        );
        assert!(task.prefer.contains(&"article_member".to_string()));
    }

    #[test]
    fn generic_fallback_keeps_query_unclaimed() {
        let task = plan_query("mysterious thing").unwrap();

        assert_eq!(task.task_kind, "generic_search");
        assert_eq!(task.object_type, "unknown");
        assert_eq!(task.planner_confidence, "low");
    }

    #[test]
    fn query_planner_candidate_matches_python_oracle_goldens() {
        for (fixture, query) in [
            ("windows_7_apps.json", "Windows 7 apps"),
            ("windows_nt_61_utilities.json", "Windows NT 6.1 utilities"),
            ("windows_xp_software.json", "Windows XP software"),
            ("windows_98_registry_repair.json", "Windows 98 registry repair"),
            (
                "latest_firefox_before_xp_support_ended.json",
                "latest Firefox before XP support ended",
            ),
            ("latest_vlc_for_windows_xp.json", "latest VLC for Windows XP"),
            (
                "driver_thinkpad_t42_wifi_windows_2000.json",
                "ThinkPad T42 wifi driver Windows 2000",
            ),
            (
                "creative_ct1740_driver_windows_98.json",
                "Creative CT1740 driver Windows 98",
            ),
            ("old_blue_ftp_client_xp.json", "old blue FTP client for XP"),
            ("driver_inside_support_cd.json", "driver inside support CD"),
            ("installer_inside_iso.json", "installer inside ISO"),
            (
                "manual_sound_blaster_ct1740.json",
                "manual for Sound Blaster CT1740",
            ),
            ("mac_os_9_browser.json", "Mac OS 9 browser"),
            (
                "powerpc_mac_os_x_10_4_browser.json",
                "PowerPC Mac OS X 10.4 browser",
            ),
            (
                "article_ray_tracing_1994_magazine.json",
                "article about ray tracing in 1994 magazine",
            ),
            (
                "generic_unknown_query.json",
                "obscure utility with no known fixture",
            ),
        ] {
            let expected = load_query_planner_golden(fixture);
            let observed = query_plan_response(query);
            assert_eq!(observed, expected, "fixture {}", fixture);
        }
    }

    fn load_query_planner_golden(file_name: &str) -> Value {
        let path = repo_root()
            .join("tests/parity/golden/python_oracle/v0/query_planner")
            .join(file_name);
        let text = fs::read_to_string(path).unwrap();
        serde_json::from_str(&text).unwrap()
    }

    fn repo_root() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .and_then(|path| path.parent())
            .unwrap()
            .to_path_buf()
    }
}
