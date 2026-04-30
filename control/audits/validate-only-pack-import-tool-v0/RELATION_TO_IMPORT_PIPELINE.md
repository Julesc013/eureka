# Relation To Import Pipeline

Validate-Only Pack Import Tool v0 connects two earlier milestones:

- Pack Import Validator Aggregator v0 validates pack roots.
- Pack Import Report Format v0 records validation outcomes.

This milestone combines them into a preflight command. It is still not import.

Future milestones may add:

- local quarantine/staging model
- staged pack inspector
- validate-only report review UX
- local index candidate import after explicit opt-in
- contribution queue candidate export

Those future milestones must remain private-by-default and review-gated. They
must not treat validation success as canonical truth, rights clearance, malware
safety, or master-index acceptance.
