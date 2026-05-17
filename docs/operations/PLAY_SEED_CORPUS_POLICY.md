# PLAY Seed Corpus Policy

PLAY-00 adds a deterministic local demo pack. The pack is committed fixture
data under `examples/play/`; it is not runtime state and it is not a public
index export.

Allowed demo state:

- reviewed demo records that are fixture-backed or demo-local
- local absence records scoped to the demo corpus
- SearchNeed records for unresolved operator demand
- WorkUnit records that are queued or blocked by policy
- provisional candidates that clearly remain unresolved

Forbidden demo state:

- fake evidence
- fake verified records for unresolved needs
- fake hashes
- fake rights or malware-safety claims
- live source observations
- source probe, extraction, model/provider, download, install, execution, or
  deployment side effects

The seed script defaults to dry-run:

```powershell
$Instance = "..\instances\default"
python scripts\eureka_seed_play_demo.py --instance $Instance --dry-run --json
```

Only an explicit apply command may write to an initialized local instance:

```powershell
$Instance = "..\instances\default"
$Token = "local-dev-token"
python scripts\eureka_seed_play_demo.py --instance $Instance --operator-token $Token --apply --json
```

The apply path writes only inside the explicit instance root. It does not move,
copy, or delete operator instance directories.
