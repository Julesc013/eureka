# Public Search View Models

Canonical public search view models:

- `SearchPageViewModel`
- `ResultCardViewModel`
- `ObjectPageViewModel`
- `CandidatePageViewModel`
- `NeedPageViewModel`
- `SourcePageViewModel`
- `EvidencePageViewModel`
- `NoResultsNeedViewModel`
- `SearchCoverageViewModel`
- `ActionPostureViewModel`
- `CapabilityProfileViewModel`

Supported projection profiles:

- `public_web`
- `operator_workbench`
- `api_json`
- `classic_html`
- `text`

Agents should consume JSON packets such as `api_json` projections rather than
scraping HTML.
