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

Current v0 behavior is intentionally narrow:

- runs are created and completed synchronously
- runs are persisted as local JSON records under a caller-provided bootstrap
  `run_store_root`
- runs record checked source ids and families through Source Registry v0 where
  current implemented connectors are actually consulted
- runs surface one current result summary or one absence report

Still deferred here:

- streaming partial results
- explicit phases
- checkpoints and budgets
- worker queues or async orchestration
- query-planner-owned run compilation
- public hosted or multi-user semantics
