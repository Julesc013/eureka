# Candidate Store Review

Candidate review decides what should happen to provisional discoveries. The
Candidate Store runtime only records and summarizes candidates; it does not
accept them.

## Review Gates

Review is required before:

- public use
- evidence acceptance
- master-index mutation
- pack export
- source policy approval
- rights or risk decisions

Allowed future review decisions include accept after review, reject, defer,
mark duplicate possible, request more evidence, block by policy, block by
rights, or block by risk.

Forbidden outcomes include automatic public use, automatic evidence acceptance,
automatic master-index mutation, rights-clearance claims, malware-safety
claims, verified-installability claims, exhaustive-search claims, and
production-readiness claims.

## Review Procedure

1. Validate candidate records.
2. Inspect status, type, origin, and related refs.
3. Preserve duplicate and conflict context.
4. Require evidence review before any evidence use.
5. Require master-index review before any future index mutation.
6. Keep policy-blocked candidates blocked until policy changes are reviewed.

## Validation Commands

```bash
python scripts/record_candidate.py --input examples/search/needs/software_version_search_need_v0.json --check
python scripts/summarize_candidate_store.py --input examples/index/candidates --check
python scripts/validate_candidate_store_runtime.py
```

