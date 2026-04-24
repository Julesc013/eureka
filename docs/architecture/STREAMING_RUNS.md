# Streaming Runs

Eureka should treat deeper search and resolution work as a resolution run rather
than a stateless request.

## Resolution Run Model

A durable resolution run should eventually track:

- raw query
- compiled task
- current phase
- completed phases
- remaining work
- partial results
- notices
- checkpoints
- budget
- status

## Why This Matters

This lets the product say things like:

- best current answer
- still checking bundles
- still checking archived vendor pages
- still checking manuals or compatibility traces

Instead of forcing the user into a binary success-or-no-result experience.

## Streaming Phases

Illustrative phases include:

- local or cached results
- deterministic search results
- source metadata results
- decomposition results
- absence summary

The exact phase model is still open, but the principle is accepted: long work
should be resumable and progressively visible.

## Current Status

Resolution Run Model v0 is now implemented as a synchronous local investigation
record for:

- exact resolution
- deterministic search
- planned search backed by a bounded deterministic `resolution_task`

Current v0 behavior is intentionally narrow:

- runs are created and completed synchronously
- runs are persisted as local JSON records under a caller-provided bootstrap
  `run_store_root`
- runs record checked source ids and families through Source Registry v0 where
  current implemented connectors are actually consulted
- planned-search runs may persist one bounded `resolution_task` summary from
  Query Planner v0
- runs surface one current result summary or one absence report
- Local Worker and Task Model v0 now exists separately for synchronous local
  prerequisite work such as source-registry validation, local-index build/query,
  and archive-resolution eval validation, but it does not make resolution runs
  themselves asynchronous or streaming yet

Still deferred here:

- streaming partial results
- explicit phases
- checkpoints and budgets
- worker queues or async orchestration
- full investigation planning and planner-driven retrieval routing
- public hosted or multi-user semantics
