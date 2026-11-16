# ruff: noqa: E501
"""Bank problem -> one-page PDF sheet (problem or solution), FR/EN. Art direction in templates/sheet.typ."""
from __future__ import annotations

import json
import random
import shutil
from datetime import UTC, datetime
from pathlib import Path

from . import render

LABELS = {
    "fr": {"no": "N°", "status": "Statut", "source": "Source", "context": "Contexte", "data": "Données",
               "ask": "À déterminer", "form": "Formules utiles", "problem": "Problème", "assump": "Hypothèses",
               "calc": "Calcul", "result": "Résultat", "by": "Réalisé par", "contact": "Contact",
               "finger": "Empreinte de l'édition", "scan": "Scanner : archive et dépôt de solution",
               "kicker_p": "Fiche problème", "kicker_s": "Ma solution", "sector": "Secteur", "region": "Région",
               "level": "Niveau", "real": "Cas public réel", "realistic": "Problème réaliste",
               "note_realistic": "Classe de problèmes typique d'un site industriel. Aucune entreprise n'est "
                              "désignée, aucun besoin d'une entreprise précise n'est affirmé.",
               "note_real": "Cas public documenté. La source ci-dessous fait foi.",
               "nosrc": "— (aucune source : problème réaliste)",
               "honest": "Problème de type réaliste ; non commandé par une entreprise."},
    "en": {"no": "No.", "status": "Status", "source": "Source", "context": "Context", "data": "Given data",
               "ask": "To determine", "form": "Useful formulas", "problem": "Problem", "assump": "Assumptions",
               "calc": "Calculation", "result": "Result", "by": "Prepared by", "contact": "Contact",
               "finger": "Edition fingerprint", "scan": "Scan: archive and solution upload",
               "kicker_p": "Problem sheet", "kicker_s": "My solution", "sector": "Sector", "region": "Region",
               "level": "Level", "real": "Real public case", "realistic": "Realistic problem",
               "note_realistic": "A problem class typical of an industrial site. No company is named and "
                              "no need of a specific company is claimed.",
               "note_real": "Documented public case. The source below is authoritative.",
               "nosrc": "— (no source: realistic problem)",
               "honest": "Realistic problem class; not commissioned by any company."},
}


def fingerprint(seed: str, cols: int = 64, rows: int = 7) -> list[list[int]]:
    rnd = random.Random(seed)
    return [[1 if rnd.random() < 0.04 + 0.96 * ((i + 1) / cols) ** 1.5 else 0 for i in range(cols)]
            for _ in range(rows)]


def build_data(problem: dict, mode: str = "problem", solution: dict | None = None,
               today=None, base_url: str = "https://github.com/omax404/acta-problemata") -> dict:
    lang = problem.get("lang", "fr")
    t = LABELS[lang]
    today = today or datetime.now(UTC).date()
    doy = today.timetuple().tm_yday
    code = (f"AP-{today.year}-{problem.get('id', doy):03d}-MA-{problem['sector_code']}-{problem['level']}"
            + ("-S" if mode == "solution" else ""))
    real = problem["status"] == "real"
    stars = "★" * problem["level"] + "☆" * (3 - problem["level"])
    data = {
        "lang": lang, "t": t, "mode": mode, "code": code, "number": problem.get("id", doy),
        "date": today.strftime("%d/%m/%Y"), "title": problem["title"],
        "mode_label": t["kicker_s"] if mode == "solution" else t["kicker_p"],
        "kicker": f"{t['kicker_s'] if mode == 'solution' else t['kicker_p']} // {t['sector']}: "
                  f"{problem['sector']} // {t['region']}: {problem['region']} // {t['level']}: {stars}",
        "status_label": t["real"] if real else t["realistic"],
        "status_note": t["note_real"] if real else t["note_realistic"],
        "source": problem.get("source_url") or t["nosrc"],
        "context": problem["context"], "data": problem["data"], "questions": problem["questions"],
        "formulas": problem["formulas"], "finger": fingerprint(code), "qr_url": base_url,
    }
    if mode == "solution":
        s = solution or {}
        c = " // ".join(x for x in (s.get("email"), s.get("phone"), s.get("link")) if x)
        data["s"] = {"name": s.get("name", ""), "contact": c, "assumptions": s.get("assumptions", []),
                     "steps": s.get("steps", []), "result": s.get("result", ""),
                     "recommendation": s.get("recommendation", "")}
    return data


def render_sheet(data: dict, repo_root: Path, out_pdf: Path) -> None:
    build = repo_root / "build" / f"sheet-{data['code']}"
    build.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_root / "templates" / "sheet.typ", build / "sheet.typ")
    (build / "sheet.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    render.make_qr(data["qr_url"], build / "qr.svg")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    render._compile(build, out_pdf, "sheet.typ")


def load_problem(repo_root: Path, ref: str) -> dict:
    files = sorted((repo_root / "bank").glob("*.json"))
    if ref == "today":                      # same rotation as pick_edition.py
        return json.loads(files[(datetime.now(UTC).timetuple().tm_yday - 1) % len(files)].read_text(encoding="utf-8"))
    for f in files:
        p = json.loads(f.read_text(encoding="utf-8"))
        if ref in (p["slug"], str(p.get("id"))):
            return p
    have = [json.loads(f.read_text(encoding="utf-8"))["slug"] for f in files]
    raise KeyError(f"no bank problem {ref!r}; have: {have}")