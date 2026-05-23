# AIDE Generated Policy Review v1

## Summary

This closeout classifies tracked AIDE and audit-generated material as control-plane evidence or generated inventory. It does not make AIDE output product truth.

## Observed Footprint

- Tracked `.aide/` files: `1990`
- Tracked `control/audits/**/generated` files: `1314`
- Tracked `site/dist/` files: `58`
- Tracked `tmp/` files: `0`

## Policy

- `.aide/export/` is artifact-only and not active source.
- `.aide/reports/`, `.aide/repo/`, `.aide/roots/`, and `.aide/tools/` are evidence or generated inventory, not product authority.
- `.aide/cache/` is local/cache material unless explicitly justified by policy.
- `control/audits/**/generated/` is retained audit evidence only.
- `site/dist/` remains a committed generated public artifact and is not source truth.

## Non-Claims

- No production-readiness claim is made.
- No product behavior, source connector behavior, public search behavior, or live-source behavior is intentionally changed.
- No AIDE material defines runtime semantics.
