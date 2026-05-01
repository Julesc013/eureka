# Source Cache Contract v0

Source Cache Contract v0 defines future public-safe source metadata summaries. The source cache is not live connector runtime, not arbitrary URL cache, not a raw payload store, not a private data store, not an executable payload store, and not production persistence in P70.

Source cache records preserve source refs, cache identity, cache kind, source policy, acquisition context, payload summary, normalized metadata, freshness, provenance, fixity, privacy, rights/risk, and hard no-runtime/no-mutation guarantees. Runtime source cache is contract-only and not implemented.

Future live source cache entries require approved source sync workers, source policy review, rate limits, timeouts, circuit breakers, descriptive User-Agent policy, source terms review, cache-first handling, and evidence attribution. Public queries must not fan out live to source cache writes.

Source cache records may feed the future evidence ledger, candidate index, public index builder, or master index review queue only after validation, review, promotion policy, and contract-specific runtime work. P70 performs no source cache mutation, evidence ledger mutation, candidate mutation, public/local/master index mutation, telemetry, credentials, downloads, installs, execution, or external calls.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval

`docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md` defines an approval-only, metadata-only future Internet Archive connector pack. It is not runtime, makes no external calls, enables no public-query fanout, performs no downloads/file retrieval/mirroring, and mutates no source cache, evidence ledger, candidate index, public/local/master index, telemetry, or credentials. Future work is blocked on official source policy review, User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit breakers, cache-first source cache output, and evidence ledger attribution.

This cross-reference keeps `docs/reference/SOURCE_CACHE_CONTRACT.md` aligned with the source-ingestion boundary: IA metadata may become future reviewed cache/evidence input, never direct truth or live public search fanout.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

P72 defines a future availability/capture-metadata-only Wayback/CDX/Memento connector approval pack. The connector is not implemented, no external calls are made, public queries do not fan out to Wayback/CDX/Memento, arbitrary URL fetch is forbidden, archived content fetch/capture replay/WARC download are forbidden, and future outputs must be cache-first/evidence-first after URI privacy review and approval.
