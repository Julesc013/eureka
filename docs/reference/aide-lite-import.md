# AIDE Lite Import

Eureka now carries a target-scoped AIDE Lite import for repo-operating context
discipline. The import is not product runtime behavior and does not define
archive truth, resolver semantics, public API behavior, or provider execution.

Primary generated surfaces:

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/repo-snapshot.json`
- `.aide/context/repo-map.md`
- `.aide/reports/token-savings-summary.md`
- `.aide/queue/EUREKA-AIDE-PILOT-01/`

The Q22 pilot measured the compact task packet at 3792 chars / 948 approximate
tokens against a 274587 char / 68647 approximate-token local naive baseline,
for a 98.6% estimated reduction using `chars / 4`.

Q26 reviewed the import after the repaired AIDE Q25 source pack. The safe
importer now reports zero conflicts in Eureka after refreshing portable AIDE
Lite files, skips broad AIDE roots by default, and preserves Eureka-specific
memory/context/evidence. The current handoff packet is documented in
[AIDE Lite Handover](aide-handover.md).

Limits:

- No exact tokenizer or provider billing claim.
- No provider/model/network calls.
- No Eureka product-code change.
- Actual `.aide.local/` remains ignored and uncommitted.
- Provider/Gateway runtime skeletons were not imported.
- The imported `test` and `selftest` aliases still need a small target-local
  fixture fallback repair before broad AIDE Lite substrate claims.
