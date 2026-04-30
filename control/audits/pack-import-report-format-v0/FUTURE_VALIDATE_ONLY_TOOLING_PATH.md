# Future Validate-Only Tooling Path

The next milestone should be Validate-Only Pack Import Tool v0.

That future tool may:

1. accept one explicit pack root or known example set
2. call `scripts/validate_pack_set.py` or individual validators
3. optionally call `scripts/validate_ai_output.py` for typed AI output bundles
4. emit `pack_import_report.v0`

It still must not stage packs, mutate local indexes, upload, submit, or mutate
the hosted/master index.
