#!/usr/bin/env python3
"""Validate Wayback/CDX/Memento Connector Approval v0 governance artifacts."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
from typing import Any, Mapping, Sequence
REPO_ROOT=Path(__file__).resolve().parents[1]
if str(REPO_ROOT/'scripts') not in sys.path: sys.path.insert(0,str(REPO_ROOT/'scripts'))
from _p70_contract_common import load_json_object, print_report  # noqa:E402
from validate_wayback_cdx_memento_connector_approval import validate_all_examples  # noqa:E402
APPROVAL_CONTRACT=REPO_ROOT/'contracts/connectors/wayback_cdx_memento_connector_approval.v0.json'
MANIFEST_CONTRACT=REPO_ROOT/'contracts/connectors/wayback_cdx_memento_connector_manifest.v0.json'
CONNECTOR_INVENTORY=REPO_ROOT/'control/inventory/connectors/wayback_cdx_memento_connector.json'
AUDIT_DIR=REPO_ROOT/'control/audits/wayback-cdx-memento-connector-approval-v0'
REPORT_PATH=AUDIT_DIR/'wayback_cdx_memento_connector_approval_report.json'
REQ={'schema_version','approval_record_id','approval_record_kind','status','created_by_tool','connector_ref','connector_scope','allowed_capabilities','forbidden_capabilities','url_and_uri_policy','source_policy_review','user_agent_and_contact_policy','rate_limit_timeout_retry_circuit_breaker_policy','cache_first_policy','expected_source_cache_outputs','expected_evidence_ledger_outputs','query_intelligence_relationship','public_search_boundary','rights_access_and_risk_policy','privacy_policy','approval_checklist','operator_checklist','implementation_prerequisites','limitations','no_runtime_guarantees','no_mutation_guarantees','notes'}
MANIFEST_REQ={'schema_version','connector_id','connector_kind','status','source_family','supported_capabilities','disabled_capabilities','default_policy','source_sync_worker_relationship','source_cache_relationship','evidence_ledger_relationship','safety_defaults','no_runtime_guarantees','notes'}
CONTRACT_FALSE={'x-connector_runtime_implemented','x-connector_approved_now','x-live_source_calls_allowed_now','x-external_calls_allowed_now','x-archived_content_fetch_allowed','x-capture_replay_allowed','x-warc_download_allowed','x-public_search_live_fanout_allowed','x-arbitrary_url_fetch_allowed','x-source_cache_mutation_allowed_now','x-evidence_ledger_mutation_allowed_now','x-candidate_index_mutation_allowed_now','x-public_index_mutation_allowed_now','x-local_index_mutation_allowed_now','x-master_index_mutation_allowed','x-downloads_allowed','x-file_retrieval_allowed','x-mirroring_allowed','x-telemetry_implemented','x-credentials_configured'}
MANIFEST_FALSE={'x-runtime_implemented','x-live_enabled_by_default','x-public_query_fanout_allowed','x-downloads_allowed','x-arbitrary_url_fetch_allowed','x-archived_content_fetch_allowed','x-capture_replay_allowed','x-warc_download_allowed','x-source_cache_mutation_allowed_now','x-evidence_ledger_mutation_allowed_now','x-candidate_index_mutation_allowed_now','x-master_index_mutation_allowed_now'}
INVENTORY_FALSE={'connector_runtime_implemented','connector_approved_now','live_enabled_by_default','public_query_fanout_allowed','arbitrary_url_fetch_allowed','archived_content_fetch_allowed','capture_replay_allowed','warc_download_allowed','downloads_allowed','file_retrieval_allowed','mirroring_allowed','source_cache_mutation_allowed_now','evidence_ledger_mutation_allowed_now','candidate_index_mutation_allowed_now','master_index_mutation_allowed'}
INVENTORY_TRUE={'metadata_only_scope','availability_capture_metadata_only','uri_privacy_review_required','source_policy_review_required','user_agent_contact_required_future','rate_limit_required_future','timeout_required_future','retry_backoff_required_future','circuit_breaker_required_future','cache_required_before_public_use','evidence_attribution_required'}
REPORT_FALSE={'connector_runtime_implemented','connector_approved_now','live_enabled_by_default','live_source_called','external_calls_performed','public_query_fanout_allowed','public_search_live_fanout_enabled','arbitrary_url_fetch_allowed','archived_content_fetch_allowed','capture_replay_allowed','warc_download_allowed','downloads_allowed','file_retrieval_allowed','mirroring_allowed','source_cache_mutation_allowed_now','evidence_ledger_mutation_allowed_now','candidate_index_mutation_allowed_now','public_index_mutation_allowed_now','local_index_mutation_allowed_now','master_index_mutation_allowed','rights_clearance_claimed','malware_safety_claimed','telemetry_implemented','credentials_configured'}
AUDIT_FILES={'README.md','APPROVAL_SUMMARY.md','CONNECTOR_SCOPE.md','ALLOWED_METADATA_CAPABILITIES.md','FORBIDDEN_CAPABILITIES.md','URL_AND_URI_PRIVACY_POLICY.md','SOURCE_POLICY_REVIEW.md','USER_AGENT_AND_CONTACT_POLICY.md','RATE_LIMIT_TIMEOUT_RETRY_CIRCUIT_BREAKER_POLICY.md','CACHE_FIRST_AND_EVIDENCE_OUTPUT_POLICY.md','SOURCE_SYNC_WORKER_RELATIONSHIP.md','SOURCE_CACHE_OUTPUT_MODEL.md','EVIDENCE_LEDGER_OUTPUT_MODEL.md','QUERY_INTELLIGENCE_RELATIONSHIP.md','PUBLIC_SEARCH_BOUNDARY.md','RIGHTS_ACCESS_AND_RISK_POLICY.md','PRIVACY_AND_REDACTION_POLICY.md','APPROVAL_CHECKLIST.md','OPERATOR_CHECKLIST.md','EXAMPLE_APPROVAL_RECORD_REVIEW.md','NO_RUNTIME_AND_NO_MUTATION_POLICY.md','FUTURE_IMPLEMENTATION_PATH.md','COMMAND_RESULTS.md','REMAINING_BLOCKERS.md','NEXT_STEPS.md','wayback_cdx_memento_connector_approval_report.json'}
DOCS={'docs/reference/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.md':('connector is not implemented','no external calls','availability/capture metadata-only','arbitrary url fetch','archived page content fetch','capture replay','warc download','uri-r review','source policy','user-agent','cache-first','evidence ledger','public search must not call'),'docs/architecture/SOURCE_INGESTION_PLANE.md':('p72 wayback/cdx/memento connector approval','connector is not implemented','no external calls','public queries do not fan out'),'docs/reference/SOURCE_SYNC_WORKER_CONTRACT.md':('p72 wayback/cdx/memento connector approval','cache-first'),'docs/reference/SOURCE_CACHE_CONTRACT.md':('p72 wayback/cdx/memento connector approval','source cache'),'docs/reference/EVIDENCE_LEDGER_CONTRACT.md':('p72 wayback/cdx/memento connector approval','evidence ledger')}
FORBIDDEN=('wayback/cdx/memento connector runtime exists','wayback/cdx/memento live search enabled true','cdx api was called','memento endpoint was called','capture replay enabled true','warc download enabled true','source cache was mutated','evidence ledger was mutated','master index was mutated','rights clearance is complete','malware safety is confirmed','production ready')

def validate_contract()->dict[str,Any]:
    errors=[]; warnings=[]
    c=load_json_object(APPROVAL_CONTRACT,errors,'contracts/connectors/wayback_cdx_memento_connector_approval.v0.json')
    if c: validate_schema(c,REQ,CONTRACT_FALSE,'approval contract',errors)
    m=load_json_object(MANIFEST_CONTRACT,errors,'contracts/connectors/wayback_cdx_memento_connector_manifest.v0.json')
    if m: validate_schema(m,MANIFEST_REQ,MANIFEST_FALSE,'manifest contract',errors)
    inv=load_json_object(CONNECTOR_INVENTORY,errors,'control/inventory/connectors/wayback_cdx_memento_connector.json')
    if inv: validate_inventory(inv,errors)
    examples=validate_all_examples(strict=True)
    if examples.get('status')!='valid': errors.append('Wayback/CDX/Memento connector approval examples failed validation.'); errors.extend(examples.get('errors',[]))
    validate_docs(errors); validate_audit(errors)
    report=load_json_object(REPORT_PATH,errors,'wayback_cdx_memento_connector_approval_report.json')
    if report:
        if report.get('report_id')!='wayback_cdx_memento_connector_approval_v0': errors.append('report_id must be wayback_cdx_memento_connector_approval_v0.')
        for k in REPORT_FALSE:
            if report.get(k) is not False: errors.append(f'report {k} must be false.')
    scan_forbidden(errors)
    return {'status':'valid' if not errors else 'invalid','created_by':'wayback_cdx_memento_connector_contract_validator_v0','contract_file':'contracts/connectors/wayback_cdx_memento_connector_approval.v0.json','example_count':examples.get('example_count',0),'errors':errors,'warnings':warnings}

def validate_schema(c:Mapping[str,Any],req:set[str],false:set[str],label:str,errors:list[str])->None:
    if c.get('x-status')!='contract_only': errors.append(f'{label} x-status must be contract_only.')
    for k in false:
        if c.get(k) is not False: errors.append(f'{label} {k} must be false.')
    missing=req-set(c.get('required',[]))
    if missing: errors.append(f'{label} missing required fields: '+', '.join(sorted(missing)))

def validate_inventory(inv:Mapping[str,Any],errors:list[str])->None:
    if inv.get('status')!='approval_required': errors.append('connector inventory status must be approval_required.')
    if inv.get('connector_id')!='wayback_cdx_memento_connector': errors.append('connector inventory connector_id must be wayback_cdx_memento_connector.')
    if inv.get('source_family')!='wayback_cdx_memento': errors.append('connector inventory source_family must be wayback_cdx_memento.')
    for k in INVENTORY_FALSE:
        if inv.get(k) is not False: errors.append(f'connector inventory {k} must be false.')
    for k in INVENTORY_TRUE:
        if inv.get(k) is not True: errors.append(f'connector inventory {k} must be true.')

def validate_docs(errors:list[str])->None:
    for rel,phrases in DOCS.items():
        p=REPO_ROOT/rel
        if not p.is_file(): errors.append(f'{rel} missing.'); continue
        text=p.read_text(encoding='utf-8').casefold()
        for phrase in phrases:
            if phrase not in text: errors.append(f'{rel} missing required phrase: {phrase}')

def validate_audit(errors:list[str])->None:
    if not AUDIT_DIR.is_dir(): errors.append('control/audits/wayback-cdx-memento-connector-approval-v0 missing.'); return
    present={p.name for p in AUDIT_DIR.iterdir() if p.is_file()}; missing=AUDIT_FILES-present
    if missing: errors.append('audit pack missing files: '+', '.join(sorted(missing)))

def scan_forbidden(errors:list[str])->None:
    paths=[REPO_ROOT/'contracts/connectors',REPO_ROOT/'control/inventory/connectors',REPO_ROOT/'docs/reference/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.md',REPO_ROOT/'examples/connectors/wayback_cdx_memento_approval_v0',AUDIT_DIR]
    chunks=[]
    for base in paths:
        if not base.exists(): continue
        for p in ([base] if base.is_file() else base.rglob('*')):
            if p.is_file(): chunks.append(p.read_text(encoding='utf-8'))
    text='\n'.join(chunks).casefold()
    for phrase in FORBIDDEN:
        if phrase in text: errors.append(f'forbidden Wayback/CDX/Memento connector claim present: {phrase}')
    if re.search(r'\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+',text,re.I): errors.append('Wayback/CDX/Memento governed artifacts contain prohibited private path.')
    if re.search(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',text,re.I): errors.append('Wayback/CDX/Memento governed artifacts contain an email/contact value.')
    if re.search(r'https?://[^\s/]*@|\b(?:file|data|javascript):|https?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)',text,re.I): errors.append('Wayback/CDX/Memento governed artifacts contain private, credentialed, local, file, data, or javascript URL.')

def main(argv:Sequence[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--json',action='store_true'); args=parser.parse_args(argv); report=validate_contract(); print_report(report,args.json); return 0 if report['status']=='valid' else 1
if __name__=='__main__': raise SystemExit(main())
