# R0 Contract Taxonomy Remediation

R0-REMEDIATION-CONTRACT-TAXONOMY-01 resolves the 19 unresolved contract taxonomy items left by R0-03B-2.

## Before

- unresolved contract count: 19
- compatibility shim count: 19
- contracts root status: partial

## Actions

- Moved synthetic archive fixtures into `contracts/control_schemas/fixtures/archive/`.
- Moved H14 candidate preview schemas into `contracts/control_schemas/previews/h14/connectors/`.
- Moved work-unit control schemas into `contracts/control_schemas/policies/node/`.
- Moved query candidate/review schemas into `contracts/control_schemas/previews/query/` and `contracts/control_schemas/tasks/query/`.
- Updated active references in current scripts, tests, docs, examples, and control inventories.
- Left historical audit narrative intact.

## Decision

- contracts clean enough for F0: true
- F0 decision: resume_f0
- dev-to-main decision: promotion_plan_only
- production readiness claimed: false
- public launch readiness claimed: false
