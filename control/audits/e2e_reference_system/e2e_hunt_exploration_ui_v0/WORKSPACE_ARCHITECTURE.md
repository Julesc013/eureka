# Workspace Architecture

`runtime/local/e2e_hunt_exploration.py` builds view-model payloads for workspace, run list, run detail, replay, and compare.

`runtime/local/service/routes.py` exposes those payloads as local service routes.

`surfaces/web/workbench/render_e2e_hunt_exploration.py` renders server-side HTML without JavaScript.

Generated synthetic run bundles are written only under `.eureka/e2e-reference/runs/`.

