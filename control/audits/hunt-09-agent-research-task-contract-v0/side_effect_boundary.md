# Side Effect Boundary

Allowed:

- Create disabled local task records.
- Read report schema.
- Show task records in CLI/API/UI.

Forbidden:

- Model/provider calls.
- Browser calls.
- Source probes.
- Extraction.
- Downloads.
- Review decisions.
- Public or master index mutation.
- Deployment.
