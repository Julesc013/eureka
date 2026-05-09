# IA Connector Readiness Checklist

IA-BUNDLE-00 does not approve source access.
IA-BUNDLE-00 does not perform external calls.
IA-BUNDLE-00 does not enable a connector.

| Gate | Status | Target |
| --- | --- | --- |
| source policy approval required | pending | IA-BUNDLE-01 |
| User-Agent/contact decision required | pending | IA-BUNDLE-01 |
| allowed IA endpoints pending | pending | IA-BUNDLE-01 |
| forbidden IA endpoints/actions pending | pending | IA-BUNDLE-01 |
| rate limit pending | pending | IA-BUNDLE-01 |
| timeout/retry pending | pending | IA-BUNDLE-01 |
| cache TTL pending | pending | IA-BUNDLE-01 |
| kill switch pending | pending | IA-BUNDLE-01 |
| fixture-only normalizer pending | pending | IA-BUNDLE-01 |
| metadata-only live probe pending | blocked | IA-BUNDLE-02 after approval |
| source cache write pending | blocked | IA-BUNDLE-02 after approval |
| evidence candidate conversion pending | blocked | IA-BUNDLE-02 after approval |
| review queue integration pending | blocked | IA-BUNDLE-02 after approval |
| reviewed-index dry-run pending | blocked | IA-BUNDLE-03 |
| quality delta pending | blocked | IA-BUNDLE-03 |
| postmortem pending | blocked | IA-BUNDLE-03 |

## Current Boundary

- no Internet Archive calls
- no external calls
- no API calls
- no live probes
- no source sync
- no connector runtime
- no source cache writes
- no evidence ledger writes
- no public-index mutation
- no master-index mutation
- no downloads, uploads, accounts, telemetry, hosting, pack import, or hosted
  review
