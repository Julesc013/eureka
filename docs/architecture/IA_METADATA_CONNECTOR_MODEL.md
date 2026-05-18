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
