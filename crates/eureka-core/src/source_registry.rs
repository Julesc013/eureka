use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::error::Error;
use std::fmt;
use std::fs;
use std::path::{Path, PathBuf};

pub const SOURCE_CAPABILITY_FIELDS: &[&str] = &[
    "supports_search",
    "supports_item_metadata",
    "supports_file_listing",
    "supports_bulk_access",
    "supports_delta_or_feed",
    "supports_live_probe",
    "supports_member_listing",
    "supports_reviews_or_comments",
    "supports_hashes",
    "supports_signatures",
    "supports_content_text",
    "supports_temporal_captures",
    "supports_action_paths",
    "auth_required",
    "network_required",
    "local_private",
    "fixture_backed",
    "recorded_fixture_backed",
    "live_supported",
    "live_deferred",
];

pub const COVERAGE_DEPTHS: &[&str] = &[
    "source_known",
    "catalog_indexed",
    "metadata_indexed",
    "representation_indexed",
    "content_or_member_indexed",
    "action_indexed",
];

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ConnectorRecord {
    pub label: String,
    pub entrypoint: Option<String>,
    pub status: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct LiveAccessRecord {
    pub mode: String,
    pub notes: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ExtractionPolicyRecord {
    pub mode: String,
    pub notes: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SourceCapabilityRecord {
    pub supports_search: bool,
    pub supports_item_metadata: bool,
    pub supports_file_listing: bool,
    pub supports_bulk_access: bool,
    pub supports_delta_or_feed: bool,
    pub supports_live_probe: bool,
    pub supports_member_listing: bool,
    pub supports_reviews_or_comments: bool,
    pub supports_hashes: bool,
    pub supports_signatures: bool,
    pub supports_content_text: bool,
    pub supports_temporal_captures: bool,
    pub supports_action_paths: bool,
    pub auth_required: bool,
    pub network_required: bool,
    pub local_private: bool,
    pub fixture_backed: bool,
    pub recorded_fixture_backed: bool,
    pub live_supported: bool,
    pub live_deferred: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SourceCoverageRecord {
    pub coverage_depth: String,
    pub coverage_status: String,
    pub indexed_scopes: Vec<String>,
    pub connector_mode: String,
    pub last_fixture_update: String,
    pub coverage_notes: String,
    pub current_limitations: Vec<String>,
    pub next_coverage_step: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct SourceRecord {
    pub source_id: String,
    pub name: String,
    pub source_family: String,
    pub status: String,
    pub roles: Vec<String>,
    pub surfaces: Vec<String>,
    pub trust_lane: String,
    pub authority_class: String,
    pub protocols: Vec<String>,
    pub object_types: Vec<String>,
    pub artifact_types: Vec<String>,
    pub identifier_types_emitted: Vec<String>,
    pub connector: ConnectorRecord,
    pub fixture_paths: Vec<String>,
    pub live_access: LiveAccessRecord,
    pub extraction_policy: ExtractionPolicyRecord,
    pub rights_notes: String,
    pub legal_posture: String,
    pub freshness_model: String,
    pub capabilities: SourceCapabilityRecord,
    pub coverage: SourceCoverageRecord,
    pub notes: String,
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct SourceFilter {
    pub status: Option<String>,
    pub source_family: Option<String>,
    pub role: Option<String>,
    pub surface: Option<String>,
    pub coverage_depth: Option<String>,
    pub capability: Option<String>,
    pub connector_mode: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SourceRegistry {
    records: Vec<SourceRecord>,
}

impl SourceRegistry {
    pub fn new(mut records: Vec<SourceRecord>) -> Result<Self, SourceRegistryError> {
        records.sort_by(|left, right| left.source_id.cmp(&right.source_id));
        let mut seen: BTreeMap<String, usize> = BTreeMap::new();
        for (index, record) in records.iter().enumerate() {
            record.validate()?;
            if seen.insert(record.source_id.clone(), index).is_some() {
                return Err(SourceRegistryError::DuplicateSourceId {
                    source_id: record.source_id.clone(),
                });
            }
        }
        Ok(Self { records })
    }

    pub fn records(&self) -> &[SourceRecord] {
        &self.records
    }

    pub fn list_records(&self, filter: SourceFilter) -> Vec<&SourceRecord> {
        self.records
            .iter()
            .filter(|record| {
                filter
                    .status
                    .as_ref()
                    .map_or(true, |status| &record.status == status)
                    && filter
                        .source_family
                        .as_ref()
                        .map_or(true, |family| &record.source_family == family)
                    && filter
                        .role
                        .as_ref()
                        .map_or(true, |role| record.roles.iter().any(|item| item == role))
                    && filter
                        .surface
                        .as_ref()
                        .map_or(true, |surface| record.surfaces.iter().any(|item| item == surface))
                    && filter
                        .coverage_depth
                        .as_ref()
                        .map_or(true, |depth| &record.coverage.coverage_depth == depth)
                    && filter
                        .capability
                        .as_ref()
                        .map_or(true, |capability| record.capabilities.supports(capability))
                    && filter
                        .connector_mode
                        .as_ref()
                        .map_or(true, |mode| &record.coverage.connector_mode == mode)
            })
            .collect()
    }

    pub fn get_record(&self, source_id: &str) -> Option<&SourceRecord> {
        self.records
            .binary_search_by(|record| record.source_id.as_str().cmp(source_id))
            .ok()
            .map(|index| &self.records[index])
    }
}

impl SourceRecord {
    pub fn validate(&self) -> Result<(), SourceRegistryError> {
        require_non_empty("source_id", &self.source_id)?;
        require_non_empty("name", &self.name)?;
        require_non_empty("source_family", &self.source_family)?;
        require_non_empty("status", &self.status)?;
        require_non_empty_list("roles", &self.roles)?;
        require_non_empty_list("surfaces", &self.surfaces)?;
        require_non_empty("trust_lane", &self.trust_lane)?;
        require_non_empty("authority_class", &self.authority_class)?;
        require_non_empty_list("protocols", &self.protocols)?;
        require_non_empty_list("object_types", &self.object_types)?;
        require_non_empty_list("artifact_types", &self.artifact_types)?;
        require_non_empty_list("identifier_types_emitted", &self.identifier_types_emitted)?;
        require_non_empty("connector.label", &self.connector.label)?;
        require_non_empty("connector.status", &self.connector.status)?;
        require_optional_non_empty("connector.entrypoint", &self.connector.entrypoint)?;
        require_non_empty("live_access.mode", &self.live_access.mode)?;
        require_optional_non_empty("live_access.notes", &self.live_access.notes)?;
        require_non_empty("extraction_policy.mode", &self.extraction_policy.mode)?;
        require_optional_non_empty("extraction_policy.notes", &self.extraction_policy.notes)?;
        require_non_empty("legal_posture", &self.legal_posture)?;
        require_non_empty("freshness_model", &self.freshness_model)?;
        self.capabilities.validate()?;
        self.coverage.validate()?;
        Ok(())
    }
}

impl SourceCapabilityRecord {
    pub fn enabled_capabilities(&self) -> Vec<&'static str> {
        SOURCE_CAPABILITY_FIELDS
            .iter()
            .copied()
            .filter(|capability| self.supports(capability))
            .collect()
    }

    pub fn supports(&self, capability_name: &str) -> bool {
        match capability_name {
            "supports_search" => self.supports_search,
            "supports_item_metadata" => self.supports_item_metadata,
            "supports_file_listing" => self.supports_file_listing,
            "supports_bulk_access" => self.supports_bulk_access,
            "supports_delta_or_feed" => self.supports_delta_or_feed,
            "supports_live_probe" => self.supports_live_probe,
            "supports_member_listing" => self.supports_member_listing,
            "supports_reviews_or_comments" => self.supports_reviews_or_comments,
            "supports_hashes" => self.supports_hashes,
            "supports_signatures" => self.supports_signatures,
            "supports_content_text" => self.supports_content_text,
            "supports_temporal_captures" => self.supports_temporal_captures,
            "supports_action_paths" => self.supports_action_paths,
            "auth_required" => self.auth_required,
            "network_required" => self.network_required,
            "local_private" => self.local_private,
            "fixture_backed" => self.fixture_backed,
            "recorded_fixture_backed" => self.recorded_fixture_backed,
            "live_supported" => self.live_supported,
            "live_deferred" => self.live_deferred,
            _ => false,
        }
    }

    pub fn validate(&self) -> Result<(), SourceRegistryError> {
        Ok(())
    }
}

impl SourceCoverageRecord {
    pub fn validate(&self) -> Result<(), SourceRegistryError> {
        require_non_empty("coverage.coverage_depth", &self.coverage_depth)?;
        if !COVERAGE_DEPTHS.contains(&self.coverage_depth.as_str()) {
            return Err(SourceRegistryError::InvalidCoverageDepth {
                coverage_depth: self.coverage_depth.clone(),
            });
        }
        require_non_empty("coverage.coverage_status", &self.coverage_status)?;
        require_string_list("coverage.indexed_scopes", &self.indexed_scopes)?;
        require_non_empty("coverage.connector_mode", &self.connector_mode)?;
        require_non_empty("coverage.last_fixture_update", &self.last_fixture_update)?;
        require_string_list("coverage.current_limitations", &self.current_limitations)?;
        Ok(())
    }
}

pub fn load_source_registry(
    inventory_dir: impl AsRef<Path>,
) -> Result<SourceRegistry, SourceRegistryError> {
    let inventory_dir = inventory_dir.as_ref();
    if !inventory_dir.is_dir() {
        return Err(SourceRegistryError::InventoryNotFound {
            path: inventory_dir.to_path_buf(),
        });
    }

    let mut source_paths = Vec::new();
    for entry in fs::read_dir(inventory_dir).map_err(|error| SourceRegistryError::ReadDirectory {
        path: inventory_dir.to_path_buf(),
        message: error.to_string(),
    })? {
        let entry = entry.map_err(|error| SourceRegistryError::ReadDirectory {
            path: inventory_dir.to_path_buf(),
            message: error.to_string(),
        })?;
        let path = entry.path();
        if path
            .file_name()
            .and_then(|name| name.to_str())
            .map_or(false, |name| name.ends_with(".source.json"))
        {
            source_paths.push(path);
        }
    }
    source_paths.sort();

    let mut records = Vec::new();
    for source_path in source_paths {
        records.push(load_source_record(&source_path)?);
    }
    SourceRegistry::new(records)
}

pub fn load_source_record(
    source_path: impl AsRef<Path>,
) -> Result<SourceRecord, SourceRegistryError> {
    let source_path = source_path.as_ref();
    let text = fs::read_to_string(source_path).map_err(|error| SourceRegistryError::ReadRecord {
        path: source_path.to_path_buf(),
        message: error.to_string(),
    })?;
    let record: SourceRecord =
        serde_json::from_str(&text).map_err(|error| SourceRegistryError::MalformedRecord {
            path: source_path.to_path_buf(),
            message: error.to_string(),
        })?;
    record.validate()?;
    Ok(record)
}

pub fn list_sources_response(registry: &SourceRegistry) -> Value {
    let records: Vec<&SourceRecord> = registry.list_records(SourceFilter::default());
    json!({
        "status_code": 200,
        "body": source_registry_envelope(&records, None, None),
    })
}

pub fn source_response(registry: &SourceRegistry, source_id: &str) -> Value {
    match registry.get_record(source_id) {
        Some(record) => {
            let records = vec![record];
            json!({
                "status_code": 200,
                "body": source_registry_envelope(&records, None, Some(source_id)),
            })
        }
        None => json!({
            "status_code": 404,
            "body": {
                "status": "blocked",
                "source_count": 0,
                "selected_source_id": source_id,
                "sources": [],
                "notices": [{
                    "code": "source_id_not_found",
                    "severity": "warning",
                    "message": format!("Unknown source_id '{}'.", source_id),
                }],
            },
        }),
    }
}

pub fn source_registry_envelope(
    records: &[&SourceRecord],
    applied_filters: Option<BTreeMap<String, String>>,
    selected_source_id: Option<&str>,
) -> Value {
    let mut body = serde_json::Map::new();
    body.insert(
        "status".to_string(),
        Value::String(if selected_source_id.is_some() {
            "available".to_string()
        } else {
            "listed".to_string()
        }),
    );
    body.insert(
        "source_count".to_string(),
        Value::Number(serde_json::Number::from(records.len())),
    );
    body.insert(
        "sources".to_string(),
        Value::Array(
            records
                .iter()
                .map(|record| source_record_public_entry(*record))
                .collect(),
        ),
    );
    if let Some(filters) = applied_filters {
        if !filters.is_empty() {
            body.insert("applied_filters".to_string(), json!(filters));
        }
    }
    if let Some(source_id) = selected_source_id {
        body.insert(
            "selected_source_id".to_string(),
            Value::String(source_id.to_string()),
        );
    }
    Value::Object(body)
}

pub fn source_record_public_entry(record: &SourceRecord) -> Value {
    json!({
        "source_id": &record.source_id,
        "name": &record.name,
        "source_family": &record.source_family,
        "status": &record.status,
        "status_summary": status_summary(record),
        "roles": &record.roles,
        "surfaces": &record.surfaces,
        "trust_lane": &record.trust_lane,
        "authority_class": &record.authority_class,
        "object_types": &record.object_types,
        "artifact_types": &record.artifact_types,
        "identifier_types_emitted": &record.identifier_types_emitted,
        "connector": {
            "label": &record.connector.label,
            "status": &record.connector.status,
        },
        "capabilities": &record.capabilities,
        "capabilities_summary": record.capabilities.enabled_capabilities(),
        "coverage": &record.coverage,
        "coverage_depth": &record.coverage.coverage_depth,
        "coverage_status": &record.coverage.coverage_status,
        "connector_mode": &record.coverage.connector_mode,
        "indexed_scopes": &record.coverage.indexed_scopes,
        "current_limitations": &record.coverage.current_limitations,
        "next_coverage_step": &record.coverage.next_coverage_step,
        "placeholder_warning": placeholder_warning(record),
        "live_access_mode": &record.live_access.mode,
        "extraction_mode": &record.extraction_policy.mode,
        "legal_posture": &record.legal_posture,
        "freshness_model": &record.freshness_model,
        "rights_notes": &record.rights_notes,
        "notes": &record.notes,
    })
}

pub fn status_summary(record: &SourceRecord) -> &'static str {
    match record.status.as_str() {
        "active_fixture" => "Active fixture-backed source record.",
        "active_recorded_fixture" => {
            "Active recorded-fixture source record. Live source access remains separate."
        }
        "placeholder" => "Placeholder record only. No runtime connector is implemented yet.",
        "future" => "Future source record only. Runtime behavior remains deferred.",
        "local_private_future" => {
            "Future local/private source record only. Runtime behavior remains deferred."
        }
        "live_deferred" => "Registered source record with live access deferred.",
        _ => "Disabled source record.",
    }
}

pub fn placeholder_warning(record: &SourceRecord) -> &'static str {
    match record.status.as_str() {
        "placeholder" => "Placeholder only; no connector, fixture coverage, or live access is implemented.",
        "future" | "local_private_future" => "Future-only source; no runtime connector is implemented.",
        _ if record.connector.status == "unimplemented" || record.connector.status == "deferred" => {
            "Connector is not implemented for current runtime behavior."
        }
        _ => "",
    }
}

#[derive(Debug, Eq, PartialEq)]
pub enum SourceRegistryError {
    InventoryNotFound { path: PathBuf },
    ReadDirectory { path: PathBuf, message: String },
    ReadRecord { path: PathBuf, message: String },
    MalformedRecord { path: PathBuf, message: String },
    MissingRequiredField { field_name: String },
    EmptyRequiredField { field_name: String },
    EmptyRequiredList { field_name: String },
    InvalidCoverageDepth { coverage_depth: String },
    DuplicateSourceId { source_id: String },
}

impl fmt::Display for SourceRegistryError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SourceRegistryError::InventoryNotFound { path } => {
                write!(formatter, "Source inventory directory '{}' was not found.", path.display())
            }
            SourceRegistryError::ReadDirectory { path, message } => {
                write!(
                    formatter,
                    "Could not read source inventory directory '{}': {}",
                    path.display(),
                    message
                )
            }
            SourceRegistryError::ReadRecord { path, message } => {
                write!(formatter, "{}: could not read source record: {}", path.display(), message)
            }
            SourceRegistryError::MalformedRecord { path, message } => {
                write!(formatter, "{}: malformed source record: {}", path.display(), message)
            }
            SourceRegistryError::MissingRequiredField { field_name } => {
                write!(formatter, "Missing required field '{}'.", field_name)
            }
            SourceRegistryError::EmptyRequiredField { field_name } => {
                write!(formatter, "Field '{}' must be a non-empty string.", field_name)
            }
            SourceRegistryError::EmptyRequiredList { field_name } => {
                write!(
                    formatter,
                    "Field '{}' must be a non-empty list of non-empty strings.",
                    field_name
                )
            }
            SourceRegistryError::InvalidCoverageDepth { coverage_depth } => {
                write!(
                    formatter,
                    "Field 'coverage.coverage_depth' has unsupported value '{}'.",
                    coverage_depth
                )
            }
            SourceRegistryError::DuplicateSourceId { source_id } => {
                write!(formatter, "Duplicate source_id '{}' found.", source_id)
            }
        }
    }
}

impl Error for SourceRegistryError {}

fn require_non_empty(field_name: &str, value: &str) -> Result<(), SourceRegistryError> {
    if value.is_empty() {
        return Err(SourceRegistryError::EmptyRequiredField {
            field_name: field_name.to_string(),
        });
    }
    Ok(())
}

fn require_optional_non_empty(
    field_name: &str,
    value: &Option<String>,
) -> Result<(), SourceRegistryError> {
    if value.as_ref().map_or(false, |item| item.is_empty()) {
        return Err(SourceRegistryError::EmptyRequiredField {
            field_name: field_name.to_string(),
        });
    }
    Ok(())
}

fn require_non_empty_list(field_name: &str, value: &[String]) -> Result<(), SourceRegistryError> {
    if value.is_empty() || value.iter().any(|item| item.is_empty()) {
        return Err(SourceRegistryError::EmptyRequiredList {
            field_name: field_name.to_string(),
        });
    }
    Ok(())
}

fn require_string_list(field_name: &str, value: &[String]) -> Result<(), SourceRegistryError> {
    if value.iter().any(|item| item.is_empty()) {
        return Err(SourceRegistryError::EmptyRequiredField {
            field_name: field_name.to_string(),
        });
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn loads_governed_inventory_records() {
        let registry = load_source_registry(repo_root().join("control/inventory/sources")).unwrap();
        let source_ids: Vec<&str> = registry
            .records()
            .iter()
            .map(|record| record.source_id.as_str())
            .collect();

        assert_eq!(source_ids.len(), 15);
        assert_eq!(source_ids.first().copied(), Some("article-scan-recorded-fixtures"));
        assert!(source_ids.contains(&"synthetic-fixtures"));
        assert!(source_ids.contains(&"github-releases-recorded-fixtures"));
        assert!(source_ids.contains(&"internet-archive-recorded-fixtures"));
        assert!(source_ids.contains(&"local-bundle-fixtures"));
        assert!(source_ids.contains(&"article-scan-recorded-fixtures"));
        assert!(source_ids.contains(&"local-files-placeholder"));
        assert!(source_ids.contains(&"manual-document-recorded-fixtures"));
        assert!(source_ids.contains(&"package-registry-recorded-fixtures"));
        assert!(source_ids.contains(&"review-description-recorded-fixtures"));
        assert!(source_ids.contains(&"software-heritage-recorded-fixtures"));
        assert!(source_ids.contains(&"sourceforge-recorded-fixtures"));
        assert!(source_ids.contains(&"wayback-memento-recorded-fixtures"));
    }

    #[test]
    fn filters_records_by_status_role_and_surface() {
        let registry = load_source_registry(repo_root().join("control/inventory/sources")).unwrap();

        let active = registry.list_records(SourceFilter {
            status: Some("active_fixture".to_string()),
            ..SourceFilter::default()
        });
        assert_eq!(active.len(), 2);

        let recorded = registry.list_records(SourceFilter {
            status: Some("active_recorded_fixture".to_string()),
            ..SourceFilter::default()
        });
        assert_eq!(recorded.len(), 9);

        let member_listing = registry.list_records(SourceFilter {
            capability: Some("supports_member_listing".to_string()),
            ..SourceFilter::default()
        });
        let member_source_ids: Vec<&str> = member_listing
            .iter()
            .map(|record| record.source_id.as_str())
            .collect();
        assert_eq!(
            member_source_ids,
            vec![
                "article-scan-recorded-fixtures",
                "local-bundle-fixtures",
                "package-registry-recorded-fixtures",
                "synthetic-fixtures"
            ]
        );

        let fixture_search = registry.list_records(SourceFilter {
            role: Some("fixture".to_string()),
            surface: Some("fixture_file".to_string()),
            ..SourceFilter::default()
        });
        let source_ids: Vec<&str> = fixture_search
            .iter()
            .map(|record| record.source_id.as_str())
            .collect();
        assert_eq!(
            source_ids,
            vec![
                "article-scan-recorded-fixtures",
                "github-releases-recorded-fixtures",
                "internet-archive-recorded-fixtures",
                "local-bundle-fixtures",
                "manual-document-recorded-fixtures",
                "package-registry-recorded-fixtures",
                "review-description-recorded-fixtures",
                "software-heritage-recorded-fixtures",
                "sourceforge-recorded-fixtures",
                "synthetic-fixtures",
                "wayback-memento-recorded-fixtures"
            ]
        );
    }

    #[test]
    fn detects_duplicate_source_ids() {
        let temp_root = unique_temp_dir();
        fs::create_dir_all(&temp_root).unwrap();

        let source = fs::read_to_string(
            repo_root().join("control/inventory/sources/synthetic-fixtures.source.json"),
        )
        .unwrap();
        fs::write(temp_root.join("a.source.json"), &source).unwrap();
        fs::write(temp_root.join("b.source.json"), &source).unwrap();

        let error = load_source_registry(&temp_root).unwrap_err();
        fs::remove_dir_all(&temp_root).unwrap();

        assert_eq!(
            error,
            SourceRegistryError::DuplicateSourceId {
                source_id: "synthetic-fixtures".to_string(),
            }
        );
    }

    #[test]
    fn list_output_matches_python_oracle_golden() {
        let registry = load_source_registry(repo_root().join("control/inventory/sources")).unwrap();
        let observed = list_sources_response(&registry);
        let expected = load_golden("sources_list.json");

        assert_eq!(observed, expected);
    }

    #[test]
    fn synthetic_source_output_matches_python_oracle_golden() {
        let registry = load_source_registry(repo_root().join("control/inventory/sources")).unwrap();
        let observed = source_response(&registry, "synthetic-fixtures");
        let expected = load_golden("source_synthetic_fixtures.json");

        assert_eq!(observed, expected);
    }

    #[test]
    fn github_source_output_matches_python_oracle_golden() {
        let registry = load_source_registry(repo_root().join("control/inventory/sources")).unwrap();
        let observed = source_response(&registry, "github-releases-recorded-fixtures");
        let expected = load_golden("source_github_releases_recorded_fixtures.json");

        assert_eq!(observed, expected);
    }

    #[test]
    fn current_source_outputs_match_python_oracle_goldens() {
        let registry = load_source_registry(repo_root().join("control/inventory/sources")).unwrap();
        for (source_id, golden_file) in [
            ("internet-archive-recorded-fixtures", "source_internet_archive_recorded_fixtures.json"),
            ("local-bundle-fixtures", "source_local_bundle_fixtures.json"),
            ("article-scan-recorded-fixtures", "source_article_scan_recorded_fixtures.json"),
            ("internet-archive-placeholder", "source_internet_archive_placeholder.json"),
            ("local-files-placeholder", "source_local_files_placeholder.json"),
            ("wayback-memento-placeholder", "source_wayback_memento_placeholder.json"),
            ("software-heritage-placeholder", "source_software_heritage_placeholder.json"),
        ] {
            let observed = source_response(&registry, source_id);
            let expected = load_golden(golden_file);
            assert_eq!(observed, expected);
        }
    }

    fn load_golden(file_name: &str) -> Value {
        let path = repo_root()
            .join("tests/parity/golden/python_oracle/v0/source_registry")
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

    fn unique_temp_dir() -> PathBuf {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!(
            "eureka-source-registry-parity-{}-{}",
            std::process::id(),
            stamp
        ))
    }
}
