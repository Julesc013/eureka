# Local Rehearsal Results

Initial P54 local rehearsal:

```text
python scripts/run_hosted_public_search.py --check-config
status: valid

python scripts/check_hosted_public_search_wrapper.py
status: passed
checks: 14/14
```

The rehearsal checked `/healthz`, `/status`, `/api/v1/status`,
`/api/v1/search`, `/api/v1/query-plan`, `/api/v1/sources`, `/search`, and
blocked `index_path`, `url`, `live_probe`, `download`, `upload`, and a 161
character query.
