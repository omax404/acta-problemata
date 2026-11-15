#!/usr/bin/env python3
"""Build a provenance-labelled daily problem and browsable static archive.

The current vault contains illustrative scenarios, so editions are always labelled
"realistic problem" and never imply that a named company has this problem.
Uses only the Python standard library.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
ARCHIVE = DOCS / "archive"
TEXT = {
    "fr": {
        "kind": "Fiche problème", "status": "Problème réaliste", "sector": "Secteur",
        "region": "Région", "level": "Niveau", "context": "Contexte",
        "data": "Données", "question": "À déterminer", "formula": "Formule utile",
        "solution": "Ma solution", "assumptions": "Hypothèses", "calculation": "Calcul",
        "result": "Résultat et recommandation", "figure": "Schéma", "contact": "Nom et contact",
        "source": "Source", "no_source": "Aucune source externe : scénario réaliste, non attribué à une entreprise.",
        "notice": "Exercice réaliste destiné à l’apprentissage. Ce document ne décrit pas un besoin confirmé d’une entreprise.",
        "archive": "Archive des éditions", "filter": "Filtrer par secteur", "all": "Tous les secteurs",
        "region_unknown": "Non précisée", "footer": "Acta Problemata · problème réaliste, non attribué à une entreprise.",
    },
    "en": {
        "kind": "Problem sheet", "status": "Realistic problem", "sector": "Sector",
        "region": "Region", "level": "Difficulty", "context": "Context",
        "data": "Given data", "question": "To determine", "formula": "Useful formula",
        "solution": "My solution", "assumptions": "Assumptions", "calculation": "Calculation",
        "result": "Result and recommendation", "figure": "Diagram", "contact": "Name and contact",
        "source": "Source", "no_source": "No external source: realistic scenario, not attributed to a company.",
        "notice": "Realistic learning exercise. This document does not describe a confirmed company need.",
        "archive": "Edition archive", "filter": "Filter by sector", "all": "All sectors",
        "region_unknown": "Unspecified", "footer": "Acta Problemata · realistic problem, not attributed to a company.",
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_case(today: dt.date, language: str) -> tuple[dict, str]:
    entries = json.loads((ROOT / "data" / "case_vault.json").read_text(encoding="utf-8"))
    if not entries:
        raise ValueError("case_vault.json contains no cases")
    entry = entries[today.toordinal() % len(entries)]
    case = entry["case"]
    lang = language if language in TEXT else "fr"
    labels = TEXT[lang]
    edition = {
        "date": today.isoformat(),
        "code": f"AP-{today.year}-{today.timetuple().tm_yday:03d}-{re.sub(r'[^A-Z0-9]+', '-', str(case.get('domain', 'GEN').upper()).replace('É', 'E')).strip('-')[:8]}",
        "title": case["title"],
        "sector": case.get("domain", "General engineering"),
        "region": labels["region_unknown"],
        "difficulty": "Intermediate",
        "status": "realistic",
        "source_url": "",
        "context": case["narrative"],
        "data": [[item["name"], item["value"]] for item in case.get("boundary_conditions", [])],
        "question": case["challenge_question"],
        "formula": case.get("formula", {}).get("symbolic", ""),
        "language": lang,
        "labels": labels,
    }
    return edition, entry["id"]


def diagram_svg() -> str:
    return ('<svg viewBox="0 0 640 120" role="img" aria-label="Engineering system schematic" '
            'xmlns="http://www.w3.org/2000/svg"><path d="M35 60h155l55-35 70 70 55-35h235" '
            'fill="none" stroke="#e8500c" stroke-width="4"/><circle cx="245" cy="60" r="24" '
            'fill="#f4f0e9" stroke="#151515" stroke-width="3"/><path d="M235 74l24-14-24-14z" '
            'fill="#e8500c"/><path d="M35 40v40m570-40v40" stroke="#151515" stroke-width="3"/></svg>')


def render_problem(edition: dict, case_id: str) -> str:
    t = edition["labels"]
    data_rows = "".join(f"<tr><th>{esc(name)}</th><td>{esc(value)}</td></tr>" for name, value in edition["data"])
    source = (f'<a href="{esc(edition["source_url"])}" rel="noopener">{esc(edition["source_url"])}</a>'
              if edition["source_url"] else esc(t["no_source"]))
    formula = f'<pre>{esc(edition["formula"])}</pre>' if edition["formula"] else ""
    fields = "".join(f'<section class="write"><h2>{esc(t[label])}</h2><div></div></section>'
                      for label in ("assumptions", "calculation", "result", "contact"))
    return f'''<!doctype html><html lang="{esc(edition['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(edition['code'])} · {esc(edition['title'])}</title>
<style>
:root{{--ink:#151515;--orange:#e8500c;--paper:#f4f0e9}}*{{box-sizing:border-box}}body{{margin:0;background:#dcd7cf;color:var(--ink);font:16px/1.55 Inter,Arial,sans-serif}}main{{max-width:850px;margin:28px auto;padding:36px;background:var(--paper);border-left:6px solid var(--orange);box-shadow:0 6px 24px #0002}}header{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid;padding-bottom:18px}}.brand{{font-weight:800;letter-spacing:.12em;color:var(--orange)}}.seal{{font-size:12px;text-transform:uppercase;letter-spacing:.1em}}h1{{font-size:clamp(25px,5vw,40px);line-height:1.12;text-transform:uppercase;margin:25px 0 10px}}.meta{{font:12px monospace;text-transform:uppercase;letter-spacing:.08em}}.status{{margin:20px 0;padding:14px;background:var(--orange);font-weight:700}}section{{margin:24px 0}}h2{{font:700 13px monospace;text-transform:uppercase;border-bottom:1px solid;padding-bottom:5px}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:7px;border-bottom:1px solid #ccc}}th{{width:45%}}pre{{white-space:pre-wrap;background:#e7e2da;padding:12px;border-left:3px solid var(--orange)}}.diagram svg{{width:100%;height:auto}}.write div{{height:100px;border-bottom:1px solid #bbb}}.write:last-child div{{height:42px}}a{{color:inherit}}footer{{border-top:1px solid;padding-top:12px;font:11px monospace}}@media print{{body{{background:white}}main{{margin:0 auto;box-shadow:none;padding:20mm;border:0}}.write div{{height:72px}}}}
</style></head><body><main><header><span class="brand">ACTA PROBLEMATA</span><span class="seal">{esc(t['kind'])} · {esc(edition['code'])}</span></header>
<div class="meta">{esc(t['sector'])}: {esc(edition['sector'])} · {esc(t['region'])}: {esc(edition['region'])} · {esc(t['level'])}: {esc(edition['difficulty'])}</div><h1>{esc(edition['title'])}</h1>
<div class="status">{esc(t['status'])}<br><small>{esc(t['notice'])}</small></div><section><h2>{esc(t['context'])}</h2><p>{esc(edition['context'])}</p></section>
<section><h2>{esc(t['data'])}</h2><table>{data_rows}</table></section><section><h2>{esc(t['question'])}</h2><p>{esc(edition['question'])}</p>{formula}</section>
<section class="diagram"><h2>{esc(t['figure'])}</h2>{diagram_svg()}</section><section><h2>{esc(t['solution'])}</h2>{fields}</section>
<section><h2>{esc(t['source'])}</h2><p>{source}</p></section><footer>{esc(t['footer'])} · {esc(case_id)} · {esc(edition['date'])}</footer></main></body></html>'''


def update_index() -> None:
    pages = sorted(ARCHIVE.glob("edition-*.html"), reverse=True)
    entries = []
    for path in pages:
        match = re.match(r"edition-(\d{4}-\d{3})-(.+)\.html", path.name)
        title = path.stem.replace("edition-", "").replace("-", " · ")
        entries.append(f'<li data-sector="{esc(match.group(2) if match else "")}"><a href="archive/{esc(path.name)}">{esc(title)}</a></li>')
    sectors = sorted({re.search(r"edition-\d{4}-\d{3}-(.+)\.html", p.name).group(1)
                      for p in pages if re.search(r"edition-\d{4}-\d{3}-(.+)\.html", p.name)})
    options = ''.join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in sectors)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(f'''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Acta Problemata — Archive</title><style>body{{max-width:900px;margin:40px auto;padding:20px;background:#f4f0e9;color:#151515;font:17px/1.5 Arial}}h1{{color:#e8500c}}li{{margin:12px 0}}a{{color:inherit}}select{{padding:8px}}</style><h1>Acta Problemata</h1><p>Problèmes d’ingénierie réalistes pour l’apprentissage. Les éditions ne sont pas présentées comme des besoins confirmés d’entreprises.</p><label>Filtrer par secteur <select id="sector"><option value="">Tous</option>{options}</select></label><ul id="editions">{''.join(entries)}</ul><script>document.getElementById('sector').onchange=e=>document.querySelectorAll('#editions li').forEach(x=>x.hidden=!!e.target.value&&x.dataset.sector!==e.target.value)</script></html>''', encoding="utf-8")


def main() -> None:
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    language = config.get("language", "fr")
    today = dt.datetime.now(dt.timezone.utc).date()
    edition, case_id = load_case(today, language)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9-]+", "-", edition["sector"].lower()).strip("-")[:24] or "general"
    out = ARCHIVE / f"edition-{today.year}-{today.timetuple().tm_yday:03d}-{slug}.html"
    out.write_text(render_problem(edition, case_id), encoding="utf-8")
    update_index()
    print(f"Built {out.relative_to(ROOT)} ({edition['status']}; {edition['language']})")


if __name__ == "__main__":
    main()
