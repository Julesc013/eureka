# PLAY Session Runbook

PLAY session mode is the repeatable operator loop for the local demo corpus.
It proves that the local appliance can be used like a small product surface
without enabling live sources, extraction, model/provider calls, downloads, or
deployment.

Recommended local layout:

```text
D:\Projects\Eureka\
  eureka\
  instances\
    default\
```

PowerShell setup:

```powershell
cd D:\Projects\Eureka\eureka

$Instance = "..\instances\default"
$Token = "local-dev-token"
```

Run a safe dry-run session:

```powershell
python scripts\eureka_play_session.py --instance $Instance --operator-token $Token --dry-run --json
```

Dry-run mode validates the PLAY seed pack, resolves the explicit instance path,
checks the deterministic demo queries from committed examples, inspects demo
Hunts, SearchNeeds, and WorkUnits, and emits a structured report. It does not
write instance state.

Apply demo state only when the target instance is explicit and intentional:

```powershell
python scripts\eureka_seed_play_demo.py --instance $Instance --operator-token $Token --apply --json
python scripts\eureka_play_session.py --instance $Instance --operator-token $Token --apply --json
```

Apply mode writes only the committed PLAY demo state to the explicit local
instance. It does not run source probes, extraction, model/provider calls,
downloads, installs, WorkUnits, source sync, deployment, or public launch
behavior.

Optional localhost workbench check:

```powershell
python scripts\eureka_local_server.py --instance $Instance --host 127.0.0.1 --port 8765 --operator-token $Token
python scripts\eureka_play_session.py --instance $Instance --operator-token $Token --base-url http://127.0.0.1:8765 --expect-server --json
```

Server checks are restricted to localhost URLs and are skipped unless
`--base-url` is supplied.

Run the smoke:

```powershell
python scripts\eureka_play_smoke.py --use-temp-instance --apply-demo-to-temp --operator-token $Token --json
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --dry-run --json
```

The temp-instance smoke proves explicit apply behavior without touching the
operator instance. The `..\instances\default` smoke is read-only and proves the
same query/absence/Hunt matrix without writing instance state.

PLAY differs from later tracks:

- PLAY is deterministic local demonstration state.
- SYN is future evaluation/query pressure.
- IA is future connector approval closure and must not imply live calls.
- F0 is future extraction work and remains disabled here.
- Production/public launch readiness is not claimed by PLAY.
