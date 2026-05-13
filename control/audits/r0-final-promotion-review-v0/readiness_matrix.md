# Readiness Matrix

Promotion readiness: ready with warning-level debt.

Required checks:

- Current branch is `dev`: pass.
- `dev` is synced to `origin/dev`: pass for reviewed baseline.
- `origin/main` is contained in `origin/dev`: pass.
- R0 final closeout: pass with warnings.
- Runtime seams: pass.
- Contract taxonomy remediation: pass.
- Generated artifact drift remediation: pass.
- Legacy runtime leakage remediation: pass with warnings.
- Full unittest discovery: pass.
- Generated artifact cleanliness: pass.
- Architecture boundary checks: pass.
- R0 validators: pass.
- Forbidden claim scan over current R0/final-promotion evidence: pass.

Overall decision: `promotion_plan_only` because no explicit apply was requested.
