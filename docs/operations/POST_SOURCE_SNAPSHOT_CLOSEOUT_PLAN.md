
# Post Source Snapshot Closeout Plan

1. Repair public search index generated drift without violating public-index mutation policy.
2. Repair governed example pack and candidate/search checksum manifests with the owning generators.
3. Reconcile historical HUNT/LOCAL queue validators with the post-source/snapshot task ledger.
4. Reconcile legacy runtime leakage gate findings in a dedicated taxonomy/leakage remediation task.
5. Rerun full unittest discovery.
6. Start `DEV-TO-MAIN-PROMOTION-REVIEW-03` only after full discovery is green.
7. Start `PUBLIC-ALPHA-READONLY-00` only after promotion.
