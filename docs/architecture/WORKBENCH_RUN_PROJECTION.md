# Workbench Run Projection

The Workbench run projection translates kernel packets into projection-safe surfaces:

- `operator_workbench`: full local operator detail, still read-only
- `public_web`: summary only, operator-only fields hidden
- `native_desktop_read_only`: summary only, read-only

Projection rules:

- surfaces render packets and links
- runtime produces run packets, event packets, lane snapshots, WorkUnit plans, command outcomes, and boundary reports
- blocked commands return policy responses and do not mutate run state
- exact machine names for blocked actions remain in JSON; HTML uses presentation-safe labels so local page hardening does not imply enabled controls

The projection seam is intentionally local and bounded. Future IA live metadata, review/promote, and apply gates should attach to the kernel command path instead of adding source-specific behavior to the Workbench page.
