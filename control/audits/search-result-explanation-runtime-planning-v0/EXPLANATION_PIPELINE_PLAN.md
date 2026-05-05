# Explanation Pipeline Plan

Future flow:

1. Public search validates a bounded request.
2. Public/local index returns a public-safe result envelope.
3. Explanation runtime receives only that envelope if enabled.
4. Input policy checks privacy, redaction, no-hidden-score, and no-model rules.
5. Component assembler builds query interpretation without raw private query.
6. Match/recall component explains why the result matched.
7. Source coverage component explains checked and not-checked scope.
8. Evidence/provenance component summarizes refs and caveats.
9. Identity/grouping component explains grouping/dedup relation if present.
10. Ranking component explains ranking factors only when approved ranking output
    exists.
11. Compatibility component explains platform/runtime/dependency caveats.
12. Absence/gap component explains near misses and unchecked areas.
13. Action safety component explains allowed and disabled actions.
14. Copy renderer produces user-facing and audit-readable text.
15. Response includes explanation only after runtime gate approval.
16. No mutation occurs.

