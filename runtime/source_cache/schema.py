"""SQLite schema for the durable source cache store."""

from __future__ import annotations

SCHEMA_VERSION = "source_cache_store.v0"

REQUIRED_TABLES = (
    "source_cache_meta",
    "source_cache_migrations",
    "source_records",
    "metadata_responses",
    "source_observations",
    "normalized_observations",
    "cache_entries",
)

CREATE_META_TABLE = """
CREATE TABLE IF NOT EXISTS source_cache_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
)
"""

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS source_cache_migrations (
  id TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at TEXT NOT NULL
)
"""

CREATE_SOURCE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS source_records (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_id TEXT NOT NULL UNIQUE,
  source_family TEXT NOT NULL,
  trust_lane TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_METADATA_RESPONSES_TABLE = """
CREATE TABLE IF NOT EXISTS metadata_responses (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_id TEXT NOT NULL,
  request_id TEXT NOT NULL,
  response_id TEXT NOT NULL UNIQUE,
  response_fingerprint TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_SOURCE_OBSERVATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS source_observations (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_id TEXT NOT NULL,
  request_id TEXT NOT NULL,
  response_id TEXT NOT NULL,
  observation_id TEXT NOT NULL UNIQUE,
  response_fingerprint TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_NORMALIZED_OBSERVATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS normalized_observations (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_family TEXT NOT NULL,
  observation_id TEXT NOT NULL,
  normalized_observation_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_CACHE_ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS cache_entries (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_family TEXT NOT NULL,
  trust_lane TEXT NOT NULL,
  request_id TEXT NOT NULL,
  response_id TEXT NOT NULL,
  observation_id TEXT NOT NULL,
  normalized_observation_id TEXT NOT NULL,
  response_fingerprint TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  limitations_json TEXT NOT NULL,
  warnings_json TEXT NOT NULL
)
"""

CREATE_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_metadata_responses_source_id ON metadata_responses(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_source_observations_source_id ON source_observations(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_normalized_observations_source_id ON normalized_observations(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_cache_entries_source_id ON cache_entries(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_cache_entries_status ON cache_entries(status)",
)

INITIAL_SCHEMA_STATEMENTS = (
    CREATE_META_TABLE,
    CREATE_MIGRATIONS_TABLE,
    CREATE_SOURCE_RECORDS_TABLE,
    CREATE_METADATA_RESPONSES_TABLE,
    CREATE_SOURCE_OBSERVATIONS_TABLE,
    CREATE_NORMALIZED_OBSERVATIONS_TABLE,
    CREATE_CACHE_ENTRIES_TABLE,
    *CREATE_INDEXES,
)
