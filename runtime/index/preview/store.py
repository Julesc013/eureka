"""Operational SQLite Preview Index for unreviewed SourceObservations."""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sqlite3
from typing import Any, Mapping, Protocol, Sequence

from runtime.connectors.web import SourceObservation

from .index import build_preview_index, rollback_preview_index, validate_preview_index


class PreviewIndexStore(Protocol):
    def upsert_observations(self, observations: Sequence[SourceObservation | Mapping[str, Any]]) -> dict[str, Any]:
        """Insert or update policy-approved observations and derived documents."""

    def search(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        """Search the operational Preview Index."""

    def get(self, document_id: str) -> dict[str, Any] | None:
        """Load one PreviewDocument by id."""

    def stats(self) -> dict[str, Any]:
        """Return operational store counts and capabilities."""

    def export_generation(self, out_root: str | Path) -> dict[str, Any]:
        """Export observations into the immutable generation format."""


class SQLitePreviewIndexStore:
    """SQLite/FTS operational index for local unreviewed discoveries."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self._fts_available = _fts5_available(self.conn)
        self._migrate()

    def close(self) -> None:
        self.conn.close()

    def upsert_observations(self, observations: Sequence[SourceObservation | Mapping[str, Any]]) -> dict[str, Any]:
        records = [_observation_payload(item) for item in observations]
        with self.conn:
            for record in records:
                observation_id = str(record.get("observation_id") or "")
                if not observation_id:
                    raise ValueError("observation_id is required")
                if bool(record.get("provider_result_payload_persisted", False)):
                    raise ValueError("provider result payload cannot be indexed")
                canonical_url = str(record.get("canonical_url") or record.get("final_url") or "")
                content_hash = str(record.get("content_hash") or "")
                document_id = _document_id(canonical_url, content_hash)
                payload = json.dumps(record, sort_keys=True)
                self.conn.execute(
                    """
                    INSERT INTO source_observation(
                      observation_id, canonical_url, final_url, content_hash, title,
                      extracted_text, retrieved_at, run_id, query, source_family, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(observation_id) DO UPDATE SET
                      canonical_url=excluded.canonical_url,
                      final_url=excluded.final_url,
                      content_hash=excluded.content_hash,
                      title=excluded.title,
                      extracted_text=excluded.extracted_text,
                      retrieved_at=excluded.retrieved_at,
                      run_id=excluded.run_id,
                      query=excluded.query,
                      source_family=excluded.source_family,
                      payload_json=excluded.payload_json
                    """,
                    (
                        observation_id,
                        canonical_url,
                        str(record.get("final_url") or canonical_url),
                        content_hash,
                        _title(record),
                        str(record.get("extracted_text") or ""),
                        str(record.get("retrieved_at") or ""),
                        str(record.get("run_id") or ""),
                        str(record.get("query") or ""),
                        str(record.get("source_family") or "web"),
                        payload,
                    ),
                )
                self.conn.execute(
                    """
                    INSERT INTO preview_document(
                      document_id, canonical_url, title, body, source_family,
                      retrieved_at, observation_id, run_id, query, content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(document_id) DO UPDATE SET
                      canonical_url=excluded.canonical_url,
                      title=excluded.title,
                      body=excluded.body,
                      source_family=excluded.source_family,
                      retrieved_at=excluded.retrieved_at,
                      observation_id=excluded.observation_id,
                      run_id=excluded.run_id,
                      query=excluded.query,
                      content_hash=excluded.content_hash
                    """,
                    (
                        document_id,
                        canonical_url,
                        _title(record),
                        str(record.get("extracted_text") or ""),
                        str(record.get("source_family") or "web"),
                        str(record.get("retrieved_at") or ""),
                        observation_id,
                        str(record.get("run_id") or ""),
                        str(record.get("query") or ""),
                        content_hash,
                    ),
                )
                self.conn.execute("DELETE FROM link_edge WHERE observation_id = ?", (observation_id,))
                for link in record.get("outbound_links") or []:
                    if isinstance(link, Mapping):
                        self.conn.execute(
                            "INSERT INTO link_edge(observation_id, source_url, target_url, rel, anchor_text) VALUES (?, ?, ?, ?, ?)",
                            (
                                observation_id,
                                str(link.get("source_url") or ""),
                                str(link.get("target_url") or ""),
                                str(link.get("rel") or ""),
                                str(link.get("anchor_text") or ""),
                            ),
                        )
                self._upsert_fts(document_id, _title(record), canonical_url, str(record.get("extracted_text") or ""))
        return {
            "schema_version": "eureka.preview_index_upsert.v0",
            "status": "pass",
            "observation_count": len(records),
            "document_count": len(records),
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "provider_result_payload_persisted": False,
        }

    def search(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        clean = " ".join(str(query or "").split())
        limit = max(1, min(int(limit or 10), 50))
        if not clean:
            rows: list[sqlite3.Row] = []
        elif self._fts_available:
            rows = list(
                self.conn.execute(
                    """
                    SELECT d.*, bm25(preview_document_fts) AS lexical_score
                    FROM preview_document_fts
                    JOIN preview_document d ON d.document_id = preview_document_fts.document_id
                    WHERE preview_document_fts MATCH ?
                    ORDER BY lexical_score, d.retrieved_at DESC, d.document_id
                    LIMIT ?
                    """,
                    (_fts_query(clean), limit),
                )
            )
        else:
            like = f"%{clean}%"
            rows = list(
                self.conn.execute(
                    """
                    SELECT *, 0.0 AS lexical_score
                    FROM preview_document
                    WHERE title LIKE ? OR body LIKE ? OR canonical_url LIKE ?
                    ORDER BY retrieved_at DESC, document_id
                    LIMIT ?
                    """,
                    (like, like, like, limit),
                )
            )
        results = [_row_to_result(row, clean) for row in rows]
        return {
            "schema_version": "eureka.sqlite_preview_index_search.v0",
            "status": "pass",
            "query": clean,
            "result_count": len(results),
            "results": results,
            "fts": self._fts_available,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "provider_network_calls": False,
        }

    def get(self, document_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM preview_document WHERE document_id = ?", (str(document_id or ""),)).fetchone()
        return _row_to_result(row, "") if row else None

    def stats(self) -> dict[str, Any]:
        observation_count = int(self.conn.execute("SELECT COUNT(*) FROM source_observation").fetchone()[0])
        document_count = int(self.conn.execute("SELECT COUNT(*) FROM preview_document").fetchone()[0])
        link_count = int(self.conn.execute("SELECT COUNT(*) FROM link_edge").fetchone()[0])
        return {
            "schema_version": "eureka.sqlite_preview_index_stats.v0",
            "status": "pass",
            "path": str(self.path),
            "observation_count": observation_count,
            "document_count": document_count,
            "link_count": link_count,
            "fts": self._fts_available,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        }

    def export_generation(self, out_root: str | Path) -> dict[str, Any]:
        export_root = Path(out_root)
        delta_root = export_root / "source-observation-delta"
        delta_root.mkdir(parents=True, exist_ok=True)
        records = [_export_observation(json.loads(row["payload_json"])) for row in self.conn.execute("SELECT payload_json FROM source_observation ORDER BY observation_id")]
        observation_file = delta_root / "source_observations.jsonl"
        observation_file.write_text("\n".join(json.dumps(item, sort_keys=True) for item in records) + ("\n" if records else ""), encoding="utf-8")
        manifest = {
            "schema_version": "eureka.source_observation_delta_manifest.v0",
            "observation_file": observation_file.name,
            "provider_result_payload_persisted": False,
        }
        manifest_path = delta_root / "source_observation_delta_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        build = build_preview_index(out_root=export_root / "immutable", source_observation_delta=manifest_path, activate=True)
        validation = validate_preview_index(build["current_path"], strict=True)
        return {**build, "validation": validation, "source_observation_delta": str(manifest_path)}

    def rollback(self, out_root: str | Path, generation_id: str) -> dict[str, Any]:
        return rollback_preview_index(Path(out_root) / "immutable", generation_id)

    def _migrate(self) -> None:
        with self.conn:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys=ON")
            self.conn.execute("PRAGMA busy_timeout=5000")
            self.conn.execute("CREATE TABLE IF NOT EXISTS schema_migration(version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS source_observation(
                  observation_id TEXT PRIMARY KEY,
                  canonical_url TEXT NOT NULL,
                  final_url TEXT NOT NULL,
                  content_hash TEXT NOT NULL,
                  title TEXT NOT NULL,
                  extracted_text TEXT NOT NULL,
                  retrieved_at TEXT NOT NULL,
                  run_id TEXT NOT NULL,
                  query TEXT NOT NULL,
                  source_family TEXT NOT NULL,
                  payload_json TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preview_document(
                  document_id TEXT PRIMARY KEY,
                  canonical_url TEXT NOT NULL,
                  title TEXT NOT NULL,
                  body TEXT NOT NULL,
                  source_family TEXT NOT NULL,
                  retrieved_at TEXT NOT NULL,
                  observation_id TEXT NOT NULL REFERENCES source_observation(observation_id),
                  run_id TEXT NOT NULL,
                  query TEXT NOT NULL,
                  content_hash TEXT NOT NULL
                )
                """
            )
            self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_preview_document_canonical_hash ON preview_document(canonical_url, content_hash)")
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS link_edge(
                  link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  observation_id TEXT NOT NULL REFERENCES source_observation(observation_id),
                  source_url TEXT NOT NULL,
                  target_url TEXT NOT NULL,
                  rel TEXT NOT NULL,
                  anchor_text TEXT NOT NULL
                )
                """
            )
            self.conn.execute("CREATE TABLE IF NOT EXISTS fetch_error(error_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS hunt_run(run_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS hunt_query(query_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, query TEXT NOT NULL)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS index_generation(generation_id TEXT PRIMARY KEY, manifest_path TEXT NOT NULL, activated_at TEXT)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS source_score(source_family TEXT PRIMARY KEY, payload_json TEXT NOT NULL)")
            if self._fts_available:
                self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS preview_document_fts USING fts5(document_id UNINDEXED, title, url, body)")
            self.conn.execute("PRAGMA user_version=1")

    def _upsert_fts(self, document_id: str, title: str, url: str, body: str) -> None:
        if not self._fts_available:
            return
        self.conn.execute("DELETE FROM preview_document_fts WHERE document_id = ?", (document_id,))
        self.conn.execute("INSERT INTO preview_document_fts(document_id, title, url, body) VALUES (?, ?, ?, ?)", (document_id, title, url, body))


def _observation_payload(observation: SourceObservation | Mapping[str, Any]) -> dict[str, Any]:
    payload = observation.to_dict() if isinstance(observation, SourceObservation) else dict(observation)
    payload["provider_result_payload_persisted"] = False
    return payload


def _title(record: Mapping[str, Any]) -> str:
    return str(record.get("title") or record.get("extracted_title") or record.get("canonical_url") or "Indexed observation")


def _document_id(canonical_url: str, content_hash: str) -> str:
    return "preview:" + hashlib.sha256(f"{canonical_url}\n{content_hash}".encode("utf-8")).hexdigest()[:24]


def _row_to_result(row: sqlite3.Row, query: str) -> dict[str, Any]:
    title = str(row["title"])
    url = str(row["canonical_url"])
    why_matched = []
    if query and query.casefold() in title.casefold():
        why_matched.append("title contains query")
    if query and query.casefold() in str(row["body"]).casefold():
        why_matched.append("extracted text contains query")
    if query and query.casefold() in url.casefold():
        why_matched.append("URL contains query")
    return {
        "document_id": str(row["document_id"]),
        "state": "INDEXED - UNREVIEWED",
        "title": title,
        "url": url,
        "snippet": _snippet(str(row["body"]), query),
        "source_family": str(row["source_family"]),
        "retrieved_at": str(row["retrieved_at"]),
        "observation_refs": [str(row["observation_id"])],
        "run_refs": [str(row["run_id"])] if row["run_id"] else [],
        "query": str(row["query"]),
        "why_matched": why_matched or ["lexical match"],
        "why_ranked": ["FTS/BM25 lexical score" if "lexical_score" in row.keys() else "lexical fallback score"],
        "authority": "source_observation_only",
        "status": "mention_only",
        "review_required": True,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
    }


def _snippet(text: str, query: str, *, size: int = 240) -> str:
    compact = " ".join(str(text or "").split())
    if not compact:
        return ""
    needle = str(query or "").casefold()
    index = compact.casefold().find(needle) if needle else -1
    if index < 0:
        return compact[:size]
    start = max(0, index - 60)
    return compact[start : start + size]


def _fts_query(query: str) -> str:
    terms = [term.replace('"', "") for term in query.split() if term.strip()]
    return " OR ".join(f'"{term}"' for term in terms) or '""'


def _fts5_available(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.fts_probe USING fts5(value)")
        return True
    except sqlite3.DatabaseError:
        return False


def _export_observation(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **dict(record),
        "query_seed": str(record.get("query") or record.get("title") or record.get("canonical_url") or ""),
        "transport_status": "success",
        "normalized_metadata": {
            "title": str(record.get("title") or record.get("extracted_title") or ""),
            "url": str(record.get("canonical_url") or record.get("final_url") or ""),
            "text": str(record.get("extracted_text") or ""),
        },
        "provider_mode": "independent_fetch",
        "review_state": "unreviewed",
        "provider_result_payload_persisted": False,
    }
