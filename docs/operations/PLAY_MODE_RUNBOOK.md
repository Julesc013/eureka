# PLAY Mode Runbook

PLAY mode makes the Local Appliance feel usable with a tiny deterministic demo
pack while keeping all unsafe lanes disabled.

Recommended layout:

```text
D:\Projects\Eureka\
  eureka\
  instances\
    default\
```

PowerShell setup:

```powershell
cd D:\Projects\Eureka\eureka

$Workspace = "D:\Projects\Eureka"
$Instance = "$Workspace\instances\default"
$Token = "local-dev-token"
```

Validate the pack:

```powershell
python scripts\validate_play_seed_pack.py
```

Dry-run the seed:

```powershell
python scripts\eureka_seed_play_demo.py --instance $Instance --dry-run --json
```

Run the smoke:

```powershell
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --json
```

Run an operator play-session report:

```powershell
python scripts\eureka_play_session.py --instance $Instance --operator-token $Token --json
```

Apply demo state only when you intentionally want to write into the explicit
local instance:

```powershell
python scripts\eureka_seed_play_demo.py --instance $Instance --operator-token $Token --apply --json
```

PLAY mode does not enable source probes, extraction, model/provider calls,
downloads, installs, execution, deployment, production readiness, or public
launch readiness.
