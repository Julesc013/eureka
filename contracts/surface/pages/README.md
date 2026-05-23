# Page Contracts

This directory holds governed public page contracts for Eureka. P79 added `object_page.v0.json` and `object_page_section.v0.json`. P80 added `source_page.v0.json` and `source_page_section.v0.json`. P81 adds `comparison_page.v0.json` and `comparison_page_section.v0.json`.

Object Page Contract v0 is evidence-first. It does not implement runtime object pages, a persistent object-page store, downloads, installs, execution, live source fanout, candidate promotion, or index/cache/ledger mutation.

Source Page Contract v0 is evidence-first and contract-only. It does not implement runtime source pages, connector runtime, source sync execution, live source calls, downloads, mirrors, installs, execution, source trust authority, or index/cache/ledger/candidate/master-index mutation.

Comparison Page Contract v0 is evidence-first and contract-only. It does not implement runtime comparison pages, ranking authority, candidate promotion, winner selection without evidence, live source calls, downloads, installs, execution, source trust authority, or index/cache/ledger/candidate/master-index mutation.
