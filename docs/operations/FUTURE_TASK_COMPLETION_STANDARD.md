# Future Task Completion Standard

A task is not complete merely because contracts, policies, examples, validators, or audit reports exist.

Product-scoped tasks must prove behavior with:

- runtime code
- tests
- explicit command output
- persistent state where applicable
- audit evidence
- no forbidden side effects

If a task cannot finish in one shot, it must split before generating scaffold.

PASS_WITH_WARNINGS may advance only if every warning is:

- harmless,
- fixed,
- child-tasked, or
- explicitly blocking.

Future work must keep product semantics in product code and contracts, not task packets or audit vocabulary.
