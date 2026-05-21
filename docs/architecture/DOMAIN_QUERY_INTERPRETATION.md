# DOMAIN Query Interpretation

DOMAIN query interpretation adds typed hints to a query without changing the
kernel that resolves artefacts. The same Local/HUNT/PLAY/IA/Workbench stack
continues to handle evidence, review, absence, and result lanes.

The hint model records:

- promote terms that make a result more reviewable for that domain
- suppress terms that reduce misleading interpretations
- source-family preferences that are hints only
- expected result lanes and review posture
- SYN cases that pressure-test the interpretation

DOMAIN hints are not truth. The no live source boundary is deliberate: a source preference such as Internet Archive
metadata, future Wayback traces, or future package registry metadata does not
perform a live source call and does not create evidence. It only tells later
planning layers what kind of source family might be worth review.

Unsafe actions remain blocked. DOMAIN query hints do not download, extract,
execute, install, call models, mutate indexes, deploy, or make production/public
launch claims.
