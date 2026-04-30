# Artifact Groups

| artifact group | kind | owner/check | committed-output rule |
| --- | --- | --- | --- |
| `public_data_summaries` | generated | `python scripts/generate_public_data_summaries.py --check` | `site/dist/data/*.json` must match generator output. |
| `compatibility_surfaces` | generated | `python scripts/generate_compatibility_surfaces.py --check` | `site/dist/lite`, `text`, and `files` must match generator output. |
| `static_resolver_demos` | generated | `python scripts/generate_static_resolver_demos.py --check` | Static no-JS demo pages and snapshots must match generator output. |
| `static_snapshot_example` | generated seed | `python scripts/generate_static_snapshot.py --check` | Snapshot seed files must match the format generator and validator. |
| `static_site_dist` | generated static artifact | `python site/build.py --check` | `site/dist` is checked by rebuilding into a temporary directory and by the Pages artifact checker. |
| `python_oracle_goldens` | generated | `python scripts/generate_python_oracle_golden.py --check` | Python oracle fixtures must match current Python reference behavior. |
| `public_alpha_rehearsal_evidence` | generated evidence | `python scripts/generate_public_alpha_rehearsal_evidence.py --check` | Rehearsal evidence must stay synchronized with route/static/eval inputs. |
| `publication_inventory` | hybrid governance | `python scripts/validate_publication_inventory.py` | Publication inventories must parse and pass validators. |
| `test_registry` | hybrid governance | `python -m unittest tests.operations.test_test_eval_operating_layer` | Test registry and command matrix must stay machine-readable and aligned. |
| `aide_metadata` | hybrid governance | `python -m unittest tests.hardening.test_aide_test_registry_consistency` | AIDE command and queue metadata remains repo-operating metadata only. |
