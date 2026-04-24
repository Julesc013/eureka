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

The current repo does not yet implement durable resolution runs. This belongs
to the next backend program after doctrine consolidation and source-registry
work.
