"""On-demand edition: someone gives a link + an email, the program mails back a PDF.

Nothing here touches the ledger, the archive or the public pages: a request is private.
Guards: public http(s) hosts only (no SSRF), robots.txt honoured, one valid address,
company names anonymised, the answer still comes from the SymPy guard (never the LLM).
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import logging
import re
import socket
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from . import deliver, originality, render, sources, synthesize
from . import ledger as L
from .diagrams import render_diagram
from .math_guard import MathGuardError, verify_formula

log = logging.getLogger("acta.request")
EMAIL_RX = re.compile(r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,}$")
DOMAINS = ("Mechanical", "Thermodynamics", "Fluids", "Materials", "Electrical", "Civil")


class RequestError(ValueError):
    """The request is refused or cannot be turned into a verified problem."""


def valid_email(addr: str) -> bool:
    return bool(EMAIL_RX.match(addr)) and "\n" not in addr and "\r" not in addr


def public_http_url(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
        return False
    try:
        infos = socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == "https" else 80))
    except OSError:
        return False
    return all(ipaddress.ip_address(i[4][0]).is_global for i in infos)


def build_request(root: Path, url: str, email: str, domain: str | None = None,
                  send: bool = True) -> dict:
    if not valid_email(email):
        raise RequestError("invalid email address")
    if not public_http_url(url):
        raise RequestError("the link must be a public http(s) page")
    cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    domain = domain if domain in DOMAINS else cfg["target_domain"]
    try:
        got = sources.polite_get(url, root / "build" / "cache")
        title, text = sources.extract_text(got.content, got.content_type)
    except sources.FetchBlocked as exc:
        raise RequestError(f"the site does not allow automated reading ({exc})") from exc
    except Exception as exc:  # noqa: BLE001 - any fetch failure is a refusal, not a crash
        raise RequestError(f"could not read the page: {exc}") from exc
    if len(text) < sources.MIN_TEXT:
        raise RequestError("the page has too little readable text to build a problem from")
    try:
        case = synthesize.synthesize(text, domain, cfg["difficulty_level"], cfg.get("llm", {}),
                                     deadline=time.monotonic() + 35, anonymize=True)
        originality.check_original(text, case)
        vf = verify_formula(case.formula.symbolic,
                            {v.symbol: v.value for v in case.formula.variables}, case.formula.unit)
    except (synthesize.SynthesisError, originality.NotOriginalError, MathGuardError, ValueError) as exc:
        raise RequestError(f"could not build a verified problem from this page ({exc})") from exc

    today = datetime.now(UTC).date()
    led = L.load(root / "data" / "ledger.json")
    rid = hashlib.sha1(f"{url}|{email}|{time.time()}".encode()).hexdigest()[:8]
    base = cfg.get("pages_base_url") or "https://github.com/omax404/acta-problemata"
    edition = {
        "edition_number": led.get("edition_number", 0) + 1, "date": today.isoformat(),
        "date_display": today.strftime("%d %B %Y"), "domain": case.domain.value,
        "difficulty": cfg["difficulty_level"], "headline": case.title, "narrative": case.narrative,
        "boundary_conditions": {b.name: b.value for b in case.boundary_conditions},
        "formula": {"symbolic": vf.symbolic, "variables": vf.variables,
                    "computed_result": vf.computed_result,
                    "result_display": render.display_result(vf.computed_result), "unit": vf.unit},
        "challenge_question": case.challenge_question, "reveal_answer": False,
        "diagram_caption": case.diagram.caption,
        "source_line": f"Adapted from a public page ({urlparse(url).netloc}); company details omitted.",
        "source_url": url, "repo_slug": "omax404/acta-problemata", "solution_url": base,
    }
    out = root / "build" / "requests"
    out.mkdir(parents=True, exist_ok=True)
    svg = render_diagram(case.diagram.kind, {p.symbol: p.value for p in case.diagram.params},
                         out / f"{rid}.svg")
    pdf = out / f"acta-request-{rid}.pdf"
    fit = render.render_edition(edition, svg, base, root, pdf)
    sent = False
    if send:
        sent = deliver.send_email(pdf, edition, to=email, answer=vf.computed_result, unit=vf.unit)
    return {"request": rid, "pdf": str(pdf), "pages": fit["pages"], "emailed": sent,
            "headline": case.title}