# Portable Local Preview Bundle

This is a local-only source-checkout bundle manifest. It does not publish
Eureka, include secrets, include local instances, or claim production readiness.

## Create

```powershell
python scripts/eureka.py bundle create --out ..\instances\eureka-bundle
```

## Verify

```powershell
python scripts/eureka.py bundle verify ..\instances\eureka-bundle
```

## Rehearse

```powershell
python scripts/eureka.py bundle rehearse ..\instances\eureka-bundle --target ..\instances\eureka-bundle-rehearsal
```

The rehearsal bootstraps an empty local instance, runs doctor, verifies route
registration, creates and verifies a backup, and restores that backup to a fresh
target. It performs no provider calls and no public exposure.

## Launch Helpers

The generated bundle includes:

```text
launch.ps1
launch.sh
```

Both helpers call the same `python scripts/eureka.py` command surface from a
source checkout. Pass an explicit instance path. Configure provider keys only in
your local shell environment, never in the bundle.

## Boundaries

The bundle excludes:

```text
API keys
local instances
private indexes
raw observations
provider result payloads
AIDE local state
public deployment state
```

