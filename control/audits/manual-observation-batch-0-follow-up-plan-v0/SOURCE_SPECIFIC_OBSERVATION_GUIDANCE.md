# Source-specific Observation Guidance

Codex must not perform these observations. This guidance is for a human operator.

## Google or General Web Search

Record the exact query, visible filters, result date if visible, top relevant organic results, and visible title/locator/summary. Do not record private account information, personalization diagnostics, browser profile details, or private search history. Classify exact results only when the result directly identifies the requested artifact or actionable target. Mark ambiguous broad pages as partial or near miss.

## Internet Archive Item/Search Pages

Record whether the hit is an item, collection, file/member, OCR/full-text hit, or metadata-only hit. Preserve item identifiers or stable visible locators if safe. Do not call Internet Archive APIs, CDX, Memento, or Wayback endpoints for this task. Do not treat item presence as rights clearance, malware safety, or installability.

## GitHub or Repository Search

Record repository or release identity only when it is visible through manual browsing. Do not clone repositories, download release assets, fetch raw files, use tokens, or inspect private repositories. Classify private, token-required, or ambiguous repository results as blocked or near miss, not exact.

## SourceForge or Legacy Project Hosts

Record project title, visible version/platform notes, and whether the page is a project page, file listing, forum thread, or documentation result. Do not download installers or archives. If the page is only a container with unclear artifact identity, classify as partial.

## Package Registries

Record package name, visible metadata, version cues, and compatibility notes when visible. Do not use package-manager commands, registry APIs, downloads, dependency resolution, installs, or lifecycle scripts. Registry presence is not installability or dependency safety.

## Software Preservation/Catalogue Sites

Record catalogue title, object identity, version/platform fields, and source/provenance notes if visible. Do not assume preservation catalogue presence means a safe or legal executable. If the catalogue entry points to another source but does not provide enough identity, classify as partial.

## Forum, Manual, and Community Sources

Record concise paraphrased summaries and stable visible locators. Keep quotes short and necessary. Treat posts as observations, not truth. Mark uncertainty, age, conflicts, and whether the result is advice, pointer, mirror, or direct artifact reference.

## Duplicate or Ambiguous Results

Record duplicates as duplicates. Do not collapse them into one truth claim. If two results conflict, preserve both and note the conflict in `comparison_notes` or `failure_modes`.

