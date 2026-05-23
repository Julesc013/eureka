# Action Taxonomy Contract

`contracts/schema/control/policies/actions/action_taxonomy.v0.json` defines the J0 action families.

Current safe families are `view`, `inspect`, `compare`, `cite`, `export`, `preserve_manifest`, `acquisition_manifest`, and `blocked_action`.

Future risky families are `download_future`, `mirror_future`, `install_future`, `execute_future`, `emulate_future`, `submit_future`, and `import_future`. They are deferred and disabled in J0.

The taxonomy is a vocabulary, not authorization. It does not download, mirror, install, execute, emulate, accept evidence, or mutate public/master indexes.
