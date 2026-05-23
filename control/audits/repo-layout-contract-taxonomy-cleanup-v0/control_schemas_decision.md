# Control Schemas Decision

Decision: retain `contracts/schema/control/` as control schema authority with migration
backlog.

Allowed scope: control/governance schemas only.

Product contracts under `contracts/schema/control/`: not allowed.

Migration task: `REPO-LAYOUT-CONTRACT-AUTHORITY-MIGRATION-01`.

Rationale: avoid broad moves in R0-03, lock authority first, migrate later with
validators and reference updates.
