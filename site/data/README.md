# Site Data

This directory is reserved for static-site generator inputs that are neither
page JSON nor templates.

Generated Public Data Summaries v0 keeps this directory as non-runtime input
space while writing deterministic public data summaries into `site/dist/data/`
during builds. Those generated files are static JSON only; they do not add live
data, live probes, or external baseline observations.
