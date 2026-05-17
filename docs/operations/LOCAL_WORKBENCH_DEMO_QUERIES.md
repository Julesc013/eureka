# Local Workbench Demo Queries

Use these queries to exercise the local play loop after validating the demo
pack.

```powershell
$Workspace = "D:\Projects\Eureka"
$Instance = "$Workspace\instances\default"
$Token = "local-dev-token"

python scripts\validate_play_seed_pack.py
python scripts\eureka_seed_play_demo.py --instance $Instance --dry-run --json
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --json
```

Known reviewed hit:

```text
sampleproject
```

Expected result: a committed demo-local reviewed result,
`play.reviewed.sampleproject.v0`.

Known local absence:

```text
definitely-not-present-play-00
```

Expected result: local demo-corpus absence only. This does not prove global
nonexistence.

Unresolved demo SearchNeeds:

```text
New York 1993 D-Theater HD demo tape original source
StyleWriter 2500 Mac OS 8 driver
DirectX SDK June 2010 offline installer
last Firefox for Windows XP
Windows 7 compatible old app
```

Expected result: SearchNeed and WorkUnit demand state, not verified records.
Source, extraction, and model-provider future actions remain blocked by policy.
