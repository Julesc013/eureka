# Validation

Required IA-00 through IA-07 validators, focused tests, architecture boundary
checks, generated artifact cleanliness, and AIDE checks are run as part of the
IA-07 closure.

Full unittest discovery is recommended if `runtime/index/public` changes
substantially; IA-07 uses existing public-index store APIs and adds IA-specific
wrappers.
