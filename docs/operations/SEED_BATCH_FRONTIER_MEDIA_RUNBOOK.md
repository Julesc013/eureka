# Frontier Media Seed Batch Runbook

Run fixture mode:

```powershell
python scripts/eureka_seed_batch_frontier_media.py --fixture --json
```

Refresh public-safe examples:

```powershell
python scripts/eureka_seed_batch_frontier_media.py --fixture --write-examples --json
```

Summarize examples:

```powershell
python scripts/eureka_seed_batch_report.py --from-examples --json
```

Live Archive.org metadata is not part of the normal validation lane. If a later
operator-approved task enables it, use the explicit metadata flag and commit
only redacted summaries, not raw responses.
