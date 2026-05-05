# Runtime Planning Status

All first-wave runtime planning packs exist. They are planning-only artifacts.

- Internet Archive metadata runtime planning: present.
- Wayback/CDX/Memento runtime planning: present.
- GitHub Releases runtime planning: present.
- PyPI metadata runtime planning: present.
- npm metadata runtime planning: present.
- Software Heritage runtime planning: present.

Each runtime plan records `blocked_connector_approval_pending` or equivalent
approval-gated readiness. The plans document implementation phases and
do-not-implement-yet boundaries, but they do not implement connector runtime.

For every connector:

- `runtime_connector_implemented`: false in runtime planning reports.
- `live_calls_enabled`: false.
- `public_search_live_fanout_enabled`: false.
- Source-cache and evidence-ledger authoritative writes remain disabled.

The existing `runtime/connectors/github_releases/` adapter is a recorded fixture
adapter for deterministic local tests. It is not approval for live GitHub API
access and is not public-search fanout.
