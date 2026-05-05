# Pack Import Runtime Architecture Plan

Future modules only:

```text
runtime/packs/
  validate.py            future runtime wrapper around validators
  quarantine.py          future quarantine manager
  stage.py               future staging manager
  inspect.py             future staged pack inspection adapter
  report.py              future import report builder
  diff.py                future candidate diff builder
  policy.py              future privacy/path/executable/mutation policy guard
  promote.py             future review-gated promotion adapter, disabled in v0
  errors.py              future stable error envelope
  README.md              runtime docs
```

P94 creates no runtime implementation files.

Required future flags:

```text
EUREKA_PACK_IMPORT_RUNTIME_ENABLED=0
EUREKA_PACK_IMPORT_VALIDATE_ONLY=1
EUREKA_PACK_IMPORT_QUARANTINE_ENABLED=0
EUREKA_PACK_IMPORT_PROMOTION_ENABLED=0
EUREKA_PACK_IMPORT_EXECUTE_CONTENTS=0
EUREKA_PACK_IMPORT_FOLLOW_URLS=0
EUREKA_PACK_IMPORT_ALLOW_UPLOADS=0
EUREKA_PACK_IMPORT_MUTATE_SOURCE_CACHE=0
EUREKA_PACK_IMPORT_MUTATE_EVIDENCE_LEDGER=0
EUREKA_PACK_IMPORT_MUTATE_CANDIDATE_INDEX=0
EUREKA_PACK_IMPORT_MUTATE_PUBLIC_INDEX=0
EUREKA_PACK_IMPORT_MUTATE_MASTER_INDEX=0
```
