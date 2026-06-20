# Rollback Report

Rollback changes only the Preview Index `current.json` pointer to a selected
existing generation. It does not mutate generation content, reviewed records,
review ledgers, reviewed/master indexes, public indexes, or snapshots.

Command:

```powershell
python scripts/eureka_index.py preview-rollback --to <generation-id> --json
```
