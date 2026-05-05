# Package Identity Review And Normalization Plan

Allowed future package-name sources:

- reviewed source record
- reviewed search need
- source pack record
- manual observation record
- fixture example

Forbidden package-name sources:

- raw public query parameter
- private package
- credentialed package index
- alternate package index unless explicitly approved later
- localhost URL
- file URL
- uploaded file
- local path
- arbitrary URL

Future normalization:

- PEP-style name normalization policy
- case/punctuation normalization
- Unicode/confusable caution
- typo-squatting caution
- project rename/reuse caution
- private package rejection
- credential stripping or rejection
- package-name public-safe fingerprint for sensitive refs
- no raw private package/index publication

No implementation is added in P90.
