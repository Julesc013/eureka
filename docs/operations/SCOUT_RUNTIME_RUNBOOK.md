# SCOUT Runtime Runbook

Run a full local example SCOUT packet:

```powershell
python scripts/eureka_scout_runtime.py --from-candidate-examples --seed archive_org_dtheater_candidate --json
```

Inspect just the trail, relations, or source trust observation:

```powershell
python scripts/eureka_scout_trails.py --from-candidate-examples --seed archive_org_dtheater_candidate --json
python scripts/eureka_scout_relations.py --from-candidate-examples --seed archive_org_dtheater_candidate --json
python scripts/eureka_scout_source_trust.py --from-candidate-examples --json
```

All commands are local/example-only. They do not call sources, crawl, download,
extract, use models, mutate indexes, deploy, or create accepted truth.
