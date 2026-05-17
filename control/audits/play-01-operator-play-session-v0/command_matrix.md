# Command Matrix

The governed command matrix is stored at
`control/inventory/play_session_command_matrix.json`.

Key operator commands:

```powershell
$Instance = "..\instances\default"
$Token = "local-dev-token"

python scripts\validate_play_session.py
python scripts\eureka_play_session.py --instance $Instance --operator-token $Token --dry-run --json
python scripts\eureka_play_smoke.py --instance $Instance --operator-token $Token --json
```

Apply mode is explicit:

```powershell
python scripts\eureka_play_session.py --instance $Instance --operator-token $Token --apply --json
```

The apply command writes only demo state into the explicit local instance and
does not run WorkUnits.
