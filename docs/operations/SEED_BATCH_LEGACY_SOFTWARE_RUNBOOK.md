# Legacy Software Seed Batch Runbook

Run fixture mode:

```powershell
python scripts/eureka_seed_batch_legacy_software.py --fixture --json
```

Refresh public-safe examples:

```powershell
python scripts/eureka_seed_batch_legacy_software.py --fixture --write-examples --json
```

Summarize examples:

```powershell
python scripts/eureka_seed_batch_report.py --from-examples --domain legacy_software --json
```

The metadata pilot descriptor is dry-run only unless a future reviewed task
explicitly approves a bounded live metadata run. Do not commit raw live
responses, download packages, install software, execute binaries, or present a
malware-clean claim.
