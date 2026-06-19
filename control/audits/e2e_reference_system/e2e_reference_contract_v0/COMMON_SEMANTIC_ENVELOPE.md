# Common Semantic Envelope

No giant base schema is introduced. The E2E runner should use a minimal profile:

- schema or packet version;
- semantic type;
- stable object ID;
- relevant lifecycle timestamps;
- authority level;
- provenance/source refs;
- parent run/workunit refs;
- semantic hash;
- privacy classification;
- synthetic/test-only posture;
- extension/versioning posture.

Not every field is required on every object.

