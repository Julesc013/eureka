# Portable Eureka Instance v0

Task: `PORTABLE-EUREKA-INSTANCE-00`

Status: implemented locally, focused validation pending final guardrails.

This audit packet records the portable local command surface:

```text
python scripts/eureka.py bootstrap
python scripts/eureka.py doctor
python scripts/eureka.py test
python scripts/eureka.py serve --mode exploration
python scripts/eureka.py hunt "<query>"
python scripts/eureka.py replay <run-id>
python scripts/eureka.py status
```

The implementation wraps existing local instance, E2E runner, Preview Index, exploration router, replay, and oracle modules. It creates no reviewed IA truth, no public exposure, and no provider/network calls beyond loopback smoke checks.

Next recommended task: `HUMAN-END-TO-END-ACCEPTANCE-00`.
