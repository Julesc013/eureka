# Local Foundry Reset And Export

Local foundry state must be resettable, deletable, and export-gated.

## Reset And Delete

Future local state roots must define operator-controlled reset and delete
behavior. A reset removes local/private draft state. A delete removes the local
state root when the operator chooses to discard it. This milestone creates no
state that requires deletion.

## Retention

Default retention is operator-controlled for future private state. Committed
audit reports may be retained as review evidence. Private caches remain local
and must not be committed.

## Export

Export modes include no export, audit report export, future pack draft export,
future contribution/source/evidence/index pack export, future snapshot export,
and future review-required export.

Every public export requires review. Automatic public export, automatic
master-index import, and automatic evidence acceptance are forbidden.

## Stop Conditions

Stop rather than export when the state contains private data, credentials,
account material, uncertain rights posture, executable payloads, unreviewed
evidence, source-policy uncertainty, or any master-index mutation request.

## Validation

Run:

```powershell
python scripts/validate_local_foundry_state.py
```
