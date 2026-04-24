# Product Promise

Eureka's core promise is:

> Find, verify, compare, explain, and act on archived and current digital
> objects with minimal user detective work.

That promise implies a resolver that can help users answer questions such as:

- what is the thing I probably mean
- which version, state, or representation is the right one
- where is the useful artifact hidden
- can I use it on this machine or under these constraints
- what evidence supports that answer
- what did the system check when it could not find a direct hit

## User-Facing Expectations

When the resolver is behaving well, users should be able to expect:

- direct answers before bulky parent bundles when inner artifacts are known
- source-backed evidence instead of unexplained confidence
- compatibility and action guidance without pretending certainty
- explicit disagreement when sources conflict
- explicit absence reasoning when the exact target is not found
- resumable deeper work rather than a flat "no results" stop

## Scope Honesty

The promise above is the north star, not a claim that current bootstrap slices
already fulfill every part of it.

Current repo work proves bounded parts of the promise:

- exact resolution
- deterministic search
- evidence visibility
- miss explanation
- representations and access paths
- compatibility hints
- action routing
- decomposition and member readback

Longer-term parts such as streaming investigation, resolution memory,
production indexing, live federation, and public-hosted safe operation are
planned but not yet implemented.
