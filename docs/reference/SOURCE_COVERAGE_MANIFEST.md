# Source Coverage Manifest

A source coverage manifest rolls up coverage records by source family, trust
lane, index depth, connector family, blocked source count, and unknown source
count. It helps H1 work see which policies and fixtures are missing.

The manifest is local operational evidence only. It must not claim exhaustive
global coverage, accepted source truth, public-index mutation, or master-index
mutation.

Validate with:

```powershell
python scripts/record_source_coverage.py --input examples/sources/coverage/internet_archive_coverage_record_v0.json --check
```
