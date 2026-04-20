# Open Questions

These questions are intentionally left open during bootstrap:

1. What exact object identity boundary should Eureka use for composite software artifacts?
2. Which trust semantics need to be normative in `contracts/archive/trust` for v1?
3. How narrow should the future `runtime/engine/sdk` exposure be if native offline mode exists at all?
4. Which gateway operations belong in the public API versus internal runtime protocols?
5. Which draft job statuses, notices, and result envelope fields should become durable public compatibility promises?
6. Which shared UI state should be standardized across web and native without over-constraining either surface?
7. What is the first durable versioning strategy for archive contracts, gateway contracts, and migration metadata?
8. When should the advisory path-based dependency policy become mechanically enforced, and by what repo-local check?
9. When should the current synthetic connector and normalized-record path expand beyond governed local fixtures into the first real acquisition adapter, and which normalized fields should remain stable when it does?
10. If job execution later becomes asynchronous, which parts of the current bounded job envelope should remain stable?
11. Should submit and read remain one shared public envelope shape, or should they diverge into distinct durable contract types before any real HTTP boundary is introduced?
12. How long should the web workbench remain compatibility-first and server-rendered before any browser-side behavior is introduced, and which view-model fields must stay stable when that happens?
13. Which deterministic search fields and ordering guarantees should survive once the synthetic corpus is replaced by the first real acquisition-backed dataset?
14. Which parts of the bootstrap `resolution_manifest` should survive into a durable manifest or snapshot contract, and which parts should remain explicitly local-export metadata only?
15. Should future bounded actions hang directly off `target_ref`, off read-job results, or off a more explicit resolved-resource identifier once the public API grows beyond the current local deterministic slice?
