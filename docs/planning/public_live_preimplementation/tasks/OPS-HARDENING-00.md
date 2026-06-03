# OPS-HARDENING-00

Goal: make public Eureka reversible and maintainable.

Inputs to read first: `operations/*.md`, existing public alpha hosting and
rollback docs.

Allowed paths: docs/operations, release/hosting, runtime hosting only if later
authorized, tests/hosting.

Protected paths: public launch without approval.

Deliverables: backup/restore, rollback, monitoring, rate limits, incident,
privacy, takedown, disable switches, security review.

Non-goals: new product features.

Validation: hosting/readiness/rollback/security focused tests.

Exit criteria: bad deploy, bad source, bad index build, and bad renderer are
reversible.

Impact statement: operations/release impact.

