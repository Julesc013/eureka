# R0 Source Observation Seam

R0-04 adds a standard-library-only runtime seam under `runtime/source_observation/`.

## Run The Demo

```bash
python scripts/demo_source_observation_seam.py --json
```

To write the sample audit output:

```bash
python scripts/demo_source_observation_seam.py --output control/audits/r0-04-source-observation-production-seam-v0/generated/sample_demo_output.json --json
```

The demo builds a synthetic source record, policy decision, metadata request, metadata response, source observation, normalized observation, evidence candidate, and review item.

## Run The Validator

```bash
python scripts/validate_source_observation_seam.py
```

The validator checks:

- product contracts are present and JSON-valid
- `runtime/source_observation/` has no forbidden control vocabulary
- the runtime package does not import network or provider modules
- the demo output keeps evidence and review in candidate states
- durable writes and public index writes remain disabled

R0-04 also updates the contract taxonomy scanner so `contracts/runtime/evidence_candidate.v0.json` is recognized as a product runtime contract. Without that narrow compatibility update, the older R0-03A candidate-name heuristic treats any filename containing `candidate` as a preview schema.

## Interpretation

`PASS_WITH_WARNINGS` is expected while R0-03B-2 still records contract taxonomy debt. That warning does not change R0-04 behavior; it means the recovery branch still needs contract cleanup before promotion.

## Why F0 Remains Blocked

F0 depends on a real source observation, evidence, review, and index loop. R0-04 only creates the first clean runtime seam. It does not create a durable source cache, evidence ledger, review queue, or public index rebuild.

## Next Task

R0-05 should build the durable source cache store over the R0-04 seam.
