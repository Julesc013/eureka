# Snapshot Renderer Semantic Parity

Every renderer must preserve the same core semantics:

- identity
- title and summary
- source posture
- evidence posture
- compatibility posture where present
- rights posture
- risk posture
- allowed and blocked actions
- limitations and no-claims
- known absence scope where present

Text, lite HTML, file-tree, and JSON manifest outputs can format those fields differently, but they must not drop or invert them.
