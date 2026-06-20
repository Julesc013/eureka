# Compatibility Report

Existing specialized commands remain available:

- `eureka_init_instance.py`
- `eureka_validate_instance.py`
- `eureka_instance_status.py`
- `eureka_search.py`
- `eureka_index.py`
- `eureka_resolution_run.py`
- `eureka_e2e_eval.py`
- `eureka_synthetic_truth_path.py`
- `run_eureka_local.py`

`scripts/eureka.py` is the preferred coherent entrypoint. It does not deprecate the specialized commands.
