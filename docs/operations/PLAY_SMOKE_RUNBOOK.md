# PLAY Smoke Runbook

PLAY-02 is the compact smoke lane for the deterministic local demo pack. Run it
before SYN, IA, F0, workbench changes, and source-pilot work when you need a
quick proof that the local appliance is still usable.

PowerShell setup:

```powershell
cd D:\Projects\Eureka\eureka

$Instance = "..\instances\default"
$Token = "local-dev-token"
```

Recommended smoke with an isolated temporary instance:

```powershell
python scripts\eureka_play_smoke.py --use-temp-instance --apply-demo-to-temp --operator-token $Token --json
```

This initializes a temporary explicit instance, applies the committed demo pack
there, runs the known query and Hunt checks, and then lets the temp directory be
removed by the OS. It does not mutate `..\instances\default`.

Read-only smoke against the preferred local instance path:

```powershell
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --dry-run --json
```

Dry-run smoke resolves the instance path, validates the committed demo fixtures,
and checks the demo matrix without writing instance state.

Optional localhost server route check:

```powershell
python scripts\eureka_local_server.py --instance $Instance --host 127.0.0.1 --port 8765 --operator-token $Token
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --base-url http://127.0.0.1:8765 --expect-server --json
```

Route checks are limited to localhost workbench/API routes. They cover `/`,
`/status`, `/search`, `/absence`, `/hunts`, and the matching read-only
`/api/v1/...` routes.

The smoke matrix proves:

- `sampleproject` returns the committed demo hit.
- `definitely-not-present-play-00` returns local demo-corpus absence only.
- the D-Theater query is an unresolved media SearchNeed.
- the StyleWriter query is an unresolved source/extraction SearchNeed with
  blocked source and extraction WorkUnits.
- the DirectX SDK query is a source-routing SearchNeed with policy caution.
- the Firefox XP query is a compatibility SearchNeed, not final truth.
- source-probe, extraction, and model-provider paths remain blocked.

PLAY smoke is not production readiness, public launch readiness, live-source
readiness, extraction readiness, or AI readiness.
