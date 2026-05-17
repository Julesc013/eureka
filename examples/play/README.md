# Local Workbench Play Demo Pack

This directory contains deterministic demo data for the local workbench play
loop. It is committed source fixture data, not operator runtime state.

The pack demonstrates:

- a known reviewed/demo-local hit for `sampleproject`
- a known local absence for `definitely-not-present-play-00`
- demo Hunts for unresolved local investigations
- SearchNeed seeds for media, driver/source, offline installer, and
  compatibility questions
- WorkUnit seeds whose source, extraction, and model-provider paths are blocked
  by policy

Boundaries:

- no live source calls
- no source probe execution
- no extraction execution
- no model/provider calls
- no downloads, installs, or execution
- no production or public launch readiness claim

Use from the repo root:

```powershell
$Instance = "..\instances\default"
$Token = "local-dev-token"

python scripts\validate_play_seed_pack.py
python scripts\eureka_seed_play_demo.py --instance $Instance --dry-run --json
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --json
```

To load the demo into an initialized local instance, use `--apply` explicitly.
The script never moves, deletes, or creates operator instance roots by default.
