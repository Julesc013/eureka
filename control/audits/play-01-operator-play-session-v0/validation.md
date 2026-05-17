# Validation

PLAY-01 validation commands:

```powershell
python scripts\validate_play_seed_pack.py
python scripts\validate_play_session.py
python scripts\eureka_play_session.py --instance ..\instances\default --operator-token local-dev-token --dry-run --json
python scripts\eureka_play_smoke.py --instance ..\instances\default --operator-token local-dev-token --json
python -m unittest tests.runtime.test_play_seed_pack
python -m unittest tests.operations.test_play_session
python -m unittest tests.operations.test_play_session_report
python -m unittest tests.operations.test_play_smoke
```

Final command results are captured in the task final report.
