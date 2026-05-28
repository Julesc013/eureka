# Architecture Docs

This directory contains accepted and proposed architecture models for Eureka.
Read these documents as bounded direction, not as automatic evidence that every
model is implemented in the current runtime.

## Start Here

- [Temporal Object Resolver](TEMPORAL_OBJECT_RESOLVER.md)
- [Local Product Loop](LOCAL_PRODUCT_LOOP.md)
- [Workbench Local Loop](WORKBENCH_LOCAL_LOOP.md)
- [Public Alpha Launch Candidate](PUBLIC_ALPHA_LAUNCH_CANDIDATE.md)
- [Snapshot Relay](SNAPSHOT_RELAY.md)
- [Source Action Kernel](SOURCE_ACTION_KERNEL.md)
- [Source Family Model](SOURCE_FAMILY_MODEL.md)
- [Rust Backend Lane](RUST_BACKEND_LANE.md)
- [AI Policy](AI_POLICY.md)

## Current Boundaries

The current executable lane is the Python reference runtime. Public-alpha
routes are read-only and snapshot-backed. Public live source fanout, downloads,
uploads, broad extraction, model/provider calls, public mutation, and native
marketplace behavior remain disabled or gated.

Architecture proposals that describe future source families, native clients,
relay behavior, AI assistance, or action manifests require separate
implementation and validation evidence before they become product behavior.
