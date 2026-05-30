# Candidate Index Runbook

Dry-run ingest from the Archive.org example:

```powershell
python scripts/eureka_candidate_ingest.py --from-archive-org-example --query "New York 1993 D-Theater HD demo tape original source" --dry-run --json
```

Search the example candidate index:

```powershell
python scripts/eureka_candidate_search.py --query "D-Theater New York 1993" --from-examples --json
```

Build a review handoff:

```powershell
python scripts/eureka_candidate_review_handoff.py --candidate-id archive_org_dtheater_candidate --from-examples --json
```

These commands do not deploy, mutate public indexes, mutate reviewed indexes,
download files, extract payloads, or call model/provider services.
