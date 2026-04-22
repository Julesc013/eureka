# Open Questions

These questions are intentionally left open during bootstrap:

1. What exact object identity boundary should Eureka use for composite software artifacts?
2. Which trust semantics need to be normative in `contracts/archive/trust` for v1?
3. How narrow should the future `runtime/engine/sdk` exposure be if native offline mode exists at all?
4. Which gateway operations belong in the public API versus internal runtime protocols?
5. Which draft job statuses, notices, and result envelope fields should become durable public compatibility promises?
6. Which shared UI state should be standardized across web and native without over-constraining either surface?
7. What is the first durable versioning strategy for archive contracts, gateway contracts, and migration metadata?
8. How far should the current narrow Python import checker grow beyond the bootstrap rules it enforces today, and which additional boundaries are worth checking before it becomes noisy or overcommitted?
9. After the first recorded GitHub Releases connector slice, which real source family should follow next, and which normalized fields should stay stable across source families?
10. If job execution later becomes asynchronous, which parts of the current bounded job envelope should remain stable?
11. Should submit and read remain one shared public envelope shape, or should they diverge into distinct durable contract types before the current local bootstrap HTTP API is expanded into any durable network-facing contract?
12. How long should the web workbench remain compatibility-first and server-rendered before any browser-side behavior is introduced, and which view-model fields must stay stable when that happens?
13. Which deterministic search fields and ordering guarantees should survive as the bounded corpus grows beyond synthetic fixtures plus recorded GitHub Releases fixtures?
14. Which parts of the bootstrap `resolution_manifest` should survive into a durable manifest or snapshot contract, and which parts should remain explicitly local-export metadata only?
15. Should future bounded actions hang directly off `target_ref`, off read-job results, or off a more explicit resolved-resource identifier once the public API grows beyond the current local deterministic slice?
16. Which parts of the bootstrap `resolution_bundle` should survive into a durable portable bundle or snapshot contract, and which parts should remain explicitly local-export packaging only?
17. When the bundle inspection path stops using a local filesystem path for demos, what durable upload or import boundary should replace it without overcommitting restore semantics?
18. Which local store semantics should remain durable if the bootstrap content-addressed store later grows into a broader cache or database layer, and which parts should stay explicitly demo-only?
19. Which inputs should continue to participate in bootstrap `resolved_resource_id` derivation as more real external sources arrive after GitHub Releases, and which parts of that derivation should remain local implementation detail rather than contract?
20. At what point should `resolved_resource_id` become a first-class public compatibility promise rather than a bootstrap deterministic seam carried opportunistically through current envelopes?
21. How should the current local `/api/...` bootstrap routes relate to the draft `/v0/...` public API contract paths if Eureka later promotes this slice beyond a local stdlib proof?
22. Which bounded evidence-summary fields introduced in the current bootstrap seam should survive into a durable provenance or claim contract, and which should remain explicitly replaceable implementation detail?
23. Which bounded comparison categories introduced in the current bootstrap seam should survive into a durable side-by-side comparison contract, and which should remain explicitly local and replaceable before any future merge or truth-selection work?
24. Which parts of the current bootstrap `subject_key` grouping plus deterministic state-ordering rule should survive into a durable object/state identity contract, and which parts should remain explicitly replaceable before any broader temporal or merge semantics are introduced?
25. Which parts of the current bounded absence reports, near-match hints, and reason codes should survive into a durable diagnostic contract, and which should remain explicitly replaceable before any future ranking, trust, or broader reasoning work?
