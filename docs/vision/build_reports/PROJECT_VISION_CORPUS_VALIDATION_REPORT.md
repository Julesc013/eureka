# Project Vision Corpus Validation Report

## Result

`PASS_WITH_WARNINGS`

Warnings are limited to unavailable live-repo validation.

## Checks

| Check | Result |
|---|---|
| all zips accounted for | PASS |
| raw zips copied but not modified | PASS |
| human-readable sources selected | PASS |
| source blocks generated | PASS |
| duplicates reported | PASS |
| themes generated | PASS |
| synthesis documents generated | PASS |
| contradictions preserved | PASS |
| current truth vs advisory vision labelled | PASS |
| no live repo/canon/contract/schema/code/queue files modified | PASS |
| no archive claim promoted | PASS |
| no evidence-card IDs exposed in main synthesis prose | PASS |
| no machine manifests dumped into vision documents | PASS |
| no boilerplate repeated across every section | PASS |

## Repo checks

- `git diff --check`: not run; no repo was provided.
- AIDE doctor/validate: not run; no repo/AIDE queue was provided.
- Existing corpus validators: not run; none were provided in the uploaded files.

## Protected paths

No live `docs/canon`, `docs/architecture`, `contracts`, `schema`, implementation roots, release roots, or `.aide/queue/current.toml` paths were present or modified. All outputs are under `/mnt/data/project_vision_corpus/`.
