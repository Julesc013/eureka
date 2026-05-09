# Local Source Cache Runtime Model

The Track B source cache runtime is a local-foundry helper. It accepts explicit fixture or repo-local source inputs, normalizes them into source cache records, validates source-access and truth/product boundaries, and can build a snapshot for audit evidence.

## Model

A source cache record contains:

- source identity: `source_id`, `source_label`, `source_family`, `source_kind`, `source_locator`
- source posture: `source_access_mode`, `source_policy_status`, `source_authority_posture`
- summaries: coverage, metadata, health, limitations, and observation notes
- relationships: candidate, SearchNeed, WorkUnit, source-lead, pack, and future evidence refs
- gates: review, privacy, rights/risk, truth boundary, product boundary

Snapshots aggregate records by status, type, source family, and access mode. A snapshot is local audit evidence only. It is not a master index, public index, evidence ledger, or accepted source cache.

## Classification

Record types are bounded to source metadata, locator, policy, health, coverage, lead, connector fixture, identity, limitations, access posture, and future approved probe/API/static-dump vocabulary. Current runtime records cannot use future live-probe/API result types.

Statuses are bounded to example, fixture, recorded-local, normalized, observation, candidate, needs-review, policy-blocked, and deferred current cases. Future accepted-public or live-probe status vocabulary is defined only to keep later transitions explicit.

## No Execution

The module uses standard-library data handling only. It does not import networking, browser, provider, subprocess, scraping, or connector libraries, and it does not write files. File output is isolated to the CLI scripts and explicit, policy-checked output paths.
