# Source Coverage Ledger

The source coverage ledger records bounded coverage statements for known
sources. A coverage record can say which source exists, which connector family
can handle it, which D0-D5 depth is currently represented, how many fixture or
audit records were seen, and which operations remain blocked.

It is not a public index, master index, accepted evidence ledger, or global
coverage claim. H0-BUNDLE-03 coverage records stay in example, fixture, audit,
or local dry-run posture. They do not approve live access, source sync,
downloads, scraping, rights clearance, malware safety, or installability.

Validate with:

```powershell
python scripts/validate_source_os_coverage_scorecards.py
python scripts/record_source_coverage.py --input examples/sources/coverage/internet_archive_coverage_record_v0.json --check
```
