# Public Alpha

Public hosting is not the next step. It is a later milestone that should begin
only after the backend has a safer and more coherent operational shape.

## Minimum Requirements Before Hosting

The minimum public-alpha entry gate should include:

- Source Registry v0 (implemented)
- Resolution Run Model v0 (implemented)
- Query Planner v0 (implemented)
- Local Index v0 (implemented)
- Local Worker and Task Model v0 (implemented)
- Resolution Memory v0 (implemented, local-only)
- Archive Resolution Eval Runner v0 (implemented as a local regression guardrail)
- public-alpha-safe configuration
- local-path APIs disabled or explicitly restricted
- safe store-root handling
- a basic health route
- clear alpha disclaimers

## Public Alpha Safe-Mode Expectations

A public alpha should assume:

- no unrestricted filesystem path access
- no private user memory
- no hidden access to local store roots outside configured safe paths
- no hidden access to local memory-store roots outside configured safe paths
- no assumption that auth or user accounts exist yet
- no silent escalation from local bootstrap behavior into public network
  behavior

## What The Alpha Should Include

A credible small public alpha should be able to expose:

- search
- exact resolution
- evidence visibility
- miss explanation
- representation and access-path visibility
- bounded next-step guidance
- safe fetch behavior where explicitly allowed

## What The Alpha Should Not Include

The public alpha should not yet include:

- installer automation
- account system
- private user memory
- large-scale crawling
- background OCR
- broad downloads
- native app sync

## Current Status

Public alpha preparation is the next backend milestone, but public hosting
itself is not started. Source Registry v0, Resolution Run Model v0, Query
Planner v0, Local Index v0, Local Worker and Task Model v0, Resolution Memory
v0, and Archive Resolution Eval Runner v0 now satisfy the backend prerequisite
set. The hosted-alpha gate is still blocked on public-safe configuration,
route hardening, and local-path restrictions.
