# Read-Only Boundary

HUNT-02 allows only GET routes for Search Hunt UI/API state.

Forbidden in this task:

- hunt creation UI or API
- hunt state changes
- WorkUnit creation
- source probes
- model/provider calls
- review mutation
- public or master index mutation
- deployment

