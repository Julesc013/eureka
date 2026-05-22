# Archive

`archive/` retains historical, retired, or quarantined material. It is not an
active source authority and must not be imported by runtime or surface code.

`scripts/validate_archive_import_guard.py` checks that active Python under
`runtime/`, `surfaces/`, `site/`, and `native/` does not import
`archive.prototypes.*`. Tools and tests may read archived material as audit
evidence.
