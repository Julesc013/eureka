# Scripts

This directory holds lightweight repo support scripts.

Current script:

- `demo_resolution_slice.py`: submits and reads the local deterministic gateway thin slice against governed synthetic fixtures, with an optional shared workbench session view-model projection
- `demo_web_workbench.py`: renders the compatibility-first web workbench, deterministic search page, or bundle inspection page either once to stdout, starts a tiny stdlib local server, exports a bounded resolution manifest as JSON, exports a deterministic resolution bundle ZIP to stdout, stores manifest or bundle exports under a caller-provided local store root, lists stored exports for a target, reads stored artifacts by stable artifact identity, or inspects a local bundle path as JSON, while surfacing the bootstrap `resolved_resource_id` through those flows where available

These scripts are bootstrap utilities, not stable product CLIs.
