"""SQLite schema for the durable evidence ledger store."""

from __future__ import annotations

SCHEMA_VERSION = "evidence_ledger_store.v0"

REQUIRED_TABLES = (
    "evidence_ledger_meta",
    "evidence_ledger_migrations",
    "evidence_candidates",
    "evidence_events",
    "evidence_source_cache_links",
    "evidence_conflicts",
    "evidence_review_status",
)

CREATE_META_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_ledger_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_ledger_migrations (
  id TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at TEXT NOT NULL
)
"""

CREATE_EVIDENCE_CANDIDATES_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_candidates (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  evidence_id TEXT NOT NULL UNIQUE,
  source_id TEXT NOT NULL,
  source_cache_entry_id TEXT,
  observation_id TEXT NOT NULL,
  normalized_observation_id TEXT NOT NULL,
  claim_kind TEXT NOT NULL,
  claim_subject TEXT NOT NULL,
  claim_payload_json TEXT NOT NULL,
  status TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_EVIDENCE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_events (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  event_kind TEXT NOT NULL,
  event_payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_SOURCE_CACHE_LINKS_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_source_cache_links (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  source_cache_entry_id TEXT NOT NULL,
  UNIQUE(evidence_id, source_cache_entry_id)
)
"""

CREATE_CONFLICTS_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_conflicts (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  conflicting_evidence_id TEXT,
  conflict_kind TEXT NOT NULL,
  conflict_payload_json TEXT NOT NULL,
  status TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_REVIEW_STATUS_TABLE = """
CREATE TABLE IF NOT EXISTS evidence_review_status (
  evidence_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  status TEXT NOT NULL,
  reason TEXT,
  event_id TEXT NOT NULL
)
"""

CREATE_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_evidence_candidates_source_id ON evidence_candidates(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_evidence_candidates_status ON evidence_candidates(status)",
    "CREATE INDEX IF NOT EXISTS idx_evidence_candidates_claim_kind ON evidence_candidates(claim_kind)",
    "CREATE INDEX IF NOT EXISTS idx_evidence_events_evidence_id ON evidence_events(evidence_id)",
    "CREATE INDEX IF NOT EXISTS idx_evidence_events_kind ON evidence_events(event_kind)",
    "CREATE INDEX IF NOT EXISTS idx_evidence_source_cache_links_evidence_id ON evidence_source_cache_links(evidence_id)",
    "CREATE INDEX IF NOT EXISTS idx_evidence_conflicts_evidence_id ON evidence_conflicts(evidence_id)",
)

INITIAL_SCHEMA_STATEMENTS = (
    CREATE_META_TABLE,
    CREATE_MIGRATIONS_TABLE,
    CREATE_EVIDENCE_CANDIDATES_TABLE,
    CREATE_EVIDENCE_EVENTS_TABLE,
    CREATE_SOURCE_CACHE_LINKS_TABLE,
    CREATE_CONFLICTS_TABLE,
    CREATE_REVIEW_STATUS_TABLE,
    *CREATE_INDEXES,
)
