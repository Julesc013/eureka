"""Fixture-only H7 library/cultural/research normalization helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any


H7_SOURCE_CONFIGS: dict[str, dict[str, Any]] = {'worldcat_library_catalog': {'label': 'WorldCat / OCLC-style library catalog metadata', 'connector_family': 'library_catalog', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'oaister_oai_pmh': {'label': 'OAIster / OAI-PMH repository metadata', 'connector_family': 'oai_pmh', 'has_bibliographic': True, 'has_research_work': True, 'has_dataset': True, 'has_cultural_object': True, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'google_books': {'label': 'Google Books metadata', 'connector_family': 'api_json', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'hathitrust': {'label': 'HathiTrust metadata', 'connector_family': 'library_catalog', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'open_library': {'label': 'Open Library metadata', 'connector_family': 'api_json', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'trove_library_cultural': {'label': 'Trove library/cultural metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'europeana': {'label': 'Europeana metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'dpla': {'label': 'Digital Public Library of America metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'gallica_bnf': {'label': 'Gallica / BnF metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'library_of_congress': {'label': 'Library of Congress metadata', 'connector_family': 'library_catalog', 'has_bibliographic': True, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'nara_catalog': {'label': 'NARA catalog metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'national_archives_australia': {'label': 'National Archives of Australia metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'uk_national_archives_discovery': {'label': 'UK National Archives Discovery metadata', 'connector_family': 'cultural_repository', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': False, 'has_access_rights': True}, 'govinfo': {'label': 'govinfo metadata', 'connector_family': 'api_json', 'has_bibliographic': True, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': True, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'openalex': {'label': 'OpenAlex metadata', 'connector_family': 'research_graph', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'crossref': {'label': 'Crossref metadata', 'connector_family': 'research_graph', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'datacite': {'label': 'DataCite metadata', 'connector_family': 'research_graph', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': True, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'arxiv': {'label': 'arXiv metadata', 'connector_family': 'research_repository', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'pubmed': {'label': 'PubMed metadata', 'connector_family': 'api_json', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'pubmed_central': {'label': 'PubMed Central metadata', 'connector_family': 'research_repository', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'doaj': {'label': 'DOAJ metadata', 'connector_family': 'api_json', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'zenodo': {'label': 'Zenodo metadata', 'connector_family': 'dataset_repository', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': True, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'repec': {'label': 'RePEc metadata', 'connector_family': 'research_repository', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'ssrn': {'label': 'SSRN metadata', 'connector_family': 'research_repository', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'semantic_scholar': {'label': 'Semantic Scholar metadata', 'connector_family': 'research_graph', 'has_bibliographic': False, 'has_research_work': True, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'kaggle_datasets': {'label': 'Kaggle dataset metadata', 'connector_family': 'dataset_repository', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': True, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'deep_blue_repository': {'label': 'Deep Blue / institutional repository metadata', 'connector_family': 'research_repository', 'has_bibliographic': True, 'has_research_work': True, 'has_dataset': True, 'has_cultural_object': False, 'has_patent': False, 'has_citation': True, 'has_access_rights': True}, 'google_patents': {'label': 'Google Patents / public patent metadata', 'connector_family': 'patent_metadata', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': True, 'has_citation': True, 'has_access_rights': True}, 'wipo_patentscope': {'label': 'WIPO PATENTSCOPE metadata', 'connector_family': 'patent_metadata', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': True, 'has_citation': True, 'has_access_rights': True}, 'uspto_patents': {'label': 'USPTO patent metadata', 'connector_family': 'patent_metadata', 'has_bibliographic': False, 'has_research_work': False, 'has_dataset': False, 'has_cultural_object': False, 'has_patent': True, 'has_citation': True, 'has_access_rights': True}}
H7_SOURCE_IDS = tuple(H7_SOURCE_CONFIGS)
H7_FIXTURE_KINDS = ('minimal', 'identity', 'relation', 'access_rights', 'repository_or_collection', 'policy_blocked')

FIXTURE_FORBIDDEN_TRUE_KEYS = {
    "live_call_used",
    "network_used",
    "external_api_used",
    "full_text_payload_included",
    "pdf_payload_included",
    "book_scan_payload_included",
    "article_payload_included",
    "dataset_payload_included",
    "patent_document_payload_included",
    "iiif_payload_included",
    "media_payload_included",
    "scraping_output_included",
    "crawling_output_included",
    "restricted_source_accessed",
    "bypass_or_automation_used",
}

FORBIDDEN_TRUTH_TRUE_KEYS = {'master_index_mutated', 'access_metadata_is_rights_truth', 'open_access_metadata_is_rights_clearance', 'accepted_cultural_object_truth', 'patent_identity_candidate_is_truth', 'accepted_patent_truth', 'citation_correctness_verified', 'patent_validity_verified', 'normalized_record_is_public_truth', 'production_readiness_claimed', 'accepted_source_truth', 'source_cache_preview_is_accepted_source', 'dataset_identity_candidate_is_truth', 'citation_relation_candidate_is_truth', 'accepted_access_rights_truth', 'rights_clearance_claimed', 'accepted_candidate_truth', 'cultural_object_candidate_is_truth', 'evidence_preview_is_accepted_evidence', 'landing_page_grants_download_permission', 'malware_safety_claimed', 'verified_availability_claimed', 'accepted_bibliographic_truth', 'privacy_safety_claimed', 'research_work_candidate_is_truth', 'dataset_validity_verified', 'bibliographic_identity_candidate_is_truth', 'bibliographic_completeness_claimed', 'accepted_evidence_truth', 'open_access_truth_claimed', 'accepted_public_record', 'full_text_availability_verified', 'public_index_mutated', 'accepted_dataset_truth', 'accepted_research_work_truth', 'accepted_citation_truth'}
FORBIDDEN_PRODUCT_TRUE_KEYS = {'enabled_telemetry', 'patent_document_download_used', 'network_calls_made', 'media_download_used', 'changed_public_search_behavior', 'iiif_fetch_used', 'enabled_crawling', 'oai_pmh_harvest_used', 'full_text_fetch_used', 'enabled_uploads', 'enabled_accounts', 'pdf_download_used', 'article_download_used', 'enabled_live_probes', 'enabled_harvesting', 'enabled_downloads', 'api_calls_made', 'enabled_source_sync', 'bypass_or_automation_used', 'restricted_source_access_used', 'scraping_used', 'crawling_used', 'book_scan_download_used', 'dataset_download_used', 'browser_automation_used', 'mutated_master_index', 'enabled_hosting', 'mutated_public_index', 'doi_isbn_patent_query_used'}


def normalize_h7_library_research_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if source_id not in H7_SOURCE_CONFIGS:
        raise ValueError(f"unknown H7 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError(f"fixture source_id does not match requested source_id: {source_id}")
    _require_fixture_boundaries(raw_fixture)
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    config = H7_SOURCE_CONFIGS[source_id]
    native_id = _text(payload.get("source_native_id")) or _text(payload.get("catalog_record_id")) or f"fixture-{source_id}"
    limitations = list(raw_fixture.get("limitations") or [])
    limitations.extend(_missing_optional_limitations(payload))
    if raw_fixture.get("fixture_status") == "policy_blocked":
        limitations.append("fixture is policy-blocked and remains candidate-only")
    record: dict[str, Any] = {
        "schema_version": "h7_library_research_normalized_record.v0",
        "normalized_record_id": f"h7.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": str(raw_fixture.get("connector_family") or config["connector_family"]),
        "source_record_kind": _text(payload.get("source_record_kind")) or _text(raw_fixture.get("fixture_kind")) or "unknown",
        "title": _text(payload.get("title")) or "unknown",
        "subtitle": _text(payload.get("subtitle")) or "unknown",
        "creators": _list(payload.get("creators")),
        "contributors": _list(payload.get("contributors")),
        "publisher_or_institution": _text(payload.get("publisher_or_institution")) or "unknown",
        "publication_or_creation_date": _text(payload.get("publication_or_creation_date")) or "unknown",
        "language": _text(payload.get("language")) or "unknown",
        "format_or_medium": _text(payload.get("format_or_medium")) or "unknown",
        "identifiers": _list(payload.get("identifiers")),
        "source_native_id": native_id,
        "catalog_record_id": _text(payload.get("catalog_record_id")) or "unknown",
        "doi_candidate": _text(payload.get("doi_candidate")) or "unknown",
        "isbn_candidate": _text(payload.get("isbn_candidate")) or "unknown",
        "issn_candidate": _text(payload.get("issn_candidate")) or "unknown",
        "oclc_candidate": _text(payload.get("oclc_candidate")) or "unknown",
        "lccn_candidate": _text(payload.get("lccn_candidate")) or "unknown",
        "openalex_id_candidate": _text(payload.get("openalex_id_candidate")) or "unknown",
        "crossref_id_candidate": _text(payload.get("crossref_id_candidate")) or "unknown",
        "datacite_id_candidate": _text(payload.get("datacite_id_candidate")) or "unknown",
        "pmid_candidate": _text(payload.get("pmid_candidate")) or "unknown",
        "pmcid_candidate": _text(payload.get("pmcid_candidate")) or "unknown",
        "arxiv_id_candidate": _text(payload.get("arxiv_id_candidate")) or "unknown",
        "dataset_id_candidate": _text(payload.get("dataset_id_candidate")) or "unknown",
        "patent_number_candidate": _text(payload.get("patent_number_candidate")) or "unknown",
        "collection_or_repository_ref": _text(payload.get("collection_or_repository_ref")) or "unknown",
        "subject_or_classification": _list(payload.get("subject_or_classification")),
        "citation_or_relation_summary": _text(payload.get("citation_or_relation_summary")) or "unknown",
        "access_rights_availability_summary": _text(payload.get("access_rights_availability_summary")) or "unknown",
        "license_metadata_candidate": _text(payload.get("license_metadata_candidate")) or "unknown",
        "landing_page_candidate": _text(payload.get("landing_page_candidate")) or "unknown",
        "access_status_candidate": _text(payload.get("access_status_candidate")) or "unknown",
        "relations": _list(payload.get("relations")),
        "access": _mapping(payload.get("access"), "access", default={}),
        "source_metadata": _mapping(payload.get("source_metadata"), "source_metadata", default={}),
        "metadata_summary": _text(payload.get("metadata_summary")) or "fixture-only metadata summary",
        "source_limitations": _dedupe(limitations),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Fixture-only H7 normalized record; review is required before any downstream use."],
    }
    record["bibliographic_identity_candidate"] = build_h7_bibliographic_identity_candidate(record, policy)
    record["research_work_identity_candidate"] = build_h7_research_work_identity_candidate(record, policy)
    record["dataset_identity_candidate"] = build_h7_dataset_identity_candidate(record, policy)
    record["cultural_object_identity_candidate"] = build_h7_cultural_object_identity_candidate(record, policy)
    record["patent_identity_candidate"] = build_h7_patent_identity_candidate(record, policy)
    record["citation_relation_candidate"] = build_h7_citation_relation_candidates(record, policy)
    record["access_rights_availability_candidate"] = build_h7_access_rights_availability_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h7_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h7_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h7_bibliographic_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("title", "subtitle", "creators", "contributors", "publisher_or_institution", "publication_or_creation_date", "language", "format_or_medium", "isbn_candidate", "issn_candidate", "oclc_candidate", "lccn_candidate", "catalog_record_id", "subject_or_classification")
    return _candidate(normalized_record, "h7_bibliographic_identity_candidate.v0", "bibliographic", fields, "Bibliographic identity candidate is not accepted bibliographic truth, ISBN/OCLC/LCCN truth, holdings truth, or rights clearance.")


def build_h7_research_work_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("title", "creators", "contributors", "publisher_or_institution", "publication_or_creation_date", "doi_candidate", "pmid_candidate", "pmcid_candidate", "arxiv_id_candidate", "openalex_id_candidate", "crossref_id_candidate", "datacite_id_candidate", "citation_or_relation_summary")
    return _candidate(normalized_record, "h7_research_work_identity_candidate.v0", "research_work", fields, "Research work identity candidate is not accepted work truth, citation truth, article truth, or open-access rights clearance.")


def build_h7_dataset_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("title", "creators", "collection_or_repository_ref", "dataset_id_candidate", "datacite_id_candidate", "doi_candidate", "source_native_id", "license_metadata_candidate")
    return _candidate(normalized_record, "h7_dataset_identity_candidate.v0", "dataset", fields, "Dataset identity candidate is not dataset validity truth, download permission, rights clearance, or malware safety.")


def build_h7_cultural_object_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("title", "creators", "publisher_or_institution", "collection_or_repository_ref", "catalog_record_id", "format_or_medium", "subject_or_classification", "license_metadata_candidate")
    return _candidate(normalized_record, "h7_cultural_object_identity_candidate.v0", "cultural_object", fields, "Cultural object candidate is not accepted object truth, collection completeness, rights clearance, or media fetch permission.")


def build_h7_patent_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("title", "patent_number_candidate", "publication_or_creation_date", "creators", "contributors", "subject_or_classification", "source_native_id")
    return _candidate(normalized_record, "h7_patent_identity_candidate.v0", "patent", fields, "Patent identity candidate is not patent validity, legal status, enforceability, or patent document download permission.")


def build_h7_citation_relation_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fields = ("citation_or_relation_summary", "relations", "doi_candidate", "openalex_id_candidate", "crossref_id_candidate", "datacite_id_candidate", "patent_number_candidate")
    candidate = _candidate(normalized_record, "h7_citation_relation_candidate.v0", "citation_relation", fields, "Citation relation candidate is not citation correctness, impact proof, or same-work clustering truth.")
    return [candidate]


def build_h7_access_rights_availability_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fields = ("access_rights_availability_summary", "access", "license_metadata_candidate", "landing_page_candidate", "access_status_candidate", "collection_or_repository_ref")
    return _candidate(normalized_record, "h7_access_rights_availability_candidate.v0", "access_rights", fields, "Access, rights, and availability candidate is not rights clearance, open-access truth, verified availability, or download permission.")


def build_h7_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h7_library_research_source_cache_candidate_preview.v0",
        "source_cache_candidate_preview_id": f"h7.source_cache_preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "persistence_allowed_current": False,
        "supporting_fields": [field for field in ("title", "source_native_id", "connector_family", "source_record_kind") if _is_present(normalized_record.get(field))],
        "limitations": ["Source-cache candidate preview only; no source cache mutation or accepted source truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h7_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h7_library_research_evidence_candidate_preview.v0",
        "evidence_candidate_preview_id": f"h7.evidence_preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "evidence_ledger_write_allowed_current": False,
        "supporting_fields": [field for field in ("title", "identifiers", "metadata_summary") if _is_present(normalized_record.get(field))],
        "limitations": ["Evidence candidate preview only; no evidence ledger mutation or accepted evidence truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h7_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    status = "blocked_by_policy_fixture" if fixture.get("fixture_status") == "policy_blocked" else "fixture_replayed"
    result = {
        "schema_version": "h7_library_research_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h7.replay.{fixture.get('source_id')}.{_slug(fixture.get('fixture_id'))}.v0",
        "fixture_ref": fixture.get("fixture_id"),
        "source_id": fixture.get("source_id"),
        "connector_family": fixture.get("connector_family"),
        "fixture_kind": fixture.get("fixture_kind"),
        "replay_status": status,
        "normalized_record": dict(normalized_record),
        "bibliographic_identity_candidate": normalized_record.get("bibliographic_identity_candidate", {}),
        "research_work_identity_candidate": normalized_record.get("research_work_identity_candidate", {}),
        "dataset_identity_candidate": normalized_record.get("dataset_identity_candidate", {}),
        "cultural_object_identity_candidate": normalized_record.get("cultural_object_identity_candidate", {}),
        "patent_identity_candidate": normalized_record.get("patent_identity_candidate", {}),
        "citation_relation_candidate": normalized_record.get("citation_relation_candidate", []),
        "access_rights_availability_candidate": normalized_record.get("access_rights_availability_candidate", {}),
        "source_cache_candidate_preview": normalized_record.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": normalized_record.get("evidence_candidate_preview", {}),
        "no_network_used": True,
        "no_live_source_used": True,
        "no_oai_pmh_harvest_used": True,
        "no_api_query_used": True,
        "no_harvest_query_fetch_download_used": True,
        "no_full_text_or_pdf_fetch_used": True,
        "no_dataset_or_patent_download_used": True,
        "no_iiif_or_media_fetch_used": True,
        "no_scraping_crawling_used": True,
        "no_restricted_source_access_used": True,
        "warnings": [],
        "limitations": ["Fixture replay result is a candidate-only offline parser proof, not accepted truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h7_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h7_library_research_normalized_record_summary.v0",
        "source_id": record.get("source_id"),
        "normalized_record_id": record.get("normalized_record_id"),
        "title": record.get("title"),
        "bibliographic_candidates": 1 if record.get("bibliographic_identity_candidate") else 0,
        "research_work_candidates": 1 if record.get("research_work_identity_candidate") else 0,
        "dataset_candidates": 1 if record.get("dataset_identity_candidate") else 0,
        "cultural_object_candidates": 1 if record.get("cultural_object_identity_candidate") else 0,
        "patent_candidates": 1 if record.get("patent_identity_candidate") else 0,
        "citation_candidates": len(record.get("citation_relation_candidate", []) or []),
        "access_rights_candidates": 1 if record.get("access_rights_availability_candidate") else 0,
        "network_calls_made": False,
        "harvest_query_fetch_download_used": False,
    }


def detect_h7_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, "truth_boundary", FORBIDDEN_TRUTH_TRUE_KEYS)


def detect_h7_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return _detect_true_keys(record, "product_boundary", FORBIDDEN_PRODUCT_TRUE_KEYS)


def _candidate(normalized_record: Mapping[str, Any], schema_version: str, candidate_type: str, fields: tuple[str, ...], limitation: str) -> dict[str, Any]:
    source_id = str(normalized_record.get("source_id"))
    native_id = str(normalized_record.get("source_native_id") or normalized_record.get("normalized_record_id") or "unknown")
    supporting = [field for field in fields if _is_present(normalized_record.get(field))]
    candidate = {
        "schema_version": schema_version,
        "candidate_id": f"h7.{candidate_type}.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "source_record_ref": str(normalized_record.get("normalized_record_id") or "unknown"),
        "candidate_type": candidate_type,
        "candidate_fields": {field: normalized_record.get(field, "unknown") for field in fields},
        "supporting_fields": supporting,
        "missing_fields": [field for field in fields if field not in supporting],
        "confidence_or_uncertainty": "candidate_from_committed_fixture_no_truth_acceptance",
        "limitations": [limitation],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(raw_fixture: Mapping[str, Any]) -> None:
    if raw_fixture.get("schema_version") != "h7_library_research_fixture.v0":
        raise ValueError("fixture schema_version must be h7_library_research_fixture.v0")
    for key in FIXTURE_FORBIDDEN_TRUE_KEYS:
        if raw_fixture.get(key) is True:
            raise ValueError(f"H7 fixture cannot enable or include forbidden behavior: {key}")
    truth_boundary = raw_fixture.get("truth_boundary")
    if isinstance(truth_boundary, Mapping):
        errors = _detect_true_keys({"truth_boundary": truth_boundary}, "truth_boundary", FORBIDDEN_TRUTH_TRUE_KEYS)
        if errors:
            raise ValueError("; ".join(errors))
    product_boundary = raw_fixture.get("product_boundary")
    if isinstance(product_boundary, Mapping):
        errors = _detect_true_keys({"product_boundary": product_boundary}, "product_boundary", FORBIDDEN_PRODUCT_TRUE_KEYS)
        if errors:
            raise ValueError("; ".join(errors))


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h7_truth_boundary_violations(record) + detect_h7_product_boundary_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _detect_true_keys(record: Mapping[str, Any], section: str, keys: set[str]) -> list[str]:
    errors: list[str] = []
    boundary = record.get(section)
    if isinstance(boundary, Mapping):
        for key in keys:
            if boundary.get(key) is True:
                errors.append(f"{section}.{key} must remain false")
    return errors


def _truth_boundary() -> dict[str, bool]:
    return {'normalized_record_is_public_truth': False, 'accepted_source_truth': False, 'accepted_evidence_truth': False, 'accepted_candidate_truth': False, 'accepted_bibliographic_truth': False, 'accepted_research_work_truth': False, 'accepted_dataset_truth': False, 'accepted_cultural_object_truth': False, 'accepted_patent_truth': False, 'accepted_citation_truth': False, 'accepted_access_rights_truth': False, 'accepted_public_record': False, 'bibliographic_identity_candidate_is_truth': False, 'research_work_candidate_is_truth': False, 'dataset_identity_candidate_is_truth': False, 'cultural_object_candidate_is_truth': False, 'patent_identity_candidate_is_truth': False, 'citation_relation_candidate_is_truth': False, 'access_metadata_is_rights_truth': False, 'open_access_metadata_is_rights_clearance': False, 'landing_page_grants_download_permission': False, 'source_cache_preview_is_accepted_source': False, 'evidence_preview_is_accepted_evidence': False, 'bibliographic_completeness_claimed': False, 'citation_correctness_verified': False, 'dataset_validity_verified': False, 'patent_validity_verified': False, 'full_text_availability_verified': False, 'public_index_mutated': False, 'master_index_mutated': False, 'rights_clearance_claimed': False, 'open_access_truth_claimed': False, 'privacy_safety_claimed': False, 'malware_safety_claimed': False, 'verified_availability_claimed': False, 'production_readiness_claimed': False}.copy()


def _product_boundary() -> dict[str, bool]:
    return {'network_calls_made': False, 'api_calls_made': False, 'oai_pmh_harvest_used': False, 'doi_isbn_patent_query_used': False, 'full_text_fetch_used': False, 'pdf_download_used': False, 'book_scan_download_used': False, 'article_download_used': False, 'dataset_download_used': False, 'patent_document_download_used': False, 'iiif_fetch_used': False, 'media_download_used': False, 'scraping_used': False, 'crawling_used': False, 'browser_automation_used': False, 'bypass_or_automation_used': False, 'restricted_source_access_used': False, 'changed_public_search_behavior': False, 'enabled_hosting': False, 'enabled_live_probes': False, 'enabled_source_sync': False, 'enabled_harvesting': False, 'enabled_downloads': False, 'enabled_crawling': False, 'enabled_uploads': False, 'enabled_accounts': False, 'enabled_telemetry': False, 'mutated_public_index': False, 'mutated_master_index': False}.copy()


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    optional = ("title", "creators", "publisher_or_institution", "publication_or_creation_date", "identifiers", "doi_candidate", "isbn_candidate", "dataset_id_candidate", "patent_number_candidate", "citation_or_relation_summary", "access_rights_availability_summary")
    return [f"optional field absent or unknown: {field}" for field in optional if not _is_present(payload.get(field))]


def _mapping(value: Any, name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if value is None:
        return {} if default is None else dict(default)
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return dict(value)


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _is_present(value: Any) -> bool:
    return value not in (None, "", "unknown", [], {})


def _dedupe(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = str(item)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _slug(value: Any) -> str:
    text = str(value or "unknown").encode("utf-8", "ignore")
    return hashlib.sha256(text).hexdigest()[:16]
