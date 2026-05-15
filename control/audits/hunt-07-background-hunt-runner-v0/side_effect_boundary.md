# Side Effect Boundary

Allowed side effects:

- WorkUnit state transition history.
- Worker result records.
- Worker audit records.
- Search Hunt runner history records.

Forbidden side effects:

- Source probes.
- Extraction.
- Model/provider calls.
- Acquisition or launch actions.
- Source sync.
- LAN worker mutation.
- Deployment.
- Master index mutation.

