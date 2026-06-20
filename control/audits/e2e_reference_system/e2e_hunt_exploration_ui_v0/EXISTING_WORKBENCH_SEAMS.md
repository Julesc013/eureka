# Existing Workbench Seams

- Existing `/search`, `/runs`, `/hunts`, `/needs`, `/review`, and `/rebuild` routes remain in place.
- `/explore` reuses `runtime.resolution_run` for synthetic run bundles and replay.
- `/explore` reuses `runtime.index.preview` for Preview Index search, stats, and status/authority records.
- HTML rendering is added under `surfaces/web/workbench`, consistent with local Workbench rendering.
- The local service keeps public-alpha and LAN safety separate from the private Explore workspace.

