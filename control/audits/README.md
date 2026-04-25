# Audit Packs

`control/audits/` holds repo-governance audit packs. These packs are evidence
and planning artifacts, not product runtime behavior and not public product
claims.

An audit pack should be grouped under a dated directory and should include:

- a baseline record
- commands run or intended for final verification
- structure, content, behavior, and test-gap audits
- structured findings using `control/audits/schemas/finding.schema.json`
- backlog and next-milestone recommendations
- explicit non-goals and deferred items

Audit findings should map to future-work labels and should avoid vague
"improve everything" recommendations. If a finding depends on external search
quality, mark the external observation as pending manual evidence rather than
fabricating a baseline.

Audit packs must not be used to claim production readiness. Public-alpha
material remains supervised-demo evidence only until a separate accepted
hosting decision exists.

