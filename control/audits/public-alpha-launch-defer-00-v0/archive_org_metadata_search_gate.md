# Archive.org Metadata Search Gate

Archive.org-wide search is now a required pre-public-alpha capability.

The gate is metadata-only:

- allowed future source surfaces:
  - `https://archive.org/advancedsearch.php`
  - `https://archive.org/services/search/v1/scrape`
  - `https://archive.org/metadata/{identifier}`
- required output:
  - candidate records
  - source-cache summaries
  - review queue items
- forbidden output:
  - automatic reviewed truth
  - public/master index mutation before review
  - raw unredacted live response commits
  - downloads or file fetches
  - extraction or execution

This gate uses Internet Archive search and metadata APIs as source-lead
surfaces. It does not claim that Eureka mirrors all of Archive.org, owns
Archive.org truth, or can guarantee immutable exhaustive results from a changing
external corpus.
