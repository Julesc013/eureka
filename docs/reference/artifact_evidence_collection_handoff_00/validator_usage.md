# Artifact Evidence Return Validator Usage

Use this validator before treating an external/manual return as reviewable
input. It checks the compact summary shape and preserves truth boundaries.

## Default Contract Path

```text
../eureka-evidence-runs/artifact_evidence_collection_00/artifact_evidence_collection_summary.json
```

## Commands

Validate the default return path:

```powershell
python scripts/validate_artifact_evidence_return.py
```

Validate a specific file:

```powershell
python scripts/validate_artifact_evidence_return.py --return-file <path>
```

Emit JSON:

```powershell
python scripts/validate_artifact_evidence_return.py --return-file <path> --json
```

Strict mode requires at least one target result:

```powershell
python scripts/validate_artifact_evidence_return.py --return-file <path> --strict
```

## What It Rejects

- missing required return-contract fields
- invalid target status values
- duplicate target ids
- reviewed artifact or verified artifact truth claims
- download, executable fetch, install, rights-clearance, or malware-safety
  claims
- private absolute local evidence paths or secret-like fields
- Windows 98 driver items that are not blocked/deferred and lack hardware
  identity fields

## Boundary

Passing validation does not create reviewed artifact records, verified
artifacts, public index mutations, download safety, rights clearance, public
alpha readiness, or `dev -> main` readiness.
