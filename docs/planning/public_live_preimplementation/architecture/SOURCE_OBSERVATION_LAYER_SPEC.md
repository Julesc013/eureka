# Source Observation Layer Spec

## Rule

Adapter output is `SourceObservation` only. A SourceObservation may support an
EvidenceCandidate or SearchNeed. It cannot create reviewed truth.

## Current Repo Paths

- `contracts/source/action/source_observation_envelope.v0.json`
- `contracts/runtime/source/observation.v0.json`
- `runtime/source/observation/**`
- `runtime/source/action/**`
- `runtime/connectors/**`

## IA Metadata Scope

Internet Archive metadata may be used as bounded metadata evidence support and
candidate generation. It is not crawling, downloading, Wayback replay,
extraction, rights clearance, malware proof, or verified artifact truth.

## Failure States

- source timeout
- source unavailable
- source policy denied
- source budget exceeded
- source output invalid
- source unsupported

