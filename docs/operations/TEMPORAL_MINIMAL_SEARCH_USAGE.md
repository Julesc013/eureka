# Temporal Minimal Search Usage

Temporal Minimal Search is a contract for future renderers. It is not CSS, not
a frontend framework, and not an instruction to rewrite `site/dist`.

## How Future Work Should Use It

1. Choose a canonical view model.
2. Choose a governed representation profile.
3. Choose a design profile from `control/inventory/publication/design_profile_matrix.json`.
4. Apply the referenced token set only as presentation guidance.
5. Verify semantic visibility before comparing pixels or styling.

## Profiles

- `eureka_default` maps to standard HTML.
- `classic_search_1998` maps to lite/HTML 3.2-ish projections.
- `classic_search_2004` and `classic_search_2010` map to standard/lite HTML.
- `high_contrast`, `terminal`, `print`, and `text_only` preserve meaning in
  accessibility, terminal/text, print, and file-tree surfaces.

These are profiles over the same components and route meanings, not separate
products or route identities.

## Guardrails

- Do not copy external search-engine logos, exact page identity, exact CSS/HTML, or
  protected trade dress.
- Do not imply affiliation with search engines or use misleading official
  source labels.
- Do not hide source, evidence, risk, rights, limitations, gaps, absence scope,
  candidate state, or blocked actions.
- Do not claim hosted backend, live probes, downloads, uploads, accounts,
  telemetry, rights clearance, malware safety, exhaustive search, or automatic
  promotion.

## Validation

```text
python scripts/validate_design_tokens.py
python scripts/validate_temporal_minimal_search.py
python scripts/validate_track_a_contracts.py
```

This task adds no renderer, CSS implementation, route activation, or generated
site artifact mutation.
