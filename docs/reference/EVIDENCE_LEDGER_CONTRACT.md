# Evidence Ledger Contract v0

Evidence Ledger Contract v0 defines future evidence observations derived from source cache records, fixtures, source packs, evidence packs, or reviewed observations. The evidence ledger is not truth by default, not production evidence authority, not candidate promotion runtime, and not master-index mutation in P70.

Evidence ledger records preserve evidence identity, kind, subject ref, claim, source cache refs, provenance, observation, confidence, review posture, conflicts, privacy, rights/risk, and hard no-truth/no-runtime/no-mutation guarantees. Confidence is not truth, accepted_as_truth is false, destructive merge is forbidden, and promotion policy plus master-index review are required before authoritative use.

The ledger stores metadata observations and short public-safe snippets only. It does not store raw web/API dumps, private data, executable payloads, credentials, telemetry, downloads, installs, or live source output in P70.

Future relationships are contract-only: source sync workers may produce source cache records; source cache records may support evidence observations; evidence observations may later inform candidates, public index builder inputs, or master-index review queues only after validation and review.
