# Pack Validator CLI Remediation

P50 recorded that individual source/evidence/index/contribution validators did
not accept the broad-matrix `--all-examples` flag. P51 adds a shared helper:

```text
scripts/pack_validator_examples.py
```

The following validators now accept `--all-examples` and `--known-examples`:

- `scripts/validate_source_pack.py`
- `scripts/validate_evidence_pack.py`
- `scripts/validate_index_pack.py`
- `scripts/validate_contribution_pack.py`
- `scripts/validate_master_index_review_queue.py`
- `scripts/validate_pack_set.py`
- `scripts/validate_only_pack_import.py`

The alias reads only `control/inventory/packs/example_packs.json` and delegates
to the existing per-pack validation functions. It does not scan arbitrary
directories, import packs, stage packs, mutate indexes, upload, call networks,
or accept master-index records.
