# Read-Only Boundary

LOCAL-05 keeps the local workbench read-only.

Forbidden in this task:

- POST, PUT, PATCH, DELETE routes
- review decision controls
- WorkUnit controls
- source probe controls
- index rebuild controls
- upload controls
- download/install/execute controls
- LAN controls

The workbench pages use GET forms only.
