# Exec Plan

## Goal

Add deterministic Eureka-specific AIDE golden tasks and prove they pass in the
target repo before moving to real product-adjacent work.

## Steps

1. Inspect current AIDE Lite eval catalog, runner, tests, and latest packet.
2. Add six Eureka-specific golden task definitions and acceptance docs.
3. Extend the existing AIDE Lite eval runner rather than adding a new framework.
4. Add focused tests proving the target-specific tasks pass in a minimal fixture.
5. Run AIDE Lite validation, regenerate reports and packets, and write evidence.
6. Leave status as `needs_review`.

## Boundaries

- Writes stay under `.aide/**`.
- No Eureka product source or product test files are changed.
- No provider/model/network calls are introduced.
- No `.aide.local/`, `.env`, secrets, raw prompts, or raw responses are stored.

## Current Status

- Golden task implementation is complete.
- `eval list` shows 12 tasks including six Eureka-specific tasks.
- `eval run` passes 12/12.
- Final validation and review are recorded in evidence.
