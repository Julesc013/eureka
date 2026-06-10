# Next Unblocking Actions

## Immediate

Run the artifact evidence return validator when the compact external return is
available:

```powershell
python scripts/validate_artifact_evidence_return.py --json --strict
```

If the return is valid, resume with:

```text
MANUAL-ARTIFACT-OBSERVATION-BATCH-03
```

## Still Blocked

- Public alpha remains blocked until reviewed artifact record counts and other
  launch gates are satisfied.
- `dev -> main` promotion remains blocked while public-alpha and validation
  gates are blocked.
- Windows 98 driver recommendation remains blocked until the user hardware
  details packet is returned and validated.
- Verified artifact claims remain blocked; source-reference metadata is not a
  verified acquisition or reproducibility path.

