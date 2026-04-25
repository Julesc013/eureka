# Audit Schemas

This directory contains lightweight, stdlib-friendly JSON schema documents for
repo audit artifacts.

The current schema is intentionally small:

- `finding.schema.json` describes a structured audit finding.
- `finding_categories.json` lists accepted categories and severities for
  Comprehensive Test/Eval Operating Layer and Repo Audit v0.

Python tests validate required fields directly with `json`; they do not require
an external JSON Schema validator.

