# Public Query Observation Runtime Plan

Purpose: planning only for a future privacy-filtered, poisoning-guarded public query observation runtime without implementing it. Readiness decision: `blocked_hosted_deployment_unverified`.
Hosted deployment gate: hosted deployment remains unverified because no hosted backend URL is configured and the configured static site verification is failed/operator-gated. P86 therefore keeps runtime observation blocked and records only a gated implementation plan.
Runtime is not implemented yet because hosted deployment, rate-limit evidence, retention/deletion/backup policy, query guard runtime wiring, storage selection, and operator approval are incomplete.
Safe fields: normalized query fingerprint, intent, target/platform/artifact hints, result-count bucket, miss/gap class, safety decision, timestamp bucket, retention class.
Forbidden fields: raw query, sensitive full query string, IP address, account/session/user identifiers, private paths/URLs, secrets, local machine details, precise geolocation, and exact user-agent unless separately approved.
Privacy/poisoning guard: required before any observation candidate can be retained or aggregated. No telemetry is enabled by this plan.
Storage/retention: planned only; raw query retention defaults to none.
Disabled-by-default flags: EUREKA_QUERY_OBSERVATION_ENABLED=0, EUREKA_QUERY_OBSERVATION_STORE=disabled, EUREKA_QUERY_OBSERVATION_RAW_QUERY_RETENTION=none, EUREKA_QUERY_OBSERVATION_PUBLIC_AGGREGATE=0, EUREKA_QUERY_OBSERVATION_BLOCK_PRIVATE_DATA=1, EUREKA_QUERY_OBSERVATION_BLOCK_POISONING=1.
Integration points: request validation, guard decision, result envelope hook, candidate builder, disabled writer, status flags, operator config, and tests.
Rollback/failure model: store writes must be bounded, non-blocking for safe search responses, fail closed for observation retention, and never log raw queries.
Acceptance criteria: hosted backend verified, safety evidence passed, rate limits present, query guard and observation contracts passed, retention/deletion accepted, storage selected, rollback accepted, operator approval, no raw query retention, no IP/account tracking, disabled-by-default config, full tests passing.
Next steps: preserve the gate and rerun P77/P86 after hosted deployment remediation.
