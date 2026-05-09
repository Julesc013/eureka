# H0 Source OS Integration Audit

The H0 integration audit checks that the three Source OS bundles form a usable
foundation:

- H0-BUNDLE-01 source registry and policy model exists.
- H0-BUNDLE-02 connector interface, replay harness, and live-probe envelope exists.
- H0-BUNDLE-03 coverage ledgers, scorecards, and source packs exist.
- Validators pass without live source access.
- No public/master index mutation or source/evidence/candidate truth acceptance occurred.

Run:

```powershell
python scripts/audit_h0_integration.py --check
```
