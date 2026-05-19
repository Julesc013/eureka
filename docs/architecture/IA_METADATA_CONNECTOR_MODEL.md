# Internet Archive Metadata Connector Model

IA-00 is a policy closure task. It approves a future metadata-only local pilot
posture for an Internet Archive metadata connector while keeping runtime
execution disabled.

The approved model is:

```text
fixture replay
-> future approved local live metadata probe
-> source observation
-> source cache
-> evidence candidate
-> review
-> reviewed local index
```

The forbidden model is:

```text
live IA JSON
-> public truth
```

## Current State

Runtime execution disabled in IA-00. No live Archive.org calls, source probes,
downloads, source-cache writes, evidence writes, candidate-index mutation,
reviewed-index mutation, master-index mutation, public-search fanout, model
provider calls, or deployment are approved.

## Future Metadata Scope

The only future endpoint classes approved in principle are:

- small bounded metadata search
- exact identifier item metadata read
- exact identifier file-list metadata read

They may only be used after IA-01 fixture replay hardening and a later IA-02
operator-approved local live metadata probe.

## Truth Boundary

Internet Archive metadata is source observation material. It can help create
candidate claims, but it is not accepted Eureka truth without review. Rights,
safety, compatibility, availability, and source trust cannot be inferred from
metadata alone.

## Runtime Gates

IA-00 does not implement runtime connector code. Later gates must prove fixture
replay, operator approval, User-Agent/contact, rate limits, timeouts, retries,
Retry-After handling, cache behavior, kill switch enforcement, and review gates
before any source-cache or evidence integration is considered.

## IA-01 Fixture Replay

IA-01 adds committed local fixtures and a standard-library-only replay lane. It
parses representative IA metadata shapes, normalizes them into source-
observation candidate records, and emits boundary reports. It does not add a
network-capable connector and it does not write source cache, evidence ledger,
candidate index, reviewed index, or master index state.

## Closed Pilot Model

IA-PILOT-CLOSEOUT-01 closes the metadata-only pilot through IA-07. The proven
local path is:

```text
fixture/live-preview metadata
-> source cache
-> evidence candidates
-> provisional candidates
-> review decisions
-> promotion previews
-> reviewed local records in a temp explicit instance
-> local search/object/absence proof
```

The reusable connector model is a gated source-observation pipeline, not a full
Archive.org integration. Broad source search, public fanout, downloads,
extraction, compatibility truth, rights clearance, malware safety, hosted
public search, master index mutation, production readiness, and public launch
readiness remain outside the approved pilot.
