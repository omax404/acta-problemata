# ruff: noqa: E501
"""Leaderboard + streaks from VERIFIED solutions only (data/solutions.json -> docs/leaderboard.html).

Privacy: an entry holds a public handle (pseudonym, optional), the problem slug, its sector and a date.
Never a real name, e-mail, phone or link. Handles that look like an e-mail or URL are dropped to "anonymous".
Honesty: only solutions that earned the math_guard VERIFIED stamp are recorded.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

FILE = Path("data") / "solutions.json"
OUT = Path("docs") / "leaderboard.html"
ANON = ""                                           # stored as "" ; rendered as "Anonyme / Anonymous"
_BAD = re.compile(r"[@/\\<>]|https?:|www\.", re.I)
_CTRL = re.compile(r"[\x00-\x1f\x7f]")


def clean_handle(raw: object) -> str:
    """Public handle: <=24 chars, no control chars; e-mail- or URL-looking values become anonymous."""
    h = _CTRL.sub("", str(raw or "")).strip()
    return ANON if not h or _BAD.search(h) else h[:24]


def load(root: Path) -> list[dict]:
    f = root / FILE
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def record(root: Path, problem: dict, sol: dict, today: date | None = None) -> dict:
    """Append one verified solution. Caller must have checked the verdict. Returns the stored entry."""
    entry = {"handle": clean_handle(sol.get("handle")), "problem": problem["slug"],
             "domain": problem.get("sector", ""), "date": (today or datetime.now(UTC).date()).isoformat()}
    rows = load(root)
    if entry["handle"] and any(r["handle"] == entry["handle"] and r["problem"] == entry["problem"] for r in rows):
        return entry                                  # a named solver counts once per problem
    rows.append(entry)
    (root / FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / FILE).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return entry


def streaks(days: set[date], today: date) -> tuple[int, int]:
    """(current, best) run of consecutive days. Current counts if the last day is today or yesterday."""
    if not days:
        return 0, 0
    ordered = sorted(days)
    best = run = 1
    for a, b in zip(ordered, ordered[1:], strict=False):
        run = run + 1 if (b - a).days == 1 else 1
        best = max(best, run)
    cur = 0
    if (today - ordered[-1]).days <= 1:
        cur, d = 1, ordered[-1]
        while d - timedelta(days=1) in days:
            d -= timedelta(days=1)
            cur += 1
    return cur, best


def stats(rows: list[dict], today: date | None = None) -> dict:
    today = today or datetime.now(UTC).date()
    per_handle: dict[str, dict] = {}
    for r in rows:
        if not r.get("handle"):
            continue
        h = per_handle.setdefault(r["handle"], {"days": set(), "problems": set()})
        h["days"].add(date.fromisoformat(r["date"]))
        h["problems"].add(r["problem"])
    board = []
    for name, h in per_handle.items():
        cur, best = streaks(h["days"], today)
        board.append({"handle": name, "solved": len(h["problems"]), "current": cur, "best": best})
    board.sort(key=lambda x: (-x["solved"], -x["best"], x["handle"].lower()))
    return {"total": len(rows), "solvers": len(per_handle),
            "by_problem": Counter(r["problem"] for r in rows).most_common(),
            "by_domain": Counter(r["domain"] or "—" for r in rows).most_common(), "board": board}


_CSS = """:root{--p:#DCD7CF;--s:#E6E1D8;--k:#121212;--m:#6E6B65;--o:#E8500C}
*{box-sizing:border-box}body{margin:0;background:var(--p);color:var(--k);font:15px/1.5 system-ui,sans-serif;padding:32px 16px}
main{max-width:860px;margin:0 auto;background:var(--s);border:2px solid var(--k);border-left:6px solid var(--o);
padding:28px;box-shadow:4px 4px 0 var(--k)}
.tag{font:700 12px ui-monospace,Menlo,monospace;color:var(--o);letter-spacing:.08em;text-transform:uppercase}
h1{margin:6px 0 4px;font-size:26px;text-transform:uppercase}h2{font-size:14px;letter-spacing:.06em;text-transform:uppercase;
border-bottom:2px solid var(--k);padding-bottom:4px;margin-top:28px}
.kpi{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}.kpi div{background:#fff;border:1px solid var(--k);padding:10px 16px}
.kpi b{display:block;font:700 26px ui-monospace,Menlo,monospace;color:var(--o)}
table{border-collapse:collapse;width:100%;background:#fff}td,th{border:1px solid #c9c4ba;padding:6px 10px;text-align:left}
th{background:var(--k);color:#fff;font:700 12px ui-monospace,Menlo,monospace;text-transform:uppercase}
td.n{text-align:right;font-family:ui-monospace,Menlo,monospace}.muted{color:var(--m);font-size:13px}
a{color:var(--o)}"""


def render_html(rows: list[dict], today: date | None = None) -> str:
    s, e = stats(rows, today), html.escape

    def table(head: tuple[str, ...], body: list[tuple]) -> str:
        if not body:
            return '<p class="muted">Aucune solution vérifiée pour le moment · No verified solution yet.</p>'
        th = "".join(f"<th>{e(h)}</th>" for h in head)
        tr = "".join("<tr>" + "".join(f'<td class="{"n" if isinstance(c, int) else ""}">{e(str(c))}</td>'
                                      for c in r) + "</tr>" for r in body)
        return f"<table><tr>{th}</tr>{tr}</table>"

    board = [(i + 1, b["handle"], b["solved"], b["current"], b["best"]) for i, b in enumerate(s["board"])]
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acta Problemata · Classement</title><link rel="icon" type="image/png" href="assets/logo.png">
<style>{_CSS}</style></head><body><main>
<span class="tag">Acta Problemata // Classement · Leaderboard</span>
<h1>Solutions vérifiées</h1>
<p class="muted">Seules les solutions ayant obtenu le tampon <b>VERIFIED by math_guard</b> comptent. Pseudonymes
autorisés ; aucun e-mail ni nom réel n'est publié. · Only math_guard-verified solutions count; pseudonyms allowed;
no e-mails or real names are published.</p>
<div class="kpi"><div><b>{s['total']}</b>solutions</div><div><b>{s['solvers']}</b>ingénieurs nommés</div></div>
<h2>Classement · Streaks</h2>
{table(("#", "Pseudo", "Problèmes", "Série en cours (j)", "Meilleure série (j)"), board)}
<h2>Par problème · Per problem</h2>
{table(("Problème", "Solutions"), s["by_problem"])}
<h2>Par domaine · Per domain</h2>
{table(("Domaine / secteur", "Solutions"), s["by_domain"])}
<p class="muted">Série = jours consécutifs avec au moins une solution vérifiée (en cours si la dernière date est
aujourd'hui ou hier). Les solutions anonymes comptent dans les totaux mais pas dans les séries.
<a href="index.html">← Accueil</a> · <a href="submit-solution.html">Déposer ma solution</a></p>
</main></body></html>
"""


def build(root: Path, today: date | None = None) -> Path:
    out = root / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(load(root), today), encoding="utf-8")
    return out
