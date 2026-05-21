# Post IA Hunt Bridge Plan

The next recommended task after `IA-HUNT-BRIDGE-00` is:

```text
SYN-00 - Synthetic Query Foundry planning over Local/HUNT/PLAY/IA/Workbench
```

## Why SYN Next

The bridge creates the local path from query or SearchNeed into Hunt, IA WorkUnits, fixture-backed IA metadata pipeline packets, and Workbench result lanes. SYN should pressure-test that path with deterministic query families and adversarial examples before broader domain/scout work.

## Preserve These Boundaries

- no live IA calls by default
- no source probes
- no downloads or extraction
- no model/provider calls
- no deployment or public fanout
- no master-index mutation
- no operator instance mutation unless a reviewed temp/explicit-instance task enables it
- no production or public-launch readiness claim

## Useful Follow-Up Checks

- Exercise synthetic SearchNeeds across Local/HUNT/PLAY/IA/Workbench.
- Confirm blocked and deferred actions stay visible in result lanes.
- Add query taxonomy coverage for metadata-only IA candidates.
- Keep full discovery at batch closeout or promotion, not after every focused repair.
