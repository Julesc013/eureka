# Query Matrix

PLAY-02 smoke covers six deterministic demo queries:

| Query ID | Query | Expected State |
| --- | --- | --- |
| known_hit | sampleproject | reviewed fixture-backed hit |
| known_absence | definitely-not-present-play-00 | known local demo-corpus absence |
| media_search_need | New York 1993 D-Theater HD demo tape original source | unresolved media SearchNeed |
| extraction_search_need | StyleWriter 2500 Mac OS 8 driver | unresolved SearchNeed with blocked source/extraction work |
| hard_source_routing | DirectX SDK June 2010 offline installer | hard source-routing SearchNeed |
| compatibility | last Firefox for Windows XP | compatibility SearchNeed, not final truth |

The matrix forbids fake evidence, fake verified records, live source calls,
source-probe execution, extraction, model/provider calls, downloads, installs,
execution, deployment, and production/public-launch claims.
