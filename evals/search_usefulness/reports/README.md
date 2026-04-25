# Search Usefulness Reports

Generated Search Usefulness Audit reports are written to stdout by default.
Use `--output <path>` when an operator wants a local JSON report:

```bash
python scripts/run_search_usefulness_audit.py --json --output tmp/search-usefulness-report.json
```

Reports are not committed by default because timestamps and local audit focus
can vary. Stable future baselines may be committed only when deliberately
accepted as repo evidence.
