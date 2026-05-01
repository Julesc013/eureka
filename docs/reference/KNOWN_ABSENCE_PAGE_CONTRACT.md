# Known Absence Page Contract v0

Known Absence Page v0 defines a future public-safe explanation envelope for unresolved searches. Scoped absence, not global absence, is the governing rule: a page may describe what Eureka checked, what was not checked, why a verified result was not found, and what safe next actions may exist.

A known absence page is not a runtime page yet. A known absence page is not evidence acceptance. A known absence page is not candidate promotion. A known absence page is not master-index mutation.

## Page Shape

The contract records query context, an absence summary, checked and not-checked scope, near misses, weak hits, gap explanations, source status, evidence context, candidate context, safe next actions, user-facing sections, an API projection, a static projection, privacy, rights/risk, limitations, and hard no-global-absence/no-mutation guarantees.

## Checked Scope

Checked scope lists the specific indexes, source families, capabilities, and snapshot refs used by the explanation. Not-checked scope lists sources, source families, capabilities, and reasons not checked. The page must never imply an exhaustive search.

## Near Misses And Gaps

Near misses and weak hits are public-safe summaries only. They do not embed raw result payloads and do not become verified results. Gap explanations name source coverage, capability, compatibility evidence, member access, representation, query interpretation, live-probe-disabled, external-baseline, deep-extraction, OCR, source-cache, or policy limits.

## Safe Actions

No download/install/upload/live fetch action is enabled by P66. Informational actions such as refining the query, viewing near misses, or viewing checked sources may be enabled in examples. Future actions such as manual observation, source/evidence pack submission, search need creation, probe queueing, live probes, deep extraction, or OCR remain future-only and require approval where applicable.

## API And Static Projection

The API projection is a contract model for a future `known_absence_response` compatible with search responses. It is not runtime API implementation. The static projection documents how a no-JS demo could be rendered, but P66 does not generate a static artifact.

## Privacy Rights And Risk

Raw query retention defaults to none. Public-safe examples must not contain raw private queries, private paths, secrets, private URLs, account identifiers, IP addresses, or private local result identifiers. Rights clearance and malware safety are not claimed.

## Relations

Known absence pages can reference query observations, shared result cache entries, miss ledger entries, search needs, probe queue items, candidate records, and promotion-policy context. These references are explanatory only and do not create, update, or promote those records.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

Query privacy and poisoning guard decisions are a future contract-only input for known absence pages. A known absence explanation should only use public-safe, privacy-filtered, poisoning-checked query context and must not let fake demand, source-stuffing, candidate-poisoning, private paths, secrets, IP addresses, account IDs, or private URLs into public aggregate learning. P67 does not create runtime known absence pages.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->
