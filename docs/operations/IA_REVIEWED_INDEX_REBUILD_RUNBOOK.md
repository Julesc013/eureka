# IA Reviewed Local Index Rebuild Runbook

IA-07 rebuilds Internet Archive reviewed local records from promotion previews in
an explicit temporary/local instance only.

## Scope

- Input: IA promotion previews from fixture and live-preview metadata paths.
- Output: reviewed local records, search results, object packets, absence
  packets, and boundary reports.
- Default mode: dry-run.
- Apply mode: requires `--apply`, `--instance`, and `--operator-token`.

## Commands

Dry-run:

```powershell
python scripts/eureka_ia_reviewed_index_rebuild.py --from-promotion-previews --dry-run --json
```

Apply proof in a temporary explicit instance:

```powershell
python scripts/eureka_ia_reviewed_index_rebuild.py --instance <temp-instance> --operator-token local-dev-token --from-promotion-previews --apply --search-query sampleproject --absence-query definitely-not-present-ia-07 --json
```

## Boundaries

- Reviewed local index records are not master records.
- The command must not mutate `site/dist/data/public_index`.
- The command must not mutate the operator instance by default.
- No raw IA response bodies, downloads, uploads, extraction, model/provider
  calls, deployment, production-readiness claim, or public-launch claim are
  allowed.

IA-PILOT-CLOSEOUT-01 may summarize the pilot after IA-07 validation, but IA-07
does not start closeout.
