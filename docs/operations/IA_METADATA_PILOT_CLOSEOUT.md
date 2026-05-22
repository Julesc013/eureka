# Internet Archive Metadata Pilot Closeout

IA-PILOT-CLOSEOUT-01 closes the Internet Archive metadata pilot as a bounded
local-source vertical slice. It proves a metadata-only path from fixture replay
and one approved live metadata probe through source cache, evidence candidates,
provisional candidates, review decisions, promotion previews, reviewed local
records, and local search/object/absence reads.

This does not prove full Archive.org integration. It does not prove broad IA
search, collection crawl, unbounded paging, downloads, rights clearance, malware
safety, final provenance truth, compatibility truth, hosted public search,
production readiness, or public launch readiness.

## What Works

- IA policy gates define metadata-only access, rate limits, user agent/contact,
  kill switch, and non-claims.
- IA fixture replay parses and normalizes controlled search, item metadata,
  file-list, missing, malformed, 429, large-list, and no-download fixtures.
- The approved live probe performed two metadata-only HTTP requests and
  committed only redacted summaries and normalized previews.
- Source-cache, evidence-ledger, candidate-index, review-queue, and reviewed
  local-index writes are proven in temp explicit instances.
- Search result, object packet, and absence packet reads work over the temp
  rebuilt reviewed local index.

## Temp-Instance Only

IA-03 through IA-07 writes remain temp explicit instance only. They do not
mutate the operator instance, committed `site/dist/data/public_index`, the master index,
or hosted public search.

## Still Disabled

- broad Archive.org search and collection crawl
- downloads, uploads, write APIs, S3 APIs, and authenticated account APIs
- Wayback content replay and arbitrary URL fetch
- extraction and model/provider calls
- deployment, production readiness, and public launch readiness

## Run Validation

```powershell
python scripts/validate_ia_metadata_policy.py
python scripts/validate_ia_fixture_replay.py
python scripts/validate_ia_live_metadata_probe.py
python scripts/validate_ia_source_cache_write.py
python scripts/validate_ia_evidence_ledger_integration.py
python scripts/validate_ia_candidate_index_integration.py
python scripts/validate_ia_review_promotion_dry_run.py
python scripts/validate_ia_reviewed_index_rebuild.py
python scripts/validate_ia_pilot_closeout.py
```

The full temp-instance vertical slice is exercised by the IA-03 through IA-07
validators. Do not run a new live IA probe for closeout.

## SYN Handoff

SYN-00 is now the correct next product task. SYN can use the completed Local,
HUNT, PLAY, and IA proof loop to plan synthetic query foundry behavior without
starting extraction or broad source expansion.

Future source-family work can reuse the policy gate, fixture replay,
metadata-only live-probe envelope, TLS diagnostics, redaction policy,
temp-instance write proofs, non-claim posture, and boundary-report pattern.
