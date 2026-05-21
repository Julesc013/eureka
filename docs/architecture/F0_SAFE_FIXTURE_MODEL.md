# F0 Safe Fixture Model

F0 fixtures are repo-local, deterministic, fixture-only examples. They are not canonical evidence and not truth. The safe ZIP fixture is tiny and contains only harmless text members; unsafe/pathological cases use descriptor JSON rather than dangerous archives.

The fixture model is manifest-only:

- no downloads
- no filesystem extraction
- no execution
- no install or emulation
- no private or operator-local directories
- no accepted evidence
- no reviewed records

Every fixture packet carries non-claims so review can see that the output is only a candidate signal. Path traversal, absolute paths, excessive sizes, nested archives, symlinks, device files, encrypted archives, and unknown containers are blocked or deferred.

This model gives tests something concrete to inspect while keeping real extraction work out of scope until a later reviewed policy enables it.
