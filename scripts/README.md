# Scripts

This directory holds lightweight repo support scripts.

Current scripts:

- `check_architecture_boundaries.py`: runs the narrow bootstrap architectural-boundary checker for Python imports and enforces the current proven layering between surfaces, `runtime/gateway/public_api`, connectors, and engine; it emits readable text by default, supports `--json`, and remains a repo-local guardrail rather than a universal policy engine
- `demo_resolution_slice.py`: submits and reads the local deterministic gateway thin slice against governed synthetic fixtures, with an optional shared workbench session view-model projection
- `demo_web_workbench.py`: renders the compatibility-first web workbench, deterministic search page, or bundle inspection page either once to stdout, starts a tiny stdlib local server, exports a bounded resolution manifest as JSON, exports a deterministic resolution bundle ZIP to stdout, stores manifest or bundle exports under a caller-provided local store root, lists stored exports for a target, reads stored artifacts by stable artifact identity, or inspects a local bundle path as JSON, while surfacing the bootstrap `resolved_resource_id` through those flows where available
- `demo_cli_workbench.py`: exposes the same bootstrap exact-resolution, deterministic search, manifest export, bundle export, bundle inspection, and local stored-export capabilities through the first stdlib-only native CLI surface, staying on the public side of the architecture without committing to a final CLI or TUI stack

Current enforced checker rules:

- `surfaces/web/**` must not import `runtime/engine/**` or `runtime/connectors/**`
- `surfaces/native/**` currently follows the same surface-side rule, with the active concrete slice under `surfaces/native/cli/**`
- `surfaces/web/**` and `surfaces/native/**` may import runtime only through `runtime/gateway/public_api/**`
- `surfaces/web/**` and `surfaces/native/**` may import only same-surface helpers under `surfaces/**`
- `runtime/gateway/public_api/**` must not import `surfaces/**`
- `runtime/connectors/**` must not import `surfaces/**`
- `runtime/engine/**` must not import `surfaces/**`

These scripts are bootstrap utilities and repo-local checks, not stable product CLIs or a finalized policy stack.
