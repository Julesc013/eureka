# Query Privacy Poisoning Guard Contract v0

Query Privacy and Poisoning Guard v0 defines a contract-only decision record for deciding whether a query or derived query-intelligence object is allowed, redacted, local-private, rejected, quarantined, future-throttled, or excluded from public aggregate learning.

The guard is not runtime yet. The guard is not telemetry. The guard is not WAF/rate limiting by itself. The guard is not truth/source trust. Guard approval does not mean candidate promotion, rights clearance, malware safety, or master-index acceptance.

## Decision Shape

`contracts/query/query_guard_decision.v0.json` records input context, privacy risks, poisoning risks, policy actions, redaction, aggregate eligibility, retention policy, query-intelligence eligibility, public-search projection, review requirements, limitations, and hard no-runtime/no-mutation guarantees.

## Privacy Risks

Privacy risks cover raw query retention risk, private path detection, credential detection, API key detection, auth token detection, password detection, private key detection, email detection, phone detection, IP address detection, account identifier detection, private URL detection, local identifier detection, user file name detection, long sensitive text, copyrighted text dump risk, executable payload reference risk, and unknown risk. Raw query retention default none.

## Poisoning Risks

Poisoning risks cover spam query, repeated fake demand, source-stuffing, candidate-poisoning, malicious identifier stuffing, prompt-injection-like text, policy bypass attempts, live-probe forcing attempts, arbitrary URL fetch attempts, download/install/execute forcing attempts, source reputation attacks, rank manipulation attempts, near-duplicate floods, unsupported parameter abuse, future bot-like patterns, and unknown risk.

## Policy Actions

Actions include allow public-safe, allow redacted, keep local-private, reject sensitive, quarantine for review, exclude from public aggregate, exclude from candidate generation future, exclude from probe queue future, throttle future, require human review, require policy review, or no action. Automatic acceptance is forbidden.

## Redaction Model

Redaction can remove raw query text, replace private paths, replace secrets, replace private URLs, truncate long text, hash identifiers, or reject without redaction. Committed examples use redacted placeholders only.

## Aggregate Eligibility

Public aggregate learning may use only coarse safe fields after privacy and poisoning checks. High or critical privacy risk disallows public aggregate. High or critical poisoning risk disallows public aggregate. Fake demand, spam, source-stuffing, and candidate-poisoning must not become demand counts.

## Query-Intelligence Object Guard Policy

Query observation, shared result cache, miss ledger, search need records, probe queue items, candidate index records, candidate promotion assessments, and known absence pages should pass guard policy before future public aggregation or derived-object creation. P67 does not mutate those objects.

## Public Search Relation

Public search integration is future/contract-only. P67 does not change public search behavior, persist guard decisions, block new runtime cases, emit telemetry, track accounts, track IPs, create query logs, or mutate public/local/master indexes.

## Future Work

Future runtime would require retention design, deletion/export support, production abuse controls outside this contract, operator controls, bounded rate limits, review evidence, deployment evidence, and explicit integration tests.

## Demand Dashboard v0 Relation

Demand Dashboard v0 is future/contract-only. It can later summarize privacy-filtered and poisoning-guarded aggregate demand, but P68 adds no telemetry, public query logging, account/IP tracking, real demand claims, runtime dashboard, candidate promotion, source sync, source cache/evidence ledger mutation, public-search ranking change, or index mutation.
