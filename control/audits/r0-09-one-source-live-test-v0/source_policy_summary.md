# Source Policy Summary

- source_id: `pypi_json_metadata`
- package: `sampleproject`
- operation: `metadata_only`
- endpoint: `https://pypi.org/pypi/sampleproject/json`
- max live requests per run: 1
- live default: disabled
- live enablement: explicit `--live`
- package downloads: disabled
- install/execution: disabled
- source sync: disabled
- site/dist writes: disabled
- master index writes: disabled

The policy requires a User-Agent with contact posture and permits only the PyPI JSON metadata endpoint for the selected package.
