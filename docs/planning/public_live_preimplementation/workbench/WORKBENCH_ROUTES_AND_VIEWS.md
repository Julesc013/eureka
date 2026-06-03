# Workbench Routes And Views

Candidate routes:

- `/run/{id}`
- `/workunit/{id}`
- `/candidate/{id}`
- `/evidence/{id}`
- `/review/{id}`
- `/index-build/{id}`
- `/need/{id}`

Each view should show canonical status, source/evidence posture, policy posture,
review state, and next operator action. Fallback-derived candidates and needs
must be visibly tied to the originating run and WorkUnit.

