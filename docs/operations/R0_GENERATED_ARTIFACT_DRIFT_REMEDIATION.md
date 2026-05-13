# R0 Generated Artifact Drift Remediation

R0 closeout remained partial because full unittest discovery exposed generated artifact drift. The reproduced drift affected the public search index, static site output, and demand dashboard checksum fixtures. The static site JSON test also wrote to the default `site/dist` output path, which made discovery order sensitive.

## Repairs

- Hardened `tests/scripts/test_static_site_generator.py` so the JSON build test writes to a temporary output directory.
- Refreshed the local public search index through its owning builder.
- Refreshed canonical `site/dist` through the static site generator and validated compatibility surfaces.
- Refreshed demand dashboard example checksum manifests.
- Added generated artifact policy, site/dist test isolation policy, drift audit, repair reporting, cleanliness check, validator, focused tests, and audit evidence.

## Validation Boundary

This remediation does not implement F0, deploy the site, mutate a hosted public index, mutate a master index, or claim production/public launch readiness.

F0 may resume only after the full validation lane confirms that generated artifact drift no longer blocks R0 closeout. Dev-to-main promotion remains a separate operator action and is not automatic.
