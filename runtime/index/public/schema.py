"""SQLite schema for the local reviewed public index store."""

from __future__ import annotations

SCHEMA_VERSION = "public_index_store.v0"

REQUIRED_TABLES = (
    "public_index_meta",
    "public_index_migrations",
    "public_index_records",
    "public_index_rebuilds",
    "public_index_search_terms",
    "public_index_source_refs",
    "public_index_evidence_refs",
    "public_index_review_refs",
)

CREATE_META_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_migrations (
  id TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at TEXT NOT NULL
)
"""

CREATE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_records (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  rebuild_id TEXT,
  source_id TEXT NOT NULL,
  source_cache_entry_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  review_item_id TEXT NOT NULL,
  review_decision_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  searchable_text TEXT NOT NULL,
  normalized_fields_json TEXT NOT NULL,
  source_family TEXT NOT NULL,
  trust_lane TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL,
  status TEXT NOT NULL
)
"""

CREATE_REBUILDS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_rebuilds (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  rebuild_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  included_count INTEGER NOT NULL,
  excluded_count INTEGER NOT NULL,
  include_statuses_json TEXT NOT NULL,
  source_cache_db TEXT NOT NULL,
  evidence_ledger_db TEXT NOT NULL,
  review_queue_db TEXT NOT NULL,
  public_index_db TEXT NOT NULL,
  dry_run INTEGER NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_SEARCH_TERMS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_search_terms (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  record_id TEXT NOT NULL,
  term TEXT NOT NULL,
  UNIQUE(record_id, term)
)
"""

CREATE_SOURCE_REFS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_source_refs (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  record_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_cache_entry_id TEXT NOT NULL,
  UNIQUE(record_id, source_cache_entry_id)
)
"""

CREATE_EVIDENCE_REFS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_evidence_refs (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  record_id TEXT NOT NULL,
  evidence_id TEXT NOT NULL,
  UNIQUE(record_id, evidence_id)
)
"""

CREATE_REVIEW_REFS_TABLE = """
CREATE TABLE IF NOT EXISTS public_index_review_refs (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  record_id TEXT NOT NULL,
  review_item_id TEXT NOT NULL,
  review_decision_id TEXT NOT NULL,
  UNIQUE(record_id, review_item_id, review_decision_id)
)
"""

CREATE_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_public_index_records_source_id ON public_index_records(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_public_index_records_status ON public_index_records(status)",
    "CREATE INDEX IF NOT EXISTS idx_public_index_records_text ON public_index_records(searchable_text)",
    "CREATE INDEX IF NOT EXISTS idx_public_index_search_terms_term ON public_index_search_terms(term)",
    "CREATE INDEX IF NOT EXISTS idx_public_index_source_refs_source ON public_index_source_refs(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_public_index_evidence_refs_evidence ON public_index_evidence_refs(evidence_id)",
    "CREATE INDEX IF NOT EXISTS idx_public_index_review_refs_item ON public_index_review_refs(review_item_id)",
)

INITIAL_SCHEMA_STATEMENTS = (
    CREATE_META_TABLE,
    CREATE_MIGRATIONS_TABLE,
    CREATE_RECORDS_TABLE,
    CREATE_REBUILDS_TABLE,
    CREATE_SEARCH_TERMS_TABLE,
    CREATE_SOURCE_REFS_TABLE,
    CREATE_EVIDENCE_REFS_TABLE,
    CREATE_REVIEW_REFS_TABLE,
    *CREATE_INDEXES,
)
