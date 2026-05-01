# Live Probe Policy

Live Probe Gateway Contract v0 is policy and validation only. It does not
enable live probes and it does not contact external sources.

## Operator Checklist

Before any future source can be enabled, an operator must:

- confirm the source is listed in `live_probe_gateway.json`
- review source terms, robots expectations, and abuse posture
- choose a user-agent policy with project identification
- confirm metadata-only scope
- confirm downloads remain disabled
- confirm arbitrary URL fetching remains disabled
- confirm no user credentials or private account data are used
- confirm per-source timeout and result caps
- confirm cache-first behavior
- confirm evidence records are written
- confirm retry/backoff and circuit breaker behavior
- confirm a per-source disable switch exists
- record explicit signoff

## Source Review

Each source review must record allowed modes, forbidden modes, default result
cap, timeout, cache requirement, evidence requirement, and rollback path.

## Disable Plan

Every future implementation must allow source disablement without code changes.
If a source fails, returns abusive-rate responses, or changes terms, the
operator must be able to turn it off and keep the backend functional.

## Current State

No live probe is implemented. Internet Archive, Wayback, GitHub, Software
Heritage, package registries, and Wikidata candidates are future-disabled.
Google remains manual-baseline only.
## P64 Candidate Index Note

Candidate records may later reference approved probe outputs, but P64 runs no
probes and calls no live sources. Any future live-probe-produced candidate
requires source policy approval, cache/evidence review, rights/risk review,
privacy review, and promotion policy before authoritative use.
