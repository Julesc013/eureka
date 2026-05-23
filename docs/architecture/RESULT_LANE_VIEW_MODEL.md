# Result Lane View Model

Result lane view models sit between runtime packets and surfaces. Runtime/local service helpers build packet-shaped dictionaries from existing local records. Surfaces render or further restrict those packets without owning product truth.

Required preservation rules:

- Preserve truth_level.
- Preserve review_required.
- Preserve uncertainty and limitations.
- Preserve provenance for operator projections.
- Preserve action posture and blocked actions.
- Hide operator-only detail from public and native read-only projections.

Public and native projections may show safe summaries, bounded absence, near misses, and blocked policy posture. They must not expose source cache internals, review queue internals, private local paths, raw debug fields, or operator-only provenance.

The current helper under runtime/local/service is packet/view-model code, not
presentation ownership. Surface-local projection helpers live under
surfaces/web/workbench and do not import runtime internals.
