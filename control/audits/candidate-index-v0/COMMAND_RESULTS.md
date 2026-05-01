# Command Results

P64 candidate-index contract checks passed locally on 2026-05-02:

- `python scripts/validate_candidate_index_record.py --all-examples`
- `python scripts/validate_candidate_index_record.py --all-examples --json`
- `python scripts/validate_candidate_index_contract.py`
- `python scripts/validate_candidate_index_contract.py --json`
- `python scripts/dry_run_candidate_index_record.py --label "Firefox ESR Windows XP compatibility candidate" --candidate-type compatibility_claim_candidate --json`

Regression checks also passed for P59-P63 query-intelligence contracts, hosted
public-search rehearsal, public-search safety evidence, static/public-index
validators, local public-search smoke tests, archive-resolution evals, search
usefulness audit, Python oracle golden checks, unit suites, and architecture
boundaries. The audit JSON records the command-level details.

Optional Cargo verification was unavailable because `cargo` is not installed in
this local environment. No external API calls, deployments, live probes, runtime
candidate writes, source-cache writes, evidence-ledger writes, local-index
writes, public-index writes, or master-index writes were performed.
