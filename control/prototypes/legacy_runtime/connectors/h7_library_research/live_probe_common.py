"""Fail-closed H7 library/cultural/research metadata live-probe helpers."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import (
    H7_SOURCE_IDS as FIXTURE_H7_SOURCE_IDS,
    build_h7_access_rights_availability_candidate as _fixture_access_candidate,
    build_h7_bibliographic_identity_candidate as _fixture_bibliographic_candidate,
    build_h7_citation_relation_candidates as _fixture_citation_candidates,
    build_h7_cultural_object_identity_candidate as _fixture_cultural_candidate,
    build_h7_dataset_identity_candidate as _fixture_dataset_candidate,
    build_h7_evidence_candidate_preview as _fixture_evidence_preview,
    build_h7_patent_identity_candidate as _fixture_patent_candidate,
    build_h7_research_work_identity_candidate as _fixture_research_candidate,
    build_h7_source_cache_candidate_preview as _fixture_source_cache_preview,
    detect_h7_product_boundary_violations as _fixture_product_violations,
    detect_h7_truth_boundary_violations as _fixture_truth_violations,
    normalize_h7_library_research_fixture,
)

POLICY_PATHS = {'allowed_requests': 'control/inventory/connectors/h7_library_research_live_probe_allowed_requests.json',
 'cache_policy': 'control/inventory/connectors/h7_library_research_live_probe_cache_policy.json',
 'endpoint_policy': 'control/inventory/connectors/h7_library_research_live_probe_endpoint_policy.json',
 'kill_switch_policy': 'control/inventory/connectors/h7_library_research_live_probe_kill_switch_policy.json',
 'live_probe_policy': 'control/inventory/connectors/h7_library_research_live_probe_policy.json',
 'no_harvest_download_policy': 'control/inventory/connectors/h7_library_research_live_probe_no_harvest_download_policy.json',
 'output_policy': 'control/inventory/connectors/h7_library_research_live_probe_output_policy.json',
 'path_policy': 'control/inventory/connectors/h7_library_research_live_probe_path_policy.json',
 'rate_limit_policy': 'control/inventory/connectors/h7_library_research_live_probe_rate_limit_policy.json',
 'restricted_source_policy': 'control/inventory/connectors/h7_library_research_live_probe_restricted_source_policy.json',
 'review_policy': 'control/inventory/connectors/h7_library_research_live_probe_review_policy.json',
 'truth_policy': 'control/inventory/connectors/h7_library_research_live_probe_truth_policy.json'}
SOURCE_CONFIGS = {'arxiv': {'connector_family': 'research_repository',
           'endpoint_or_metadata_class': 'article_metadata_lookup_future',
           'has_access_rights': True,
           'has_bibliographic': False,
           'has_citation': True,
           'has_cultural_object': False,
           'has_dataset': False,
           'has_patent': False,
           'has_research_work': True,
           'label': 'arXiv metadata',
           'request_key': 'example_article_metadata',
           'source_record_kind': 'research_work_metadata'},
 'crossref': {'connector_family': 'research_graph',
              'endpoint_or_metadata_class': 'doi_metadata_lookup_future',
              'has_access_rights': True,
              'has_bibliographic': False,
              'has_citation': True,
              'has_cultural_object': False,
              'has_dataset': False,
              'has_patent': False,
              'has_research_work': True,
              'label': 'Crossref metadata',
              'request_key': 'example_doi_metadata',
              'source_record_kind': 'research_work_metadata'},
 'datacite': {'connector_family': 'research_graph',
              'endpoint_or_metadata_class': 'dataset_metadata_lookup_future',
              'has_access_rights': True,
              'has_bibliographic': False,
              'has_citation': True,
              'has_cultural_object': False,
              'has_dataset': True,
              'has_patent': False,
              'has_research_work': True,
              'label': 'DataCite metadata',
              'request_key': 'example_dataset_metadata',
              'source_record_kind': 'research_work_metadata'},
 'deep_blue_repository': {'connector_family': 'research_repository',
                          'endpoint_or_metadata_class': 'repository_record_metadata_lookup_future',
                          'has_access_rights': True,
                          'has_bibliographic': True,
                          'has_citation': True,
                          'has_cultural_object': False,
                          'has_dataset': True,
                          'has_patent': False,
                          'has_research_work': True,
                          'label': 'Deep Blue / institutional repository metadata',
                          'request_key': 'example_repository_record_metadata',
                          'source_record_kind': 'research_work_metadata'},
 'doaj': {'connector_family': 'api_json',
          'endpoint_or_metadata_class': 'article_metadata_lookup_future',
          'has_access_rights': True,
          'has_bibliographic': False,
          'has_citation': True,
          'has_cultural_object': False,
          'has_dataset': False,
          'has_patent': False,
          'has_research_work': True,
          'label': 'DOAJ metadata',
          'request_key': 'example_article_metadata',
          'source_record_kind': 'research_work_metadata'},
 'dpla': {'connector_family': 'cultural_repository',
          'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
          'has_access_rights': True,
          'has_bibliographic': True,
          'has_citation': False,
          'has_cultural_object': True,
          'has_dataset': False,
          'has_patent': False,
          'has_research_work': False,
          'label': 'Digital Public Library of America metadata',
          'request_key': 'example_cultural_metadata',
          'source_record_kind': 'cultural_object_metadata'},
 'europeana': {'connector_family': 'cultural_repository',
               'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
               'has_access_rights': True,
               'has_bibliographic': False,
               'has_citation': False,
               'has_cultural_object': True,
               'has_dataset': False,
               'has_patent': False,
               'has_research_work': False,
               'label': 'Europeana metadata',
               'request_key': 'example_cultural_metadata',
               'source_record_kind': 'cultural_object_metadata'},
 'gallica_bnf': {'connector_family': 'cultural_repository',
                 'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
                 'has_access_rights': True,
                 'has_bibliographic': True,
                 'has_citation': False,
                 'has_cultural_object': True,
                 'has_dataset': False,
                 'has_patent': False,
                 'has_research_work': False,
                 'label': 'Gallica / BnF metadata',
                 'request_key': 'example_cultural_metadata',
                 'source_record_kind': 'cultural_object_metadata'},
 'google_books': {'connector_family': 'api_json',
                  'endpoint_or_metadata_class': 'book_metadata_lookup_future',
                  'has_access_rights': True,
                  'has_bibliographic': True,
                  'has_citation': False,
                  'has_cultural_object': False,
                  'has_dataset': False,
                  'has_patent': False,
                  'has_research_work': False,
                  'label': 'Google Books metadata',
                  'request_key': 'example_book_metadata',
                  'source_record_kind': 'bibliographic_metadata'},
 'google_patents': {'connector_family': 'patent_metadata',
                    'endpoint_or_metadata_class': 'patent_metadata_lookup_future',
                    'has_access_rights': True,
                    'has_bibliographic': False,
                    'has_citation': True,
                    'has_cultural_object': False,
                    'has_dataset': False,
                    'has_patent': True,
                    'has_research_work': False,
                    'label': 'Google Patents / public patent metadata',
                    'request_key': 'example_patent_metadata',
                    'source_record_kind': 'patent_metadata'},
 'govinfo': {'connector_family': 'api_json',
             'endpoint_or_metadata_class': 'government_record_metadata_lookup_future',
             'has_access_rights': True,
             'has_bibliographic': True,
             'has_citation': True,
             'has_cultural_object': True,
             'has_dataset': False,
             'has_patent': False,
             'has_research_work': True,
             'label': 'govinfo metadata',
             'request_key': 'example_government_record_metadata',
             'source_record_kind': 'research_work_metadata'},
 'hathitrust': {'connector_family': 'library_catalog',
                'endpoint_or_metadata_class': 'catalog_record_metadata_lookup_future',
                'has_access_rights': True,
                'has_bibliographic': True,
                'has_citation': False,
                'has_cultural_object': True,
                'has_dataset': False,
                'has_patent': False,
                'has_research_work': False,
                'label': 'HathiTrust metadata',
                'request_key': 'example_catalog_metadata',
                'source_record_kind': 'cultural_object_metadata'},
 'kaggle_datasets': {'connector_family': 'dataset_repository',
                     'endpoint_or_metadata_class': 'dataset_metadata_lookup_future',
                     'has_access_rights': True,
                     'has_bibliographic': False,
                     'has_citation': True,
                     'has_cultural_object': False,
                     'has_dataset': True,
                     'has_patent': False,
                     'has_research_work': False,
                     'label': 'Kaggle dataset metadata',
                     'request_key': 'example_dataset_metadata',
                     'source_record_kind': 'dataset_metadata'},
 'library_of_congress': {'connector_family': 'library_catalog',
                         'endpoint_or_metadata_class': 'catalog_record_metadata_lookup_future',
                         'has_access_rights': True,
                         'has_bibliographic': True,
                         'has_citation': False,
                         'has_cultural_object': True,
                         'has_dataset': False,
                         'has_patent': False,
                         'has_research_work': False,
                         'label': 'Library of Congress metadata',
                         'request_key': 'example_catalog_metadata',
                         'source_record_kind': 'cultural_object_metadata'},
 'nara_catalog': {'connector_family': 'cultural_repository',
                  'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
                  'has_access_rights': True,
                  'has_bibliographic': False,
                  'has_citation': False,
                  'has_cultural_object': True,
                  'has_dataset': False,
                  'has_patent': False,
                  'has_research_work': False,
                  'label': 'NARA catalog metadata',
                  'request_key': 'example_cultural_metadata',
                  'source_record_kind': 'cultural_object_metadata'},
 'national_archives_australia': {'connector_family': 'cultural_repository',
                                 'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
                                 'has_access_rights': True,
                                 'has_bibliographic': False,
                                 'has_citation': False,
                                 'has_cultural_object': True,
                                 'has_dataset': False,
                                 'has_patent': False,
                                 'has_research_work': False,
                                 'label': 'National Archives of Australia metadata',
                                 'request_key': 'example_cultural_metadata',
                                 'source_record_kind': 'cultural_object_metadata'},
 'oaister_oai_pmh': {'connector_family': 'oai_pmh',
                     'endpoint_or_metadata_class': 'oai_pmh_single_record_metadata_future',
                     'has_access_rights': True,
                     'has_bibliographic': True,
                     'has_citation': True,
                     'has_cultural_object': True,
                     'has_dataset': True,
                     'has_patent': False,
                     'has_research_work': True,
                     'label': 'OAIster / OAI-PMH repository metadata',
                     'request_key': 'example_oai_pmh_record_metadata',
                     'source_record_kind': 'research_work_metadata'},
 'open_library': {'connector_family': 'api_json',
                  'endpoint_or_metadata_class': 'work_metadata_lookup_future',
                  'has_access_rights': True,
                  'has_bibliographic': True,
                  'has_citation': False,
                  'has_cultural_object': False,
                  'has_dataset': False,
                  'has_patent': False,
                  'has_research_work': False,
                  'label': 'Open Library metadata',
                  'request_key': 'example_work_metadata',
                  'source_record_kind': 'bibliographic_metadata'},
 'openalex': {'connector_family': 'research_graph',
              'endpoint_or_metadata_class': 'work_metadata_lookup_future',
              'has_access_rights': True,
              'has_bibliographic': False,
              'has_citation': True,
              'has_cultural_object': False,
              'has_dataset': False,
              'has_patent': False,
              'has_research_work': True,
              'label': 'OpenAlex metadata',
              'request_key': 'example_work_metadata',
              'source_record_kind': 'research_work_metadata'},
 'pubmed': {'connector_family': 'api_json',
            'endpoint_or_metadata_class': 'article_metadata_lookup_future',
            'has_access_rights': True,
            'has_bibliographic': False,
            'has_citation': True,
            'has_cultural_object': False,
            'has_dataset': False,
            'has_patent': False,
            'has_research_work': True,
            'label': 'PubMed metadata',
            'request_key': 'example_article_metadata',
            'source_record_kind': 'research_work_metadata'},
 'pubmed_central': {'connector_family': 'research_repository',
                    'endpoint_or_metadata_class': 'article_metadata_lookup_future',
                    'has_access_rights': True,
                    'has_bibliographic': False,
                    'has_citation': True,
                    'has_cultural_object': False,
                    'has_dataset': False,
                    'has_patent': False,
                    'has_research_work': True,
                    'label': 'PubMed Central metadata',
                    'request_key': 'example_article_metadata',
                    'source_record_kind': 'research_work_metadata'},
 'repec': {'connector_family': 'research_repository',
           'endpoint_or_metadata_class': 'article_metadata_lookup_future',
           'has_access_rights': True,
           'has_bibliographic': False,
           'has_citation': True,
           'has_cultural_object': False,
           'has_dataset': False,
           'has_patent': False,
           'has_research_work': True,
           'label': 'RePEc metadata',
           'request_key': 'example_article_metadata',
           'source_record_kind': 'research_work_metadata'},
 'semantic_scholar': {'connector_family': 'research_graph',
                      'endpoint_or_metadata_class': 'work_metadata_lookup_future',
                      'has_access_rights': True,
                      'has_bibliographic': False,
                      'has_citation': True,
                      'has_cultural_object': False,
                      'has_dataset': False,
                      'has_patent': False,
                      'has_research_work': True,
                      'label': 'Semantic Scholar metadata',
                      'request_key': 'example_article_metadata',
                      'source_record_kind': 'research_work_metadata'},
 'ssrn': {'connector_family': 'research_repository',
          'endpoint_or_metadata_class': 'article_metadata_lookup_future',
          'has_access_rights': True,
          'has_bibliographic': False,
          'has_citation': True,
          'has_cultural_object': False,
          'has_dataset': False,
          'has_patent': False,
          'has_research_work': True,
          'label': 'SSRN metadata',
          'request_key': 'example_article_metadata',
          'source_record_kind': 'research_work_metadata'},
 'trove_library_cultural': {'connector_family': 'cultural_repository',
                            'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
                            'has_access_rights': True,
                            'has_bibliographic': True,
                            'has_citation': False,
                            'has_cultural_object': True,
                            'has_dataset': False,
                            'has_patent': False,
                            'has_research_work': False,
                            'label': 'Trove library/cultural metadata',
                            'request_key': 'example_cultural_metadata',
                            'source_record_kind': 'cultural_object_metadata'},
 'uk_national_archives_discovery': {'connector_family': 'cultural_repository',
                                    'endpoint_or_metadata_class': 'cultural_object_metadata_lookup_future',
                                    'has_access_rights': True,
                                    'has_bibliographic': False,
                                    'has_citation': False,
                                    'has_cultural_object': True,
                                    'has_dataset': False,
                                    'has_patent': False,
                                    'has_research_work': False,
                                    'label': 'UK National Archives Discovery metadata',
                                    'request_key': 'example_cultural_metadata',
                                    'source_record_kind': 'cultural_object_metadata'},
 'uspto_patents': {'connector_family': 'patent_metadata',
                   'endpoint_or_metadata_class': 'patent_metadata_lookup_future',
                   'has_access_rights': True,
                   'has_bibliographic': False,
                   'has_citation': True,
                   'has_cultural_object': False,
                   'has_dataset': False,
                   'has_patent': True,
                   'has_research_work': False,
                   'label': 'USPTO patent metadata',
                   'request_key': 'example_patent_metadata',
                   'source_record_kind': 'patent_metadata'},
 'wipo_patentscope': {'connector_family': 'patent_metadata',
                      'endpoint_or_metadata_class': 'patent_metadata_lookup_future',
                      'has_access_rights': True,
                      'has_bibliographic': False,
                      'has_citation': True,
                      'has_cultural_object': False,
                      'has_dataset': False,
                      'has_patent': True,
                      'has_research_work': False,
                      'label': 'WIPO PATENTSCOPE metadata',
                      'request_key': 'example_patent_metadata',
                      'source_record_kind': 'patent_metadata'},
 'worldcat_library_catalog': {'connector_family': 'library_catalog',
                              'endpoint_or_metadata_class': 'catalog_record_metadata_lookup_future',
                              'has_access_rights': True,
                              'has_bibliographic': True,
                              'has_citation': False,
                              'has_cultural_object': False,
                              'has_dataset': False,
                              'has_patent': False,
                              'has_research_work': False,
                              'label': 'WorldCat / OCLC-style library catalog metadata',
                              'request_key': 'example_catalog_metadata',
                              'source_record_kind': 'bibliographic_metadata'},
 'zenodo': {'connector_family': 'dataset_repository',
            'endpoint_or_metadata_class': 'dataset_metadata_lookup_future',
            'has_access_rights': True,
            'has_bibliographic': False,
            'has_citation': True,
            'has_cultural_object': False,
            'has_dataset': True,
            'has_patent': False,
            'has_research_work': True,
            'label': 'Zenodo metadata',
            'request_key': 'example_dataset_metadata',
            'source_record_kind': 'dataset_metadata'}}
H7_SOURCE_IDS = tuple(SOURCE_CONFIGS)

FORBIDDEN_TRUTH_TRUE_KEYS = set(['accepted_access_rights_truth',
 'accepted_bibliographic_truth',
 'accepted_candidate_truth',
 'accepted_citation_truth',
 'accepted_cultural_object_truth',
 'accepted_dataset_truth',
 'accepted_evidence_truth',
 'accepted_patent_truth',
 'accepted_public_record',
 'accepted_research_work_truth',
 'accepted_source_truth',
 'access_metadata_is_rights_truth',
 'bibliographic_identity_candidate_is_truth',
 'citation_relation_candidate_is_truth',
 'cultural_object_candidate_is_truth',
 'dataset_identity_candidate_is_truth',
 'evidence_candidate_preview_is_accepted_evidence',
 'live_probe_result_is_public_truth',
 'malware_safety_claimed',
 'master_index_mutated',
 'normalized_record_is_public_truth',
 'open_access_metadata_is_rights_clearance',
 'open_access_truth_claimed',
 'patent_identity_candidate_is_truth',
 'privacy_safety_claimed',
 'production_readiness_claimed',
 'public_index_mutated',
 'research_work_candidate_is_truth',
 'review_seed_is_review_decision',
 'rights_clearance_claimed',
 'source_cache_candidate_is_accepted_source',
 'verified_availability_claimed'])
FORBIDDEN_PRODUCT_TRUE_KEYS = set(['api_calls_made',
 'article_download_used',
 'book_scan_download_used',
 'bypass_or_automation_used',
 'changed_public_search_behavior',
 'crawling_used',
 'dataset_download_used',
 'enabled_accounts',
 'enabled_browser_automation',
 'enabled_crawling',
 'enabled_downloads',
 'enabled_harvesting',
 'enabled_hosting',
 'enabled_live_probes',
 'enabled_scraping',
 'enabled_source_sync',
 'enabled_telemetry',
 'enabled_uploads',
 'full_text_fetch_used',
 'iiif_fetch_used',
 'media_download_used',
 'mutated_master_index',
 'mutated_public_index',
 'network_calls_made',
 'oai_pmh_harvest_used',
 'patent_document_download_used',
 'pdf_download_used',
 'restricted_source_access_used',
 'scraping_used'])


def load_h7_library_research_live_probe_policy_bundle(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[5]
    bundle: dict[str, Any] = {}
    for key, rel_path in POLICY_PATHS.items():
        with (root / rel_path).open("r", encoding="utf-8") as handle:
            bundle[key] = json.load(handle)
    return bundle


def build_h7_library_research_live_probe_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any], live_requested: bool = False) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H7 source_id: {source_id}")
    source_policy = _source_policy(source_id, policy_bundle)
    request_detail = _request_detail(source_policy, request_key)
    cfg = SOURCE_CONFIGS[source_id]
    request_shape = _mapping(request_detail.get("request_shape")) or {
        "kind": "bounded_library_research_metadata_lookup",
        "identifier": {
            "source_native_id_or_identifier": f"fixture:h7:{source_id}:metadata-only",
            "title_or_label_context": f"Synthetic {cfg['label']} metadata context",
            "date_context": "2026-05-11",
            "source_context": cfg["label"],
        },
    }
    endpoint_class = str(request_detail.get("endpoint_or_metadata_class") or cfg["endpoint_or_metadata_class"])
    request = {
        "schema_version": "h7_library_research_live_probe_request.v0",
        "live_probe_request_id": f"h7.library_research_live_probe_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "operation_scope": "metadata_only",
        "endpoint_or_metadata_class": endpoint_class,
        "request_shape": request_shape,
        "approved_request_key": request_key,
        "identifier_or_query_context": _mapping(request_shape.get("identifier")),
        "doi_or_identifier_context": {"doi_candidate": "fixture-only-unapproved", "identifier_only": True},
        "isbn_or_catalog_context": {"isbn_candidate": "fixture-only-unapproved", "catalog_record_only": True},
        "repository_or_collection_context": {"repository_record_ref": f"fixture:h7:{source_id}:repository"},
        "patent_or_publication_context": {"patent_or_publication_ref": f"fixture:h7:{source_id}:publication"},
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "live_requested": bool(live_requested),
        "dry_run_only": not bool(live_requested),
        "oai_pmh_harvest_requested": False,
        "api_query_requested": False,
        "full_text_fetch_requested": False,
        "pdf_download_requested": False,
        "book_scan_download_requested": False,
        "article_download_requested": False,
        "dataset_download_requested": False,
        "patent_document_download_requested": False,
        "iiif_manifest_fetch_requested": False,
        "media_download_requested": False,
        "scraping_or_crawling_requested": False,
        "restricted_source_requested": False,
        "bypass_or_automation_requested": False,
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["No live call is permitted unless committed source-specific policy gates approve the exact request."],
        "notes": ["H7 live-probe request envelope is metadata-only and fail-closed by default."],
    }
    return request


def validate_h7_source_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        return {"approved": False, "blocked_reasons": [f"source is not in H7 allowlist: {source_id}"], "result_status": "blocked_by_policy"}
    request = build_h7_library_research_live_probe_request(source_id, request_key, policy_bundle, live_requested=True)
    return validate_h7_library_research_live_probe_request(request, policy_bundle)


def validate_h7_library_research_live_probe_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    endpoint_class = str(request.get("endpoint_or_metadata_class") or "")
    if source_id not in H7_SOURCE_IDS:
        reasons.append(f"source is not in H7 allowlist: {source_id}")
        return {"approved": False, "blocked_reasons": reasons, "result_status": "blocked_by_policy"}
    if request.get("operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    for key in (
        "full_text_fetch_requested",
        "pdf_download_requested",
        "book_scan_download_requested",
        "article_download_requested",
        "dataset_download_requested",
        "patent_document_download_requested",
        "media_download_requested",
        "scraping_or_crawling_requested",
        "restricted_source_requested",
        "bypass_or_automation_requested",
    ):
        if request.get(key) is True:
            reasons.append(f"{key} must be false")
    source = _source_policy(source_id, policy_bundle)
    endpoint = _source_policy(source_id, policy_bundle, "endpoint_policy")
    rate = _source_policy(source_id, policy_bundle, "rate_limit_policy")
    cache = _source_policy(source_id, policy_bundle, "cache_policy")
    kill = _source_policy(source_id, policy_bundle, "kill_switch_policy")
    for key in ("live_access_approved", "metadata_probe_approved"):
        if source.get(key) is not True:
            reasons.append(f"allowed_requests.{source_id}.{key} must be true")
    for key in (
        "source_sync_approved",
        "full_text_fetch_approved",
        "pdf_download_approved",
        "book_scan_download_approved",
        "article_download_approved",
        "dataset_download_approved",
        "patent_document_download_approved",
        "media_download_approved",
        "scraping_approved",
        "crawling_approved",
        "browser_automation_approved",
        "restricted_rights_sensitive_source_approved",
        "bypass_or_access_control_automation_approved",
        "public_query_fanout_approved",
    ):
        if source.get(key) is not False:
            reasons.append(f"allowed_requests.{source_id}.{key} must be false")
    if request.get("oai_pmh_harvest_requested") is True and source.get("oai_pmh_harvest_approved") is not True:
        reasons.append("oai_pmh_harvest_requested must be false unless exact bounded metadata policy approves it")
    if request.get("api_query_requested") is True and source.get("api_query_approved") is not True:
        reasons.append("api_query_requested must be false unless exact bounded metadata policy approves it")
    if request.get("iiif_manifest_fetch_requested") is True and source.get("iiif_manifest_fetch_approved") is not True:
        reasons.append("iiif_manifest_fetch_requested must be false unless exact bounded metadata policy approves it")
    if source.get("oai_pmh_harvest_approved") is not False and request.get("oai_pmh_harvest_requested") is not True:
        reasons.append("oai_pmh_harvest_approved must stay false unless exact bounded request is used")
    if source.get("api_query_approved") is not False and request.get("api_query_requested") is not True:
        reasons.append("api_query_approved must stay false unless exact bounded request is used")
    if source.get("iiif_manifest_fetch_approved") is not False and request.get("iiif_manifest_fetch_requested") is not True:
        reasons.append("iiif_manifest_fetch_approved must stay false unless exact bounded request is used")
    if source.get("approved_operation_scope") != "metadata_only":
        reasons.append("approved_operation_scope must be metadata_only")
    if source.get("approved_source_id") != source_id:
        reasons.append("approved_source_id must match requested source")
    if request_key not in list(source.get("allowed_request_keys") or []):
        reasons.append(f"request key is not approved for live use: {request_key}")
    if request_key not in _mapping(source.get("requests")):
        reasons.append(f"request key is not present in request manifest: {request_key}")
    allowlisted = list(endpoint.get("allowlisted_endpoint_or_metadata_classes_current") or [])
    if endpoint_class not in allowlisted:
        reasons.append(f"endpoint/metadata class is not currently allowlisted: {endpoint_class}")
    forbidden_classes = list(endpoint.get("forbidden_endpoint_or_metadata_classes_current") or [])
    forbidden_terms = ("harvest", "download", "payload", "scrap", "crawl", "browser", "bypass", "full_text", "sync")
    if endpoint_class in forbidden_classes or any(term in endpoint_class.casefold() and "metadata" not in endpoint_class.casefold() for term in forbidden_terms):
        reasons.append(f"endpoint/metadata class is forbidden: {endpoint_class}")
    for key in (
        "oai_pmh_harvest_allowed",
        "api_query_allowed",
        "full_text_fetch_allowed",
        "download_allowed",
        "iiif_manifest_fetch_allowed",
        "scraping_crawling_allowed",
        "restricted_source_access_allowed",
        "bypass_or_automation_allowed",
    ):
        if source.get(key) is not False:
            reasons.append(f"{key} must remain false")
    if rate.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("rate limit decision is not approved")
    if int(rate.get("max_requests_per_run") or 0) < 1:
        reasons.append("request budget must be set before live probe")
    if int(rate.get("timeout_seconds") or 0) < 1:
        reasons.append("timeout_seconds must be set")
    if "approved" not in str(rate.get("user_agent_contact_posture") or ""):
        reasons.append("User-Agent/contact posture is not approved")
    if "approved" not in str(rate.get("auth_posture") or ""):
        reasons.append("auth/no-auth posture is not approved")
    if cache.get("decision_status") != "approved_for_bounded_metadata_probe":
        reasons.append("cache TTL or no-cache decision is not approved")
    if kill.get("default_enabled") is not True or kill.get("live_probe_kill_switch_engaged") is True:
        reasons.append("kill switch blocks live probe")
    status = _status_for_reasons(reasons)
    return {"approved": not reasons, "blocked_reasons": _dedupe(reasons), "result_status": status}


def build_h7_library_research_live_probe_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons = [reason] if isinstance(reason, str) else list(reason)
    source_id = str(request.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    status = _status_for_reasons(reasons)
    result = {
        "schema_version": "h7_library_research_live_probe_result.v0",
        "live_probe_result_id": f"h7.live_probe_result.{source_id}.blocked.{_short_fingerprint({'source_id': source_id, 'reasons': reasons})}.v0",
        "live_probe_request_ref": str(request.get("live_probe_request_id") or "unknown"),
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or request.get("connector_family") or "unknown"),
        "source_record_kind": str(cfg.get("source_record_kind") or request.get("source_record_kind") or "unknown"),
        "result_status": status,
        "request_count": 0,
        "network_used": False,
        "endpoint_or_metadata_used": str(request.get("endpoint_or_metadata_class") or "not_used_blocked"),
        "response_status_code": None,
        "response_fingerprint": "not_created_blocked_by_policy",
        "response_summary": "No source call was made; committed H7 policy gates blocked before network use.",
        "normalized_record": _blocked_candidate(),
        "bibliographic_identity_candidate": _blocked_candidate(),
        "research_work_identity_candidate": _blocked_candidate(),
        "dataset_identity_candidate": _blocked_candidate(),
        "cultural_object_identity_candidate": _blocked_candidate(),
        "patent_identity_candidate": _blocked_candidate(),
        "citation_relation_candidate": _blocked_candidate(),
        "access_rights_availability_candidate": _blocked_candidate(),
        "source_cache_candidate_preview": _blocked_candidate(),
        "evidence_candidate_preview": _blocked_candidate(),
        "review_queue_seed_preview": _blocked_review_seed(source_id, status, reasons),
        "connector_health_summary": {},
        "blocked_reason": "; ".join(reasons) if reasons else None,
        "blocked_reasons": _dedupe(reasons),
        "warnings": [],
        "limitations": ["Blocked result only; no metadata observation, truth acceptance, or index mutation occurred."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H7 live probe failed closed before any source call."],
    }
    result["connector_health_summary"] = build_h7_connector_health_summary(result, policy_bundle)
    return result


def build_h7_library_research_live_probe_result(source_id: str, response_payload: Mapping[str, Any], response_metadata: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in SOURCE_CONFIGS:
        raise ValueError(f"unknown H7 source_id: {source_id}")
    cfg = SOURCE_CONFIGS[source_id]
    payload = _metadata_payload_defaults(source_id, response_payload)
    fixture = _fixture_from_payload(source_id, payload)
    normalized = normalize_h7_library_research_fixture(fixture, source_id)
    network_used = bool(response_metadata.get("network_used"))
    status = str(response_metadata.get("result_status") or ("live_probe_completed" if network_used else "dry_run_preflight_pass"))
    result = {
        "schema_version": "h7_library_research_live_probe_result.v0",
        "live_probe_result_id": f"h7.live_probe_result.{source_id}.{_slug(str(payload.get('source_native_id') or 'metadata'))}.v0",
        "live_probe_request_ref": str(response_metadata.get("live_probe_request_ref") or f"h7.library_research_live_probe_request.{source_id}.{cfg['request_key']}.v0"),
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["source_record_kind"],
        "result_status": status,
        "request_count": int(response_metadata.get("request_count") or (1 if network_used else 0)),
        "network_used": network_used,
        "endpoint_or_metadata_used": str(response_metadata.get("endpoint_or_metadata_used") or cfg["endpoint_or_metadata_class"]),
        "response_status_code": response_metadata.get("response_status_code"),
        "response_fingerprint": _fingerprint(payload),
        "response_summary": str(response_metadata.get("response_summary") or "Metadata-only response payload normalized into candidate previews."),
        "normalized_record": normalized,
        "bibliographic_identity_candidate": build_h7_bibliographic_identity_candidate_from_probe(normalized, policy_bundle),
        "research_work_identity_candidate": build_h7_research_work_identity_candidate_from_probe(normalized, policy_bundle),
        "dataset_identity_candidate": build_h7_dataset_identity_candidate_from_probe(normalized, policy_bundle),
        "cultural_object_identity_candidate": build_h7_cultural_object_identity_candidate_from_probe(normalized, policy_bundle),
        "patent_identity_candidate": build_h7_patent_identity_candidate_from_probe(normalized, policy_bundle),
        "citation_relation_candidate": build_h7_citation_relation_candidate_from_probe(normalized, policy_bundle),
        "access_rights_availability_candidate": build_h7_access_rights_availability_candidate_from_probe(normalized, policy_bundle),
        "source_cache_candidate_preview": build_h7_source_cache_candidate_preview_from_probe(normalized, policy_bundle),
        "evidence_candidate_preview": build_h7_evidence_candidate_preview_from_probe(normalized, policy_bundle),
        "review_queue_seed_preview": {},
        "connector_health_summary": {},
        "blocked_reason": None,
        "blocked_reasons": [],
        "warnings": list(response_metadata.get("warnings") or []),
        "limitations": ["Live-probe output is a controlled metadata observation preview, not accepted truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Candidates require review before any source-cache, evidence, review, public index, or master index use."],
    }
    result["review_queue_seed_preview"] = build_h7_review_queue_seed_preview_from_probe(
        result,
        result["source_cache_candidate_preview"],
        result["evidence_candidate_preview"],
        policy_bundle,
    )
    result["connector_health_summary"] = build_h7_connector_health_summary(result, policy_bundle)
    _raise_on_boundary_errors(result, policy_bundle)
    return result


def normalize_h7_library_research_live_probe_result(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if result.get("normalized_record"):
        normalized = dict(result)
        _raise_on_boundary_errors(normalized, policy_bundle)
        return normalized
    source_id = str(result.get("source_id") or "")
    return build_h7_library_research_live_probe_result(source_id, {}, {"result_status": "dry_run_preflight_pass"}, policy_bundle)


def build_h7_bibliographic_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_bibliographic_candidate(normalized_record)


def build_h7_research_work_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_research_candidate(normalized_record)


def build_h7_dataset_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_dataset_candidate(normalized_record)


def build_h7_cultural_object_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_cultural_candidate(normalized_record)


def build_h7_patent_identity_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_patent_candidate(normalized_record)


def build_h7_citation_relation_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _fixture_citation_candidates(normalized_record)


def build_h7_access_rights_availability_candidate_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_access_candidate(normalized_record)


def build_h7_source_cache_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_source_cache_preview(normalized_record)


def build_h7_evidence_candidate_preview_from_probe(normalized_record: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return _fixture_evidence_preview(normalized_record)


def build_h7_review_queue_seed_preview_from_probe(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    seed = {
        "schema_version": "h7_library_research_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h7.review_seed_preview.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "live_probe_result_ref": result.get("live_probe_result_id"),
        "source_cache_candidate_preview_ref": source_cache_preview.get("source_cache_candidate_preview_id") if isinstance(source_cache_preview, Mapping) else None,
        "evidence_candidate_preview_ref": evidence_preview.get("evidence_candidate_preview_id") if isinstance(evidence_preview, Mapping) else None,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "required_review": "human_or_future_policy_review_required_before_any_acceptance",
        "limitations": ["Review queue seed preview only; no review queue mutation or review decision."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(seed, policy_bundle)
    return seed


def build_h7_connector_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(result.get("source_id") or "unknown")
    cfg = SOURCE_CONFIGS.get(source_id, {})
    health = {
        "schema_version": "h7_library_research_connector_health_summary.v0",
        "health_summary_id": f"h7.connector_health.{source_id}.{_short_fingerprint(result)}.v0",
        "source_id": source_id,
        "connector_family": str(cfg.get("connector_family") or result.get("connector_family") or "unknown"),
        "live_probe_status": str(result.get("result_status") or "not_evaluable"),
        "request_count": int(result.get("request_count") or 0),
        "response_status_summary": "blocked_before_network" if result.get("network_used") is not True else str(result.get("response_status_code") or "metadata_response_observed"),
        "policy_blockers": list(result.get("blocked_reasons") or []),
        "warnings": list(result.get("warnings") or []),
        "source_limitations": list(result.get("limitations") or []),
        "restricted_source_status": "blocked_current",
        "next_recommended_action": "review_fixture_equivalent_outputs_or_commit_operator_approval_before_live_probe",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(health, policy_bundle)
    return health


def build_h7_library_research_live_probe_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h7_library_research_live_probe_output_bundle.v0",
        "live_probe_result": dict(result),
        "normalized_record": result.get("normalized_record", {}),
        "bibliographic_identity_candidate": result.get("bibliographic_identity_candidate", {}),
        "research_work_identity_candidate": result.get("research_work_identity_candidate", {}),
        "dataset_identity_candidate": result.get("dataset_identity_candidate", {}),
        "cultural_object_identity_candidate": result.get("cultural_object_identity_candidate", {}),
        "patent_identity_candidate": result.get("patent_identity_candidate", {}),
        "citation_relation_candidate": result.get("citation_relation_candidate", []),
        "access_rights_availability_candidate": result.get("access_rights_availability_candidate", {}),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview", {}),
        "evidence_candidate_preview": result.get("evidence_candidate_preview", {}),
        "review_queue_seed_preview": result.get("review_queue_seed_preview", {}),
        "connector_health_summary": result.get("connector_health_summary", {}),
        "validation_summary": {
            "truth_boundary_violations": detect_h7_library_research_live_probe_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h7_library_research_live_probe_product_boundary_violations(result, {}),
        },
    }


def summarize_h7_library_research_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h7_library_research_live_probe_summary.v0",
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "request_count": int(result.get("request_count") or 0),
        "network_used": bool(result.get("network_used")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "bibliographic_candidate_present": _present(result.get("bibliographic_identity_candidate")),
        "research_work_candidate_present": _present(result.get("research_work_identity_candidate")),
        "dataset_candidate_present": _present(result.get("dataset_identity_candidate")),
        "cultural_object_candidate_present": _present(result.get("cultural_object_identity_candidate")),
        "patent_candidate_present": _present(result.get("patent_identity_candidate")),
        "citation_candidate_present": bool(result.get("citation_relation_candidate")) and not (isinstance(result.get("citation_relation_candidate"), Mapping) and result.get("citation_relation_candidate", {}).get("status") == "not_created_blocked_by_policy"),
        "access_rights_candidate_present": _present(result.get("access_rights_availability_candidate")),
        "source_cache_preview_present": _present(result.get("source_cache_candidate_preview")),
        "evidence_preview_present": _present(result.get("evidence_candidate_preview")),
        "review_seed_present": _present(result.get("review_queue_seed_preview")),
    }


def detect_h7_library_research_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_truth_violations(result) + _detect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth")


def detect_h7_library_research_live_probe_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    return _fixture_product_violations(result) + _detect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product")


def _metadata_payload_defaults(source_id: str, response_payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(response_payload)
    cfg = SOURCE_CONFIGS[source_id]
    payload.setdefault("source_record_kind", cfg["source_record_kind"])
    payload.setdefault("source_native_id", f"{source_id}-metadata-candidate")
    payload.setdefault("title", f"Synthetic {cfg['label']} metadata record")
    payload.setdefault("subtitle", "Metadata-only live-probe preview")
    payload.setdefault("creators", ["Eureka Synthetic Metadata Contributor"])
    payload.setdefault("contributors", [])
    payload.setdefault("publisher_or_institution", cfg["label"])
    payload.setdefault("publication_or_creation_date", "2026-05-11")
    payload.setdefault("language", "en")
    payload.setdefault("format_or_medium", "metadata_record")
    payload.setdefault("identifiers", [{"scheme": "fixture", "value": f"h7:{source_id}:metadata"}])
    payload.setdefault("metadata_summary", f"Metadata-only observation candidate for {cfg['label']}.")
    payload.setdefault("source_metadata", {"source_label": cfg["label"], "metadata_only_probe_preview": True})
    payload.setdefault("access_rights_availability_summary", "Access metadata candidate only; no rights clearance or download permission.")
    payload.setdefault("license_metadata_candidate", "unknown")
    payload.setdefault("landing_page_candidate", f"fixture://h7/{source_id}/metadata")
    payload.setdefault("access_status_candidate", "metadata_observed_candidate_only")
    payload.setdefault("access", {"download_permission_current": False, "rights_clearance_claimed": False, "open_access_truth_claimed": False})
    payload.setdefault("relations", [{"relation_kind": "related_work", "target_ref": f"fixture:h7:{source_id}:related", "confidence_or_uncertainty": "probe_preview_no_citation_truth"}])
    payload.setdefault("citation_or_relation_summary", "Citation/relation candidate preview only; not citation truth.")
    if cfg.get("has_research_work"):
        payload.setdefault("doi_candidate", f"10.5555/{source_id}.probe")
        payload.setdefault("openalex_id_candidate", f"W{_short_fingerprint({'source_id': source_id})}")
    if cfg.get("has_dataset"):
        payload.setdefault("dataset_id_candidate", f"dataset:{source_id}:probe")
        payload.setdefault("datacite_id_candidate", f"datacite:{source_id}:probe")
    if cfg.get("has_patent"):
        payload.setdefault("patent_number_candidate", f"{source_id.upper()}-PROBE-0001")
    if cfg.get("has_bibliographic"):
        payload.setdefault("isbn_candidate", "9780000000000")
        payload.setdefault("catalog_record_id", f"catalog:{source_id}:probe")
    if cfg.get("has_cultural_object"):
        payload.setdefault("collection_or_repository_ref", f"collection:{source_id}:probe")
    return payload


def _fixture_from_payload(source_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    cfg = SOURCE_CONFIGS[source_id]
    return {
        "schema_version": "h7_library_research_fixture.v0",
        "fixture_id": f"h7.live_probe_fixture_equivalent.{source_id}.{_slug(str(payload.get('source_native_id') or 'metadata'))}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "fixture_kind": "live_probe_metadata_response_preview",
        "fixture_status": "ready",
        "fixture_public_safe": True,
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "oai_pmh_payload_included": False,
        "api_query_payload_included": False,
        "full_text_payload_included": False,
        "pdf_payload_included": False,
        "book_scan_payload_included": False,
        "article_payload_included": False,
        "dataset_payload_included": False,
        "patent_document_payload_included": False,
        "iiif_payload_included": False,
        "media_payload_included": False,
        "scraping_output_included": False,
        "crawling_output_included": False,
        "restricted_source_accessed": False,
        "bypass_or_automation_used": False,
        "fixture_payload": dict(payload),
        "expected_normalized_ref": "live_probe_result.normalized_record",
        "limitations": ["Probe response payload is normalized as candidate-only metadata; no payload download or truth acceptance."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Internal fixture-equivalent envelope for H7 live-probe normalization."],
    }


def _blocked_review_seed(source_id: str, status: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "h7_library_research_live_probe_review_seed.v0",
        "review_queue_seed_preview_id": f"h7.review_seed_preview.{source_id}.blocked.{_short_fingerprint({'source_id': source_id, 'reasons': reasons})}.v0",
        "source_id": source_id,
        "preview_only": True,
        "review_seed_is_review_decision": False,
        "review_queue_write_allowed_current": False,
        "blocked_status": status,
        "blocked_reasons": reasons,
        "limitations": ["Blocked review seed preview only; no review queue mutation or review decision."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def _blocked_candidate() -> dict[str, Any]:
    return {"status": "not_created_blocked_by_policy", "truth_boundary": _truth_boundary(), "product_boundary": _product_boundary()}


def _present(value: Any) -> bool:
    return isinstance(value, Mapping) and value.get("status") != "not_created_blocked_by_policy" and bool(value)


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], bundle_key: str = "allowed_requests") -> dict[str, Any]:
    for item in _mapping(policy_bundle.get(bundle_key)).get("sources", []):
        if isinstance(item, Mapping) and item.get("source_id") == source_id:
            return dict(item)
    return {}


def _request_detail(source_policy: Mapping[str, Any], request_key: str) -> dict[str, Any]:
    detail = _mapping(source_policy.get("requests")).get(request_key)
    return dict(detail) if isinstance(detail, Mapping) else {}


def _status_for_reasons(reasons: list[str]) -> str:
    joined = " ".join(reasons).casefold()
    if not reasons:
        return "dry_run_preflight_pass"
    if "approved" in joined or "approval" in joined:
        return "blocked_by_missing_approval"
    if "kill switch" in joined:
        return "blocked_by_kill_switch"
    if "endpoint" in joined:
        return "blocked_by_download_policy" if any(word in joined for word in ("download", "payload", "full_text")) else "blocked_by_endpoint_policy"
    if "harvest" in joined or "api_query" in joined or "sync" in joined:
        return "blocked_by_harvest_policy"
    if any(word in joined for word in ("download", "fetch", "pdf", "book", "article", "dataset", "patent", "iiif", "media", "payload")):
        return "blocked_by_download_policy"
    if any(word in joined for word in ("scraping", "crawl", "browser")):
        return "blocked_by_harvest_policy"
    if "restricted" in joined or "sensitive" in joined:
        return "blocked_by_restricted_source_policy"
    if "bypass" in joined or "automation" in joined or "access control" in joined:
        return "blocked_by_bypass_policy"
    return "blocked_by_policy"


def _raise_on_boundary_errors(value: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> None:
    errors = detect_h7_library_research_live_probe_truth_boundary_violations(value, policy_bundle or {})
    errors.extend(detect_h7_library_research_live_probe_product_boundary_violations(value, policy_bundle or {}))
    if errors:
        raise ValueError("; ".join(_dedupe(errors)))


def _truth_boundary() -> dict[str, bool]:
    return {'accepted_access_rights_truth': False,
 'accepted_bibliographic_truth': False,
 'accepted_candidate_truth': False,
 'accepted_citation_truth': False,
 'accepted_cultural_object_truth': False,
 'accepted_dataset_truth': False,
 'accepted_evidence_truth': False,
 'accepted_patent_truth': False,
 'accepted_public_record': False,
 'accepted_research_work_truth': False,
 'accepted_source_truth': False,
 'access_metadata_is_rights_truth': False,
 'bibliographic_identity_candidate_is_truth': False,
 'citation_relation_candidate_is_truth': False,
 'cultural_object_candidate_is_truth': False,
 'dataset_identity_candidate_is_truth': False,
 'evidence_candidate_preview_is_accepted_evidence': False,
 'live_probe_result_is_public_truth': False,
 'malware_safety_claimed': False,
 'master_index_mutated': False,
 'normalized_record_is_public_truth': False,
 'open_access_metadata_is_rights_clearance': False,
 'open_access_truth_claimed': False,
 'patent_identity_candidate_is_truth': False,
 'privacy_safety_claimed': False,
 'production_readiness_claimed': False,
 'public_index_mutated': False,
 'research_work_candidate_is_truth': False,
 'review_seed_is_review_decision': False,
 'rights_clearance_claimed': False,
 'source_cache_candidate_is_accepted_source': False,
 'verified_availability_claimed': False}


def _product_boundary() -> dict[str, bool]:
    return {'api_calls_made': False,
 'article_download_used': False,
 'book_scan_download_used': False,
 'bypass_or_automation_used': False,
 'changed_public_search_behavior': False,
 'crawling_used': False,
 'dataset_download_used': False,
 'enabled_accounts': False,
 'enabled_browser_automation': False,
 'enabled_crawling': False,
 'enabled_downloads': False,
 'enabled_harvesting': False,
 'enabled_hosting': False,
 'enabled_live_probes': False,
 'enabled_scraping': False,
 'enabled_source_sync': False,
 'enabled_telemetry': False,
 'enabled_uploads': False,
 'full_text_fetch_used': False,
 'iiif_fetch_used': False,
 'media_download_used': False,
 'mutated_master_index': False,
 'mutated_public_index': False,
 'network_calls_made': False,
 'oai_pmh_harvest_used': False,
 'patent_document_download_used': False,
 'pdf_download_used': False,
 'restricted_source_access_used': False,
 'scraping_used': False}


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _fingerprint(payload: Mapping[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _short_fingerprint(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    safe = "-".join(part for part in safe.split("-") if part)
    return safe[:64] if safe else hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _detect_true_keys(value: Any, forbidden: set[str], category: str, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in forbidden and item is True:
                errors.append(f"{category} boundary forbidden true value: {current}")
            errors.extend(_detect_true_keys(item, forbidden, category, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_detect_true_keys(item, forbidden, category, f"{path}[{index}]"))
    return errors


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out
