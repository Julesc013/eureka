# Confidence And Review Model

Candidate confidence describes review priority and evidence posture. It does
not accept truth.

Required review fields include:

- `review_status`
- `required_reviews`
- `promotion_allowed_now: false`
- `promotion_policy_required: true`

The hard `confidence_not_truth: true` flag prevents confidence from becoming
acceptance. Promotion remains future work behind P65.
