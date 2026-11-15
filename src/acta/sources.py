"""Polite web access + text extraction for problem sources.

Rules this module enforces (so adding a site can never turn the daily job into a scraper):
  * robots.txt is honoured; an unreadable/forbidden robots.txt means "blocked" (conservative);
  * one request per host every MIN_DELAY seconds, 10 s timeout, 2 MB cap;
  * an honest User-Agent that names the project;
  * responses are cached on disk so a page is never fetched twice.
"""
from __future__ import annotations

import hashlib
import io
import json
import logging
import re
import time
import urllib.robotparser
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

log = logging.getLogger("acta.sources")
UA_NAME = "ActaProblemataBot"
UA = {"User-Agent": f"{UA_NAME}/1.2 (+https://github.com/omax404/acta-problemata; open-source broadside)"}
TIMEOUT = 10
MAX_BYTES = 2_000_000
MIN_DELAY = 1.5
MIN_TEXT = 400            # shorter pages are navigation/stubs, not problems
MAX_TEXT = 6000           # what the LLM prompt can use anyway

_last_hit: dict[str, float] = {}
_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}


class FetchBlocked(RuntimeError):
    """robots.txt forbids (or could not confirm) access."""


@dataclass
class Fetched:
    content: bytes
    content_type: str
    url: str


# ── robots + fetching ────────────────────────────────────────
def _robots_for(url: str) -> urllib.robotparser.RobotFileParser | None:
    p = urlparse(url)
    origin = f"{p.scheme}://{p.netloc}"
    if origin in _robots:
        return _robots[origin]
    rp: urllib.robotparser.RobotFileParser | None
    try:
        r = requests.get(f"{origin}/robots.txt", headers=UA, timeout=TIMEOUT)
        if r.status_code == 200:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(r.text.splitlines())
        elif r.status_code in (404, 410):
            rp = urllib.robotparser.RobotFileParser()
            rp.parse([])                                   # no robots.txt = no restrictions
        else:
            rp = None                                      # 401/403/5xx: cannot confirm -> blocked
    except requests.RequestException:
        rp = None
    _robots[origin] = rp
    return rp


def allowed(url: str) -> bool:
    rp = _robots_for(url)
    return bool(rp and rp.can_fetch(UA_NAME, url))


def polite_get(url: str, cache_dir: Path | None = None) -> Fetched:
    if urlparse(url).scheme not in ("http", "https"):
        raise FetchBlocked(f"unsupported scheme: {url}")
    key = hashlib.sha1(url.encode()).hexdigest()
    if cache_dir:
        body, meta = cache_dir / f"{key}.bin", cache_dir / f"{key}.ct"
        if body.exists() and meta.exists():
            return Fetched(body.read_bytes(), meta.read_text(encoding="utf-8"), url)
    if not allowed(url):
        raise FetchBlocked(f"robots.txt does not allow {url}")
    host = urlparse(url).netloc
    wait = MIN_DELAY - (time.monotonic() - _last_hit.get(host, -1e9))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.monotonic()
    r = requests.get(url, headers=UA, timeout=TIMEOUT, stream=True)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} for {url}")
    data = b""
    for chunk in r.iter_content(65536):
        data += chunk
        if len(data) > MAX_BYTES:
            raise RuntimeError(f"response exceeds {MAX_BYTES} bytes: {url}")
    ctype = r.headers.get("content-type", "text/html").split(";")[0].strip().lower()
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        body.write_bytes(data)
        meta.write_text(ctype, encoding="utf-8")
    return Fetched(data, ctype, url)


# ── text extraction ──────────────────────────────────────────
_SKIP = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "button"}
_BLOCK = {"p", "br", "li", "div", "tr", "h1", "h2", "h3", "h4", "section", "article", "main", "td"}
_MAIN = {"article", "main"}


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.main = 0
        self.title = ""
        self.h1 = ""
        self._tag = ""
        self.all: list[str] = []
        self.in_main: list[str] = []

    def handle_starttag(self, tag, attrs):
        self._tag = tag
        if tag in _SKIP:
            self.skip += 1
        if tag in _MAIN:
            self.main += 1
        if tag in _BLOCK:
            self._add("\n")

    def handle_endtag(self, tag):
        if tag in _SKIP and self.skip:
            self.skip -= 1
        if tag in _MAIN and self.main:
            self.main -= 1
        if tag in _BLOCK:
            self._add("\n")
        self._tag = ""

    def handle_data(self, data):
        if self._tag == "title":
            self.title += data
        if self.skip:
            return
        if self._tag == "h1" and not self.h1:
            self.h1 = data.strip()
        self._add(data)

    def _add(self, s: str) -> None:
        self.all.append(s)
        if self.main:
            self.in_main.append(s)


def _clean(s: str) -> str:
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def html_to_text(html: str) -> tuple[str, str]:
    p = _Text()
    p.feed(html)
    main = _clean("".join(p.in_main))
    text = main if len(main) >= MIN_TEXT else _clean("".join(p.all))
    return (p.h1 or p.title.strip()), text


def extract_text(data: bytes, content_type: str) -> tuple[str, str]:
    """(title, text) from HTML, PDF or plain text; text is capped at MAX_TEXT."""
    if "pdf" in content_type or data[:4] == b"%PDF":
        from pypdf import PdfReader
        pages = [pg.extract_text() or "" for pg in PdfReader(io.BytesIO(data)).pages[:12]]
        text = _clean("\n".join(pages))
        title = text.split("\n", 1)[0][:100]
    elif "html" in content_type or data.lstrip()[:1] == b"<":
        title, text = html_to_text(data.decode("utf-8", errors="replace"))
    else:
        text = _clean(data.decode("utf-8", errors="replace"))
        title = text.split("\n", 1)[0][:100]
    return title, text[:MAX_TEXT]


# ── registry + health check ──────────────────────────────────
def load_registry(root: Path) -> list[dict]:
    f = root / "data" / "sources.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def listing_links(listing_html: str, base_url: str, pattern: str, limit: int = 15) -> list[str]:
    rx = re.compile(pattern)
    out: list[str] = []
    for href in re.findall(r'href=["\']([^"\'#]+)', listing_html):
        full = urljoin(base_url, href)
        if rx.search(full) and full not in out:
            out.append(full)
    return out[:limit]


def check_sources(root: Path) -> list[dict]:
    """One row per registry entry: robots verdict, reachability, listing matches. Never raises."""
    rows = []
    for s in load_registry(root):
        row = {"id": s["id"], "mode": s["mode"], "enabled": s["enabled"],
               "robots": "?", "http": "?", "links": "-"}
        try:
            row["robots"] = "allowed" if allowed(s["url"]) else "BLOCKED/unknown"
            if row["robots"] == "allowed":
                page = polite_get(s["url"])
                row["http"] = "ok"
                if s["mode"] == "listing" and s.get("listing_url") and s.get("link_pattern"):
                    lst = polite_get(s["listing_url"])
                    row["links"] = len(listing_links(lst.content.decode("utf-8", "replace"),
                                                    s["listing_url"], s["link_pattern"]))
                elif s["mode"] == "listing":
                    row["links"] = "fill listing_url/link_pattern"
                _ = page
        except Exception as exc:  # noqa: BLE001 - a health check reports, never crashes
            row["http"] = f"{type(exc).__name__}"
        rows.append(row)
    return rows
