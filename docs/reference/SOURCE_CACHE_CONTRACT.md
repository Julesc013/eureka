# Source Cache Contract v0

Source Cache Contract v0 defines future public-safe source metadata summaries. The source cache is not live connector runtime, not arbitrary URL cache, not a raw payload store, not a private data store, not an executable payload store, and not production persistence in P70.

Source cache records preserve source refs, cache identity, cache kind, source policy, acquisition context, payload summary, normalized metadata, freshness, provenance, fixity, privacy, rights/risk, and hard no-runtime/no-mutation guarantees. Runtime source cache is contract-only and not implemented.

Future live source cache entries require approved source sync workers, source policy review, rate limits, timeouts, circuit breakers, descriptive User-Agent policy, source terms review, cache-first handling, and evidence attribution. Public queries must not fan out live to source cache writes.

Source cache records may feed the future evidence ledger, candidate index, public index builder, or master index review queue only after validation, review, promotion policy, and contract-specific runtime work. P70 performs no source cache mutation, evidence ledger mutation, candidate mutation, public/local/master index mutation, telemetry, credentials, downloads, installs, execution, or external calls.
