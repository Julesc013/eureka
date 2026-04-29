# Project Layout Decision

Proposed future path:

```text
clients/windows/winforms-net48/
```

Rationale:

- `clients/` keeps future native app shells separate from current Python
  runtime, gateway, connectors, and surfaces.
- `windows/` leaves room for later Windows lanes without mixing platform
  families.
- `winforms-net48/` names the UI stack and target framework directly.
- The path avoids implying Windows 7 exclusivity inside the directory name
  while the lane document continues to define Windows 7 SP1+ x64 as the first
  target.

No directory is created by this milestone. The path is reserved in planning
docs only. A future implementation prompt must explicitly approve creating the
directory and any project files.

