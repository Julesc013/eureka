"""HTML/plain-text extraction helpers for safe fetch outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import re
from urllib.parse import urljoin


@dataclass(frozen=True)
class LinkEdge:
    source_url: str
    target_url: str
    rel: str
    anchor_text: str

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": "link_edge.v0",
            "source_url": self.source_url,
            "target_url": self.target_url,
            "rel": self.rel,
            "anchor_text": self.anchor_text,
        }


@dataclass(frozen=True)
class ExtractedDocument:
    url: str
    title: str
    text: str
    canonical_url: str
    outbound_links: tuple[LinkEdge, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "extracted_document.v0",
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "canonical_url": self.canonical_url,
            "outbound_links": [item.to_dict() for item in self.outbound_links],
        }


def extract_document(url: str, body: bytes, content_type: str, *, max_text_chars: int = 200_000) -> ExtractedDocument:
    charset = _charset(content_type)
    text = body.decode(charset, errors="replace")
    mime = content_type.split(";", 1)[0].strip().casefold()
    if mime == "text/plain":
        return ExtractedDocument(url=url, title="", text=_compact_text(text)[:max_text_chars], canonical_url=url, outbound_links=())
    parser = _HTMLExtractor(url)
    parser.feed(text)
    parser.close()
    return ExtractedDocument(
        url=url,
        title=_compact_text(parser.title),
        text=_compact_text(" ".join(parser.text_parts))[:max_text_chars],
        canonical_url=parser.canonical_url or url,
        outbound_links=tuple(parser.links),
    )


class _HTMLExtractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.canonical_url = ""
        self.text_parts: list[str] = []
        self.links: list[LinkEdge] = []
        self._in_title = False
        self._skip_depth = 0
        self._active_href = ""
        self._active_rel = ""
        self._active_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key.casefold(): value or "" for key, value in attrs}
        tag = tag.casefold()
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if tag == "link" and "canonical" in attrs_map.get("rel", "").casefold() and attrs_map.get("href"):
            self.canonical_url = urljoin(self.base_url, attrs_map["href"])
        if tag == "a" and attrs_map.get("href"):
            self._active_href = urljoin(self.base_url, attrs_map["href"])
            self._active_rel = attrs_map.get("rel", "")
            self._active_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._active_href:
            self.links.append(LinkEdge(self.base_url, self._active_href, self._active_rel, _compact_text(" ".join(self._active_text))))
            self._active_href = ""
            self._active_rel = ""
            self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self.title += data
        if self._active_href:
            self._active_text.append(data)
        self.text_parts.append(data)


def _charset(content_type: str) -> str:
    match = re.search(r"charset=([^;]+)", str(content_type or ""), flags=re.IGNORECASE)
    return match.group(1).strip() if match else "utf-8"


def _compact_text(text: str) -> str:
    return " ".join(str(text or "").split())
