# Public Search UX MVP

`PUBLIC-SEARCH-UX-MVP-00` renders existing public search view-model projections into a minimal no-JS public search experience.

The MVP is search-first and read-only. It uses committed snapshot/view-model examples and does not deploy, publish, mutate indexes, call live sources, fetch files, download, OCR, extract, install, execute, or call model providers.

## Pages

- `/` search home with a GET form.
- `/search?q=...` results page.
- `/object/{id}` reviewed-object detail.
- `/candidate/{id}` candidate detail.
- `/need/{id}` known-need detail.
- `/source/{id}` source/source-lead detail.
- `/evidence/{id}` evidence or bounded-absence detail.
- `/status` public-alpha status.

## Result States

The renderer preserves view-model semantics. Verified records, reviewed metadata records, reviewed source leads, candidates, known needs, absences, and near misses are visibly distinct.

Limited reviewed metadata/source-lead records improve usefulness but are not verified artifacts, downloads, malware-clean assertions, rights clearances, or compatibility guarantees.

## Boundary

This task creates examples, inventories, docs, tests, and audit evidence only. `site/dist`, `data/public_index`, reviewed indexes, master indexes, public indexes, operator instances, and public runtime state remain untouched.
