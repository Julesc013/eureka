# Query Observation Contract v0

P59 defines Eureka's first Query Intelligence Plane contract: a privacy-filtered
query observation record for future public-search learning.

This pack is contract/schema/example/validator work only. It does not implement
persistent query logging, telemetry, shared query/result cache, miss ledger,
search need records, probe queue, candidate index, public aggregate publishing,
runtime index mutation, local index mutation, or master-index mutation.

Required validation:

```bash
python scripts/validate_query_observation.py --all-examples
python scripts/validate_query_observation.py --all-examples --json
python scripts/validate_query_observation_contract.py
python scripts/validate_query_observation_contract.py --json
```
