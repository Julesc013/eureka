# Extraction Policy Schema

`contracts/extraction/extraction_policy.v0.json` records disabled-by-default extraction policy.

The schema requires allowed tiers, forbidden actions, sandbox policy, resource limits, privacy policy, rights/risk policy, output policy, mutation policy, and notes.

Runtime extraction, arbitrary path access, arbitrary URL fetch, payload execution, installer execution, package manager invocation, emulator or VM launch, source-cache mutation, evidence-ledger mutation, candidate mutation, and master-index mutation are all false now.
