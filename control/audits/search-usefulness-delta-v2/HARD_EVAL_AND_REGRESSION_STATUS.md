# Hard Eval and Regression Status

Archive resolution eval command:

```text
python scripts/run_archive_resolution_evals.py --json
```

Status:

- task count: 6
- satisfied: 6

Satisfied tasks:

- article_inside_magazine_scan
- driver_inside_support_cd
- latest_firefox_before_xp_drop
- old_blue_ftp_client_xp
- win98_registry_repair
- windows_7_apps

Regression posture:

- No hard eval was weakened.
- Public-search smoke passed.
- Python oracle golden check passed.
- Generated artifact drift checks passed.
- Architecture-boundary checks passed.
- No live source behavior, hosted search, downloads, installers, uploads, local path search, telemetry, or production claims were added.

