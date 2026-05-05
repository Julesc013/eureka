# Validation Pipeline Implementation

The dry-run may call existing repo-local validators only in bounded mode:

- source packs use `scripts/validate_source_pack.py`
- evidence packs use `scripts/validate_evidence_pack.py`
- index packs use `scripts/validate_index_pack.py`
- contribution packs use `scripts/validate_contribution_pack.py`

Validators run only for approved examples and use Python subprocess execution
without `shell=True`. Output is captured as bounded status. Validation is
structural and does not accept pack claims as truth. Validator failures do not
mutate anything. If validator CLI drift occurs, non-strict mode records warning
or invalid status; strict mode fails on invalid packs or validator errors.

Synthetic P104 `PACK_IMPORT_DRY_RUN_INPUT.json` examples are classified without
running the pack validators because they are not real source/evidence/index or
contribution pack manifests.
