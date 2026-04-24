# Physical Subsystems

The long-term backend should be described through five physical subsystems.
They should be implemented in stages rather than built all at once.

## 1. Blob and CAS Store

Purpose:

- store raw and derived bytes
- support content-addressed identity
- preserve downloads, captures, extracted members, manifests, and later OCR or
  replay artifacts

Typical contents:

- downloads
- source captures
- extracted members
- package payloads
- metadata snapshots
- later OCR outputs
- later WARC or WACZ captures

## 2. Relational Canonical Core

Purpose:

- hold authoritative typed records for normalized objects, states,
  representations, evidence, access paths, runs, memory, and dependencies

Likely record families:

- sources
- source records
- objects
- representations
- states
- agents
- claims
- evidence
- identifiers
- access paths
- edges
- resolution runs
- resolution memories
- invalidation dependencies

Current bootstrap status:

- Resolution Run Model v0 is now implemented locally as JSON-backed run records
- Resolution Memory v0 is now implemented locally as JSON-backed reusable
  investigation memory records
- the relational canonical core remains a later physical subsystem; current run
  and memory stores are bounded bootstrap-local persistence only

## 3. Lexical and Search Index

Purpose:

- support title, filename, member-path, full-text, and fielded search
- support filters and constrained queries over source, time, platform, and
  actionability

Typical indexed material:

- title text
- filename text
- member paths
- snippets
- facets
- constrained fields such as platform, source family, and dates

Current bootstrap status:

- Local Index v0 is now implemented under `runtime/engine/index/`
- SQLite is the first local index substrate
- FTS5 is preferred when available
- deterministic fallback query behavior exists when FTS5 is unavailable
- current indexed material is intentionally bounded and compact rather than a
  final ranking or retrieval engine

## 4. Vector and Semantic Recall Index

Purpose:

- optional later support for semantic recall, vague title matching,
  similar-query memory, alias discovery, and reranking support

This subsystem is explicitly optional later. It is not the source of truth.

## 5. Queue and Worker Plane

Purpose:

- run source sync, extraction, package parsing, index updates, identity
  clustering, and later deeper work such as OCR or replay processing

Required qualities:

- idempotent
- checkpointed
- cancelable
- resumable
- priority-aware
- dependency-tracked

Current bootstrap status:

- Local Worker and Task Model v0 is now implemented under
  `runtime/engine/workers/`
- task execution is synchronous and local only
- task persistence is JSON under a caller-provided bootstrap `task_store_root`
- current v0 task kinds wrap Source Registry v0 validation, Local Index v0
  build/query, and archive-resolution eval validation
- this is not a distributed queue, background scheduler, retry system, or
  production worker plane yet

## Staged Implementation Direction

The next backend phase should not attempt all five subsystems at production
scale immediately.

Near-term staging should look more like:

1. local filesystem CAS and bounded local store behavior
2. local relational and lexical index, likely SQLite plus FTS first
3. local worker and task model (implemented)
4. durable run and memory models (implemented locally as JSON-backed bootstrap seams)
5. only later optional vector recall, broader worker orchestration, and shared
   evidence services
