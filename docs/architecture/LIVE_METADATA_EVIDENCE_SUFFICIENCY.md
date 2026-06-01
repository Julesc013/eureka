# Live Metadata Evidence Sufficiency

Evidence sufficiency measures whether a redacted metadata observation is useful enough for a limited preview.

Reviewed fields include candidate id, title, source family, redacted locator hash, request plan reference, source observation reference, query context, and SCOUT trail references.

Evidence sufficiency does not imply:

- file availability
- safe installer status
- extracted file contents
- malware cleanliness
- rights clearance
- production readiness

Low or duplicate sufficiency results remain `needs_more_evidence`, `duplicate`, or `useful_lead` until more reviewed evidence exists.
