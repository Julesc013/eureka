# Source, Evidence, Index, Contribution, And Pack-Set Handling

Source packs:

- classify source inventory/source-cache candidate effects
- perform no live source calls
- perform no source-cache mutation

Evidence packs:

- classify evidence observation candidate effects
- keep `accepted_as_truth` false
- perform no evidence-ledger mutation

Index packs:

- compare-only future posture
- no index replacement
- no public/master mutation

Contribution packs:

- review-required
- no public intake
- no automatic acceptance

Pack sets:

- detect synthetic cross-pack refs when present
- classify dependencies as metadata only
- perform no mutation
