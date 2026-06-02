# Public Search UX MVP Runbook

Use this runbook for the example-backed public search UX MVP.

## Build

```bash
python scripts/eureka_public_search_render.py --from-view-model-examples --write-examples --json
```

This writes examples under `examples/public_search_ux/` plus task evidence under `control/inventory/` and `control/audits/public-search-ux-mvp-00-v0/`.

## Smoke

```bash
python scripts/eureka_public_search_ux_smoke.py --from-examples --json
python scripts/eureka_public_search_route_smoke.py --from-examples --json
```

## Validate

```bash
python scripts/validate_public_search_ux_mvp.py
```

Full unittest discovery is not part of this lane.

## Boundaries

Do not write `site/dist`, mutate public indexes, call live sources, fetch files, run OCR, extract files, execute/install software, or claim public launch readiness.
