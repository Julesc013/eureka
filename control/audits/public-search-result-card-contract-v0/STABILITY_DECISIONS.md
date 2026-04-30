# Stability Decisions

The card contract is stable-draft where old clients need predictable rendering:
identity, title, lane, source, user-cost, public evidence summaries, actions,
warnings, limitations, rights caveats, and risk caveats.

Experimental fields are useful for richer future interfaces but may change
before runtime implementation. This includes detailed compatibility confidence,
ranking explanation, trust lanes, parent/member details, representation details,
and public link affordances.

Volatile fields are intentionally limited. The contract allows source coverage
and summary wording to change as the local index grows, but does not allow
private paths, raw payloads, credentials, executable trust claims, rights
clearance claims, or malware-safety claims.

Internal fields are explicitly forbidden from public cards. Internal row ids,
private local paths, source credentials, raw source payloads, operator-local
store roots, and live fetch locators must remain outside the public envelope.

Future fields are reserved for object truth, state/release modeling, debug
diagnostics, and gated workflows. Future fields do not make those features live.

## User-Cost Decision

`user_cost.score` is a stable-draft bounded hint from 0 through 9. Lower scores
mean less user detective work. The value is not a production ranking guarantee
and must remain explainable through `user_cost.reasons` and `why_ranked`.

## Action Decision

The card must show unsafe actions as blocked or future-gated instead of omitting
them silently. This gives every client a consistent way to explain why Eureka
does not offer downloads, installs, execution, uploads, or private-source
submission in v0.
