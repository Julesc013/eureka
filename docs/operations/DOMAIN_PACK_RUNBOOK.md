# DOMAIN Pack Runbook

Use the DOMAIN foundation in read-only mode:

```bash
python scripts/eureka_domain_pack.py --manifest examples/domain/domain_seed_manifest.json --validate --json
python scripts/eureka_domain_pack.py --manifest examples/domain/domain_seed_manifest.json --list --json
python scripts/eureka_domain_console.py --domain legacy_software --projection operator_workbench --json
python scripts/validate_domain_packs.py
```

The runbook is intentionally narrow. DOMAIN seed packs are not truth, and they
do not create evidence, reviewed records, source probes, downloads, extraction,
model/provider calls, deployments, public fanout, or index mutations. The
no live source boundary applies to every command here.

When a seed pack changes, rerun the validator and the focused DOMAIN tests.
For larger runtime changes, use the lane router and reserve full discovery for
closeout or promotion.

Unsafe actions remain blocked by policy and by the console projection. Operator
review/promote posture is only a gated hint here; no operator instance is
mutated by these scripts.
