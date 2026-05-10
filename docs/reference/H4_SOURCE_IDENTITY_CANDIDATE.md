# H4 Source Identity Candidate

Source identity candidates carry host, namespace, repository, URL, Git object, and SWHID hints without accepting truth.

H4-BUNDLE-02 is fixture-runtime work only. It reads committed synthetic or
repo-local fixtures and creates candidate/previews for review. It does not
perform live source calls, API calls, model/provider calls, browser
automation, repository cloning, git command invocation, source archive
downloads, release asset downloads, binary downloads, build tool
invocation, package-manager invocation, installs, execution, scraping,
crawling, source sync, public-index mutation, master-index mutation, or
truth acceptance.

The runtime can produce normalized code/source/release metadata records,
source identity candidates, release identity candidates, source-to-binary
relation candidates, release asset metadata candidates, source-cache
candidate previews, evidence candidate previews, connector output
envelopes, fixture replay results, and summaries.

It cannot produce accepted source identity truth, accepted release truth,
accepted provenance, accepted source truth, accepted evidence truth,
accepted candidate truth, accepted public records, clone/download
permission, authenticity proof, build reproducibility proof, rights
clearance, malware safety, installability, or production readiness.

Validation commands:

- `python scripts/validate_h4_code_source_release_fixture_runtime.py`
- `python scripts/replay_h4_code_source_fixtures.py --check`
- `python scripts/summarize_h4_code_source_fixture_outputs.py --input examples/connectors/h4_code_source_release --check`
