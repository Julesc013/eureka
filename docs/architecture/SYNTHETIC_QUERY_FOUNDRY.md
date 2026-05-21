# Synthetic Query Foundry

Synthetic Query Foundry is the local pressure layer over the current Eureka stack:

- LOCAL
- HUNT
- PLAY
- IA metadata pilot
- Workbench result lanes
- IA-HUNT bridge

The foundation is example-only. It defines deterministic query cases and query sets that let validators and future local eval tools pressure the stack without inventing user demand or truth.

## Contract Posture

SYN-00 adds:

- `contracts/query/synthetic_query_case.v0.json`
- `contracts/query/synthetic_query_set.v0.json`
- demo, hard, and adversarial query set examples
- SearchNeed seed bridge examples
- WorkUnit seed bridge examples

The contracts define pressure cases, expected lanes, and seed mappings. They do not create runtime query logs, SearchNeeds, WorkUnits, evidence, candidates, source-cache records, reviewed-index records, or master-index records.

## Stack Relationship

Demo cases verify the happy path: local reviewed results, scoped absence, and IA metadata candidates can project into result lanes.

Hard cases carry legacy software and media questions from PLAY into review-gated SearchNeed and WorkUnit seed posture.

Adversarial cases pressure policy gates: unsafe acquisition, private/local-state pressure, live IA call requests, and extraction requests must remain blocked or deferred.

## Boundaries

SYN-00 does not enable:

- source probes
- live IA calls
- downloads or uploads
- extraction
- model/provider calls
- synthetic generation runtime
- runtime SearchNeed creation
- runtime WorkUnit creation
- operator instance mutation
- master-index mutation
- public search behavior changes
- deployment
- production readiness claims
- public launch readiness claims

The next task can use these pressure sets to plan domain packs, but it must not treat synthetic cases as observed demand or accepted evidence.
