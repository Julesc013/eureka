# Validation

Validation was run before promotion:

- IA validators from IA-00 through IA-07.
- IA pilot closeout validator.
- repo layout canon validator and focused tests.
- architecture boundary check.
- generated artifact cleanliness check.
- AIDE doctor, validate, test, selftest, verify, review-pack, and commit check.
- full unittest discovery.

Result:

- IA validators: pass.
- Repo layout canon validator and focused tests: pass.
- Architecture boundaries: pass.
- AIDE doctor/validate/test/selftest/verify/review-pack: pass.
- Full unittest discovery: fail, blocking promotion.
- Blocked audit evidence was committed and pushed to `dev`; `main` was not
  pushed or fast-forwarded.

Full discovery failed with `17` failures and `5` errors. Blocking groups:

- candidate-index contract and record validators: missing
  `examples/candidate_index/internet_archive_metadata/CANDIDATE_INDEX_RECORD.json`.
- contract taxonomy plan: new `contracts/repo/*.contract.toml` files are not
  classified in `control/inventory/contract_taxonomy_inventory.json`.
- runtime/source-observation leakage: unallowlisted production-path vocabulary
  and network dependency findings in IA source-observation modules.
- HUNT/LOCAL promotion-state tests: current queue and prior promotion state no
  longer satisfy their expected SYN/main-promoted posture.

Generated artifact cleanliness reports uncommitted audit drift while this review
evidence is unstaged. It must be rerun after any evidence commit if this blocked
audit is preserved on `dev`.
