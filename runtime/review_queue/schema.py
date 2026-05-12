"""SQLite schema for the durable review queue store."""

from __future__ import annotations

SCHEMA_VERSION = "review_queue_store.v0"

REQUIRED_TABLES = (
    "review_queue_meta",
    "review_queue_migrations",
    "review_items",
    "review_events",
    "review_evidence_links",
    "review_source_cache_links",
    "review_decisions",
)

CREATE_META_TABLE = """
CREATE TABLE IF NOT EXISTS review_queue_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS review_queue_migrations (
  id TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at TEXT NOT NULL
)
"""

CREATE_REVIEW_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS review_items (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  review_item_id TEXT NOT NULL UNIQUE,
  evidence_id TEXT,
  source_cache_entry_id TEXT,
  subject_kind TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  queue_status TEXT NOT NULL,
  priority INTEGER NOT NULL,
  summary TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_REVIEW_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS review_events (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  review_item_id TEXT NOT NULL,
  event_kind TEXT NOT NULL,
  event_payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_REVIEW_EVIDENCE_LINKS_TABLE = """
CREATE TABLE IF NOT EXISTS review_evidence_links (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  review_item_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  UNIQUE(review_item_id, evidence_id)
)
"""

CREATE_REVIEW_SOURCE_CACHE_LINKS_TABLE = """
CREATE TABLE IF NOT EXISTS review_source_cache_links (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  review_item_id TEXT NOT NULL,
  source_cache_entry_id TEXT NOT NULL,
  UNIQUE(review_item_id, source_cache_entry_id)
)
"""

CREATE_REVIEW_DECISIONS_TABLE = """
CREATE TABLE IF NOT EXISTS review_decisions (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  review_item_id TEXT NOT NULL,
  decision_kind TEXT NOT NULL,
  decision_status TEXT NOT NULL,
  decision_actor TEXT NOT NULL,
  reason TEXT,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_review_items_status ON review_items(queue_status)",
    "CREATE INDEX IF NOT EXISTS idx_review_items_subject_kind ON review_items(subject_kind)",
    "CREATE INDEX IF NOT EXISTS idx_review_events_item ON review_events(review_item_id)",
    "CREATE INDEX IF NOT EXISTS idx_review_evidence_links_item ON review_evidence_links(review_item_id)",
    "CREATE INDEX IF NOT EXISTS idx_review_source_cache_links_item ON review_source_cache_links(review_item_id)",
    "CREATE INDEX IF NOT EXISTS idx_review_decisions_item ON review_decisions(review_item_id)",
)

INITIAL_SCHEMA_STATEMENTS = (
    CREATE_META_TABLE,
    CREATE_MIGRATIONS_TABLE,
    CREATE_REVIEW_ITEMS_TABLE,
    CREATE_REVIEW_EVENTS_TABLE,
    CREATE_REVIEW_EVIDENCE_LINKS_TABLE,
    CREATE_REVIEW_SOURCE_CACHE_LINKS_TABLE,
    CREATE_REVIEW_DECISIONS_TABLE,
    *CREATE_INDEXES,
)
