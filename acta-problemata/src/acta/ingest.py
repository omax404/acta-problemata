"""FR-01: NTRS + arXiv ingestion with 10 s timeouts and ledger dedupe."""
from __future__ import annotations

import hashlib
import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import requests

from . import ledger as L
from . import sources as S

log = logging.getLogger("acta.ingest")
TIMEOUT = 10  # FR-01.2
NTRS_URL = "https://ntrs.nasa.gov/api/citations/search"
ARXIV_URL = "https://export.arxiv.org/api/query"
UA = {"User-Agent": "acta-problemata/1.0 (open-source daily engineering broadside)"}

DOMAIN_TERMS = {
    "Mechanical": "fatigue failure beam", "Aerospace": "structural failure aircraft",
    "Electrical": "power electronics failure", "Chemical": "pressure vessel corrosion",
    "Civil": "buckling structural collapse", "Thermal": "heat exchanger thermal stress",
    "Materials": "fracture crack failure", "Fluids": "pipe friction head loss",
}


@dataclass
class SourceDoc:
    case_id: str
    title: str
    text: str
    origin: str          # ntrs | arxiv | market | inbox | web
    domain: str | None = None     # overrides config target_domain when known
    url: str = ""                 # public source URL (shown on the solution page only)


def _pick(cands: list[SourceDoc], today: date) -> SourceDoc:
    return cands[today.toordinal() % len(cands)]   # deterministic per day


