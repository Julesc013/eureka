# Baseline Audit Counts

Baseline command:

```text
python scripts/run_search_usefulness_audit.py --json
```

Baseline status counts before Source Expansion v2:

| Status | Count |
| --- | ---: |
| covered | 5 |
| partial | 22 |
| source_gap | 26 |
| capability_gap | 9 |
| unknown | 2 |

Archive resolution eval baseline:

```text
python scripts/run_archive_resolution_evals.py --json
```

The archive eval suite remained satisfied with 6 satisfied tasks before the fixture expansion.

