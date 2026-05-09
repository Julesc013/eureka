# H1 Metadata Review Integration

H1 review integration consumes explicit fixture replay outputs and blocked or approved live-probe outputs. It produces review queue seed previews, source-cache review seeds, evidence candidate review seeds, candidate promotion previews, coverage update previews, scorecard updates, and source-pack update previews.

It is not review persistence, candidate promotion, source-cache persistence, evidence acceptance, public truth, or index mutation. Review seeds are prompts for later human or governed review workflows; they are not review decisions.

Validation:

```text
python scripts/integrate_h1_metadata_review.py --input-dir examples/connectors/h1_metadata_wave/replay_results --check
python scripts/validate_h1_review_quality_audit.py
```
