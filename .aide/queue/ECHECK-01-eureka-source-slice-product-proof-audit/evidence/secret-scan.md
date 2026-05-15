# Secret / Local-State Scan

## Command

Targeted `rg` scan over `.aide`, `.aide.local.example`, AGENTS/README and
product/governance roots for:

`sk-*`, `sk-ant`, `api_key`, `SECRET`, `TOKEN`, `PASSWORD`,
`BEGIN PRIVATE KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and
`DEEPSEEK_API_KEY`.

## Result

- Match count after post-write scan: 3697.
- Classification: `PASS_WITH_FALSE_POSITIVES`.

## Inspection Summary

The matches are policy terms, task-id text, docs, examples, test fixtures,
secret-scan tests, fake fixture strings, or validators that intentionally reject
credential-shaped content.

Examples of inspected false-positive classes:

- `AGENTS.md` task-id references.
- `.aide/verification/secret-scan-policy.yaml` policy terms.
- `.aide/upgrade/**` preservation-plan references to secret policy docs.
- tests with fake values such as `sk-testsecretvalue000`,
  `sk-exampleSecretValue`, `api_key=example`, or `BEGIN PRIVATE KEY` assertions.
- runtime policy code that scans for `api_key` markers.

No actual provider key, private key, raw prompt, raw response, `.aide.local`
content, or credential assignment was identified. The ECHECK-01 reports add a
small number of additional policy-term matches such as `provider` and `task-id`
references; these are false positives.
