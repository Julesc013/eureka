# Human Live Search Acceptance Rehearsal

Use this only after the operator live canary has passed.

## Setup

```powershell
$env:BRAVE_SEARCH_API_KEY="<your-key>"
python scripts/eureka.py --instance ..\instances\live-acceptance bootstrap --no-demo
python scripts/eureka.py --instance ..\instances\live-acceptance canary preflight
```

## Start

```powershell
python scripts/eureka.py --instance ..\instances\live-acceptance serve --live
```

Open the displayed local URL.

## Try

Search with three unseen queries:

```text
ordinary current-web query
obscure historical artifact query
archive-oriented query
```

For each query:

```text
search
use Hunt deeper
open a promising result
check whether a fetched/indexed result is understandable
restart Eureka
search locally for the saved result
```

## Decide

Record the outcome in:

```text
control/inventory/product/human_live_search_acceptance_decision_template.json
```

Choose only one:

```text
accepted
accepted_with_changes
rejected
```

Do not mark acceptance from automated checks. The operator verdict is the
product decision.
