# Eureka Node Capabilities

A node capability is one design-time vocabulary entry for what a Eureka Node may eventually do under a manifest and policy.

A capability record binds a capability ID to compatible node modes, input/output categories, side-effect class, network/source/model/credential/local-state requirements, review gates, and truth boundaries.

## Current Side Effects

Current capability examples may only use read-only, committed-fixture, validate-only, report-only, dry-run-report-only, or blocked side-effect classes. They do not create local state, call networks, call models or providers, fetch sources, run WorkUnits, import packs, submit packs, or mutate public records.

## Future Side Effects

Future side effects such as local-state writes, local index writes, source-cache writes, evidence-ledger writes, pack drafts, pack exports, network probes, model calls, and hosted execution require explicit future runtime tasks and policy approval. Declaring the vocabulary does not activate those side effects.

## Review Gates

Capabilities may relax review gates only when they are strictly local read-only or validate-only and have no public/export/truth effect. Future capabilities that touch sources, models, credentials, local state, hosted behavior, evidence, candidates, packs, or WorkUnits must retain human, operator, source-policy, risk, and master index review boundaries.

## Relationship To WorkUnits

Capabilities prepare the vocabulary for WorkUnit contracts. A WorkUnit may later require capabilities, but this milestone does not run WorkUnits or create a WorkUnit runtime.
