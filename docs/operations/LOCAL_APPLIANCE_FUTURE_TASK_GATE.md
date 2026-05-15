# Local Appliance Future Task Gate

Future product work must use the Local Appliance when it affects local runtime
behavior.

Required posture:

- use explicit local instances where applicable
- use runtime composition boundaries
- route background work through WorkUnits
- route accepted results through evidence, review, and index rebuild
- prove search behavior with auto-test or auto-search
- avoid direct master-index mutation
- avoid ad hoc store paths and hidden state roots
- avoid unreviewed truth acceptance
- reject scaffold-only completion

Exceptions require explicit task-scoped rationale and audit evidence.
