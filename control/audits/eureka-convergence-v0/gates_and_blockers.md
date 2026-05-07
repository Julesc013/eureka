# Gates And Blockers

These gates apply after `EUREKA-CONVERGE-01` unless a future reviewed task
explicitly narrows or changes them.

## Product And Truth Gates

- No public truth from candidates.
- No master-index mutation.
- No automatic acceptance.
- No destructive merge or deduplication.
- No AI truth.
- No source trust, rights clearance, malware safety, installability, or
  compatibility oracle claim without evidence.

## Runtime And Source Gates

- No live probes.
- No broad crawling or scraping.
- No arbitrary URL fetching.
- No source connector runtime before approval.
- No public-query fanout to external sources.
- No downloads, installers, execution, package-manager invocation, emulator, or
  VM behavior.
- No uploads, accounts, telemetry, private user memory, or private path search.

## Hosting Gates

- No hosted backend claim.
- No production API claim.
- No DNS/TLS/rate-limit/edge/monitoring claim without operator evidence.
- No full hosting before Track E.
- Early public-alpha-shaped work means local/staging/static proof only.
- Actual hosted public alpha is Track E only.

## Native And Relay Gates

- No native project creation before Track C.
- No relay runtime before Track D approval.
- No socket listener, protocol server, private-data relay, or live backend proxy
  before an explicit relay implementation task.
- No production signed snapshots, real signing keys, or public `/snapshots/`
  route before Track D/Track E gates.

## AIDE Gates

- AIDE Lite may generate compact context, evidence, and validation reports.
- AIDE Lite must not define product semantics or runtime truth.
- Future tasks should start from `.aide/context/latest-task-packet.md`.
- Full chat history should not be pasted when compact packets exist.
