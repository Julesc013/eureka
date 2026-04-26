# Backlog Packs

`control/backlog/` holds governed backlog packs that turn audit and eval evidence into prioritized future work.

Backlog packs are not runtime behavior, source connectors, product surfaces, or deployment plans. They sit between audits and implementation prompts:

- audits answer what was observed
- evals answer how current behavior performs
- backlog packs answer what should be done next and why
- runtime work happens only in later implementation milestones

Backlog packs should include structured backlog items, evidence references, acceptance criteria, tests to add first, and explicit "do not do" warnings.

They must not fabricate external baselines, weaken hard evals, claim production readiness, or imply placeholder sources are implemented connectors.
