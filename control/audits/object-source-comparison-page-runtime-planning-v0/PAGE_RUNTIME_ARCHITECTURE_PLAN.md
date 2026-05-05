# Page Runtime Architecture Plan

Future modules only:

```text
runtime/pages/
  object_page.py          future object page assembler
  source_page.py          future source page assembler
  comparison_page.py      future comparison page assembler
  identifiers.py          future safe ID/slug resolver
  render.py               future HTML/text/JSON rendering helpers
  policy.py               future privacy/action/source policy guard
  errors.py               future stable error envelope
  README.md               runtime docs

runtime/gateway/public_api/pages.py  future API route adapter
```

P93 does not create these runtime files.

Future dependencies:

- public index reader
- public search result card contract
- object/source/comparison page contracts
- source/evidence/candidate policy guards
- stable route/error envelope
- static/lite/text fallback renderer
- operator kill switch for hosted runtime

Required future env flags:

- EUREKA_PAGE_RUNTIME_ENABLED=0
- EUREKA_OBJECT_PAGE_RUNTIME_ENABLED=0
- EUREKA_SOURCE_PAGE_RUNTIME_ENABLED=0
- EUREKA_COMPARISON_PAGE_RUNTIME_ENABLED=0
- EUREKA_PAGE_RUNTIME_SOURCE=public_index_only
- EUREKA_PAGE_RUNTIME_LIVE_SOURCE_CALLS=0
- EUREKA_PAGE_RUNTIME_DOWNLOADS=0
- EUREKA_PAGE_RUNTIME_INSTALLS=0
- EUREKA_PAGE_RUNTIME_EXECUTION=0
- EUREKA_PAGE_RUNTIME_TELEMETRY=0