def _ntrs(domain: str, led: dict, today: date) -> list[SourceDoc]:
    r = requests.get(NTRS_URL, params={"q": DOMAIN_TERMS.get(domain, "engineering failure"),
                                       "page.size": 25}, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    out = []
    for it in r.json().get("results", []):
        cid, abstract = f"ntrs:{it.get('id')}", (it.get("abstract") or "").strip()
        if it.get("id") and len(abstract) > 300 and not L.is_seen(led, cid, today):
            out.append(SourceDoc(cid, it.get("title", ""), f"{it.get('title','')}\n\n{abstract}", "ntrs"))
    return out


def _arxiv(led: dict, today: date) -> list[SourceDoc]:
    r = requests.get(ARXIV_URL, params={
        "search_query": "cat:eess.SY OR cat:physics.app-ph",
        "sortBy": "submittedDate", "sortOrder": "descending", "max_results": 25,
    }, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(r.text).findall("a:entry", ns):
        raw_id = (e.findtext("a:id", "", ns) or "").rsplit("/", 1)[-1]
        cid = f"arxiv:{raw_id.split('v')[0]}"
        summary = " ".join((e.findtext("a:summary", "", ns) or "").split())
        title = " ".join((e.findtext("a:title", "", ns) or "").split())
        if raw_id and len(summary) > 300 and not L.is_seen(led, cid, today):
            out.append(SourceDoc(cid, title, f"{title}\n\n{summary}", "arxiv"))
    return out


def _market(domain: str, led: dict, today: date, repo_root: Path | None) -> list[SourceDoc]:
    """Curated industrial-maintenance briefs modelled on CPS/tender categories
    (usinage, chaudronnerie, tuyauterie...). Offline, so it never fails."""
    root = repo_root or Path(__file__).resolve().parents[2]
    f = root / "data" / "market_briefs.json"
    if not f.exists():
        return []
    items = json.loads(f.read_text(encoding="utf-8"))
    ranked = sorted(items, key=lambda b: b.get("domain") != domain)   # domain matches first
    return [SourceDoc(f"market:{b['id']}", b["category"], f"{b['category']}\n\n{b['text']}", "market")
            for b in ranked if not L.is_seen(led, f"market:{b['id']}", today)
            and (b.get("domain") == domain or not any(x.get("domain") == domain for x in items))]


_DOMAINS = ("Mechanical", "Aerospace", "Electrical", "Chemical", "Civil", "Thermal", "Materials", "Fluids")


def _domain_prefix(name: str) -> str | None:
    head = name.split("__", 1)[0]
    return head if "__" in name and head in _DOMAINS else None


def _inbox(led: dict, today: date, repo_root: Path | None) -> list[SourceDoc]:
    """FIFO queue of human-curated real problems: files first, then URLs. One item per call."""
    root = (repo_root or Path(__file__).resolve().parents[2]) / "inbox"
    if not root.is_dir():
        return []
    for f in sorted(root.iterdir()):
        if f.suffix.lower() not in (".txt", ".md", ".pdf") or f.name in ("README.md", "urls.txt") \
                or f.name.startswith(("_", ".")):
            continue
        cid = f"inbox:{f.stem}"
        if L.is_seen(led, cid, today):
            continue
        ctype = "application/pdf" if f.suffix.lower() == ".pdf" else "text/plain"
        title, text = S.extract_text(f.read_bytes(), ctype)
        if len(text) >= S.MIN_TEXT:
            return [SourceDoc(cid, title or f.stem, text, "inbox", _domain_prefix(f.stem))]
        log.warning("inbox: %s too short (%d chars) - skipped", f.name, len(text))
    urls = root / "urls.txt"
    if urls.exists():
        for line in urls.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip() if line.lstrip().startswith("#") else line.strip()
            if not line:
                continue
            url, _, hint = (p.strip() for p in line.partition("|"))
            cid = "inbox:url-" + hashlib.sha1(url.encode()).hexdigest()[:10]
            if L.is_seen(led, cid, today):
                continue
            try:
                got = S.polite_get(url, cache_dir=(repo_root or root.parent) / "build" / "cache")
                title, text = S.extract_text(got.content, got.content_type)
            except Exception as exc:  # noqa: BLE001 - one bad URL must not block the queue
                log.warning("inbox: %s failed (%s) - skipped", url, exc)
                continue
            if len(text) >= S.MIN_TEXT:
                return [SourceDoc(cid, title or url, text, "inbox", hint if hint in _DOMAINS else None, url)]
            log.warning("inbox: %s has too little text - skipped", url)
    return []


def _listing(led: dict, today: date, repo_root: Path | None) -> list[SourceDoc]:
    """Registry entries with mode=listing AND enabled=true: follow links matching link_pattern."""
    root = repo_root or Path(__file__).resolve().parents[2]
    for s in S.load_registry(root):
        if not (s["enabled"] and s["mode"] == "listing" and s.get("listing_url") and s.get("link_pattern")):
            continue
        cache = root / "build" / "cache"
        try:
            lst = S.polite_get(s["listing_url"], cache_dir=cache)
            html = lst.content.decode("utf-8", "replace")
            links = S.listing_links(html, s["listing_url"], s["link_pattern"])
        except Exception as exc:  # noqa: BLE001
            log.warning("listing %s failed (%s)", s["id"], exc)
            continue
        for url in links:
            cid = f"web:{s['id']}:" + hashlib.sha1(url.encode()).hexdigest()[:10]
            if L.is_seen(led, cid, today):
                continue
            try:
                got = S.polite_get(url, cache_dir=cache)
                title, text = S.extract_text(got.content, got.content_type)
            except Exception as exc:  # noqa: BLE001
                log.warning("listing %s: %s failed (%s)", s["id"], url, exc)
                continue
            if len(text) >= S.MIN_TEXT:
                return [SourceDoc(cid, title or url, text, "web", s.get("domain_hint"), url)]
    return []


def fetch_source(domain: str, led: dict, today: date, repo_root: Path | None = None,
                 order: list[str] | None = None) -> SourceDoc | None:
    registry = {"inbox": lambda: _inbox(led, today, repo_root),
                "listing": lambda: _listing(led, today, repo_root),
                "market": lambda: _market(domain, led, today, repo_root),
                "ntrs": lambda: _ntrs(domain, led, today),
                "arxiv": lambda: _arxiv(led, today)}
    names = order or ["inbox", "listing", "market", "ntrs", "arxiv"]
    for name, fn in [(k, registry[k]) for k in names if k in registry]:
        try:
            cands = fn()
            if cands:
                src = _pick(cands, today)
                log.info("ingest: %s -> %s", name, src.case_id)
                return src
            log.warning("ingest: %s returned no fresh candidates", name)
        except Exception as exc:  # noqa: BLE001 - any source failure must fall through
            log.warning("ingest: %s failed (%s) — falling through", name, exc)
    return None
