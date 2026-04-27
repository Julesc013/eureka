# Batch 0 Manual Observation Instructions

Use these steps for one query/system slot at a time.

Optional local helpers:

```bash
python scripts/list_external_baseline_observations.py --batch batch_0 --status pending_manual_observation
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id <query_id> --system-id <system_id> --output <path>
python scripts/validate_external_baseline_observations.py --file <path>
```

The helpers only list slots, create pending fillable JSON, and validate files.
They do not search Google, search Internet Archive, open browsers, fetch URLs,
or collect results.

1. Pick one query ID from `batch_manifest.json`.
2. Open the relevant external system manually.
3. Submit the exact query text from the search-usefulness query corpus.
4. Record date/time, operator, browser/tool, filters, and scope.
5. Copy only short visible summaries or snippets, not entire pages.
6. Record top visible results manually.
7. Identify the first useful result rank, or leave it absent with an explicit
   reason.
8. Score usefulness dimensions from 0 to 3:
   - 0 absent or misleading
   - 1 weak or high manual work
   - 2 useful but incomplete
   - 3 strong or low detective work
9. Record failure modes and notes.
10. Keep the slot pending if it was not observed.
11. Do not automate result collection and do not scrape.
12. Do not treat one observation as global Google or Internet Archive truth.
13. For Google, do not count sponsored or ad results as organic unless they are
    explicitly labeled in the notes.
14. Distinguish a parent collection or parent item from the smallest actionable
    unit.
15. For Internet Archive full text, record whether the hit is article/page-level
    or only a parent scan.

Do not use this batch to claim Eureka beats Google or Internet Archive
globally. The goal is auditable comparison evidence, not production benchmark
claims.
