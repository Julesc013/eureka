# Source Coverage Review

Reviewers should check that each coverage record:

- uses an approved current basis: example, fixture, audit, or local dry-run;
- names blocked operations and known gaps;
- avoids exhaustive coverage, rights, malware, and installability claims;
- keeps public-index and master-index mutation false;
- documents the review gate for any future public claim.

Run:

```powershell
python scripts/validate_source_os_coverage_scorecards.py
python scripts/audit_h0_integration.py --check
```
