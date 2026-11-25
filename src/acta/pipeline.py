"""Orchestration: fetch -> synthesize -> guard -> diagram -> render -> deliver.

Fallback order: live source + LLM -> Gemini ideation -> bank (committed problems)
-> vault (last resort). Ideation keeps the daily edition fresh even when every
scraper fails, as long as an LLM key is configured.
Each stage is a small function; `run` only sequences them and owns the timings.
Publication never depends on delivery: a broken SMTP/printer is reported, not fatal.
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import urlparse

from . import (
    deliver,
    ingest,
    legibility,
    originality,
    pages,
    readme_widget,
    render,
    rotation,
    style,
    synthesize,
    video,
)
from . import ledger as L
from .diagrams import render_diagram
from .math_guard import MathGuardError, VerifiedFormula, verify_formula
from .schemas import DOMAINS, LLMCase

log = logging.getLogger("acta")
NFR_BUDGET_S = 45
SYNTH_DEADLINE_S = 35


@dataclass
class Content:
    case: LLMCase
    case_id: str
    origin: str          # vault | bank | gemini | market | inbox | web | ntrs | arxiv
    source_url: str = ""


def _vars(case: LLMCase) -> dict[str, float]:
    return {v.symbol: v.value for v in case.formula.variables}


def _verify(case: LLMCase) -> VerifiedFormula:
    return verify_formula(case.formula.symbolic, _vars(case), case.formula.unit)


def _bank_content(repo_root: Path, led: dict, today: date) -> Content:
    bank_path = repo_root / "data" / "bank_cases.json"
    if not bank_path.exists():
        return _vault_content(repo_root, led, today)
    entries = json.loads(bank_path.read_text(encoding="utf-8"))
    fresh = [e for e in entries if not L.is_seen(led, e["id"], today)]
    pool = fresh or sorted(entries, key=lambda e: led["seen"].get(e["id"], "0000"))
    for e in pool:
        try:
            case = LLMCase.model_validate(e["case"])
            _verify(case)
            return Content(case, e["id"], "bank")
        except ValueError as exc:
            log.warning("bank entry %s invalid (%s)", e.get("id"), exc)
    return _vault_content(repo_root, led, today)


def _vault_content(repo_root: Path, led: dict, today: date) -> Content:
    entries = json.loads((repo_root / "data" / "case_vault.json").read_text(encoding="utf-8"))
    fresh = [e for e in entries if not L.is_seen(led, e["id"], today)]
    pool = fresh or sorted(entries, key=lambda e: led["seen"].get(e["id"], "0000"))
    errors = []
    for e in pool:
        try:
            case = LLMCase.model_validate(e["case"])
            _verify(case)
            return Content(case, e["id"], "vault")
        except ValueError as exc:                       # pydantic + MathGuardError are ValueErrors
            errors.append(f"{e['id']}: {exc}")
    raise RuntimeError(f"vault exhausted or corrupt: {errors}")


def _target_domain(cfg: dict, today: date) -> str:
    """Domain of the day: rotates through the 8 domains unless pinned in config."""
    if not cfg.get("rotate_domains"):
        return cfg["target_domain"]
    return DOMAINS[today.toordinal() % len(DOMAINS)]


def _ideation_content(cfg: dict, today: date) -> Content | None:
    """Gemini invents a fresh problem when the live sources yield nothing usable.
    Honesty: 'gemini' sheets are always 'realistic problem' class (no companies named)."""
    llm_cfg = cfg.get("llm", {})
    if not llm_cfg.get("ideation", True):
        return None
    domain = _target_domain(cfg, today)
    try:
        case = synthesize.synthesize_ideation(domain, cfg["difficulty_level"], llm_cfg, today,
                                              deadline=time.monotonic() + SYNTH_DEADLINE_S)
        log.info("gemini ideation produced a fresh %s case", domain)
        return Content(case, f"gemini:{domain.lower()}:{today.isoformat()}", "gemini")
    except synthesize.SynthesisError as exc:
        log.warning("gemini ideation failed -> bank: %s", exc)
        return None


def acquire_content(repo_root: Path, cfg: dict, led: dict, today: date,
                    force_vault: bool) -> tuple[Content, list[str]]:
    """Live source + LLM when possible, then Gemini ideation, then the bank (then vault).
    Returns the content plus notes about what failed on the way (surfaced in summary.json)."""
    notes: list[str] = []
    if not force_vault:
        domain = _target_domain(cfg, today)
        rcfg = rotation.load_cfg(cfg=cfg)
        ok = rotation.csb_allowed(led["history"], today, rcfg)
        skip = frozenset() if ok else frozenset({rotation.CSB_SOURCE_ID})
        src = ingest.fetch_source(domain, led, today, repo_root, cfg.get("source_order"), skip)
        if src:
            try:
                case = synthesize.synthesize(src.text, src.domain or domain,
                                             cfg["difficulty_level"], cfg.get("llm", {}),
                                             deadline=time.monotonic() + SYNTH_DEADLINE_S,
                                             anonymize=not cfg.get("name_companies", False))
                originality.check_original(src.text, case)     # rewritten, never copied
                return Content(case, src.case_id, src.origin, src.url), notes
            except synthesize.SynthesisError as exc:
                notes.append(f"live synthesis: {exc}")
                log.warning("synthesis failed -> ideation/bank: %s", exc)
            except originality.NotOriginalError as exc:
                notes.append(f"originality: {src.case_id}: {exc}")
                log.warning("originality guard rejected %s (%s) -> ideation/bank", src.case_id, exc)
        idea = _ideation_content(cfg, today)
        if idea:
            return idea, notes
        return _bank_content(repo_root, led, today), notes
    return _vault_content(repo_root, led, today), notes


def verified_content(content: Content, repo_root: Path, led: dict,
                     today: date) -> tuple[Content, VerifiedFormula]:
    """FR-03: recompute deterministically; a rejected live case falls back through bank -> vault."""
    try:
        return content, _verify(content.case)
    except MathGuardError as exc:
        log.warning("math guard rejected %s case (%s) -> bank/vault fallback", content.origin, exc)
        fallback = _bank_content(repo_root, led, today)
        return fallback, _verify(fallback.case)


_SOURCE_LINES: dict[str, str] = {
    "ntrs":   "Source: NASA NTRS {tail} (public domain).",
    "arxiv":  "Source: arXiv {tail} (abstract adapted).",
    "market": "Scenario class: industrial maintenance brief ({tail}); figures illustrative.",
    "ntsb":   "Source: NTSB hazmat investigation {tail} (public domain).",
    "inbox":  "Adapted from a public document ({host}); company details omitted.",
    "web":    "Adapted from a public page ({host}); company details omitted.",
    "gemini": "Scenario class: original AI-composed industrial problem ({case_id}); figures illustrative.",
    "bank":   "Source: Acta Problemata problem bank ({case_id}).",
    "vault":  "Source: Acta Problemata vault, case {case_id}.",
}


def source_line(origin: str, case_id: str, url: str = "") -> str:
    tail = case_id.split(":", 1)[-1]
    host = urlparse(url).netloc or "the inbox"
    tmpl = _SOURCE_LINES.get(origin, "Source: {case_id}.")
    return tmpl.format(tail=tail, host=host, case_id=case_id)


def build_edition(content: Content, vf: VerifiedFormula, cfg: dict, *, edition_no: int,
                  today: date, repo_slug: str, solution_url: str) -> dict:
    case = content.case
    return {
        "edition_number": edition_no,
        "date": today.isoformat(),
        "date_display": today.strftime("%d %B %Y"),
        "domain": case.domain.value,
        "accent": style.accent_for(case.domain.value),
        "difficulty": cfg["difficulty_level"],
        "headline": case.title,
        "narrative": case.narrative,
        "boundary_conditions": {b.name: b.value for b in case.boundary_conditions},
        "formula": {"symbolic": vf.symbolic, "variables": vf.variables,
                    "computed_result": vf.computed_result,
                    "result_display": render.display_result(vf.computed_result),
                    "unit": vf.unit},
        "challenge_question": case.challenge_question,
        "reveal_answer": bool(cfg.get("reveal_answer", False)),
        "diagram_caption": case.diagram.caption,
        "source_line": source_line(content.origin, content.case_id, content.source_url),
        "source_url": content.source_url,
        "repo_slug": repo_slug,
        "solution_url": solution_url,
    }


def publish(repo_root: Path, led: dict, today: date, content: Content, edition: dict,
            vf: VerifiedFormula, pdf: Path, repo_slug: str, media: dict | None = None) -> list[str]:
    """Record + pages + README, then best-effort delivery. Returns delivery errors."""
    n = edition["edition_number"]
    entry = {"edition": n, "date": today.isoformat(), "id": content.case_id,
             "domain": content.case.domain.value, "headline": content.case.title,
             "pdf": f"docs/gazette/archive/{pdf.name}", "solution": f"solutions/edition-{n:04d}.html"}
    L.record_success(led, today, content.case_id, entry)
    pages.write_solution_pages(repo_root, edition, vf, led)
    L.save(repo_root / "data" / "ledger.json", led)          # persisted BEFORE delivery
    readme_widget.update_readme(repo_root, led, today, repo_slug)
    errors = []
    for name, send in (("email", lambda: deliver.send_email(pdf, edition, media=media)),
                       ("printer", lambda: deliver.send_printer(pdf))):
        try:
            send()
        except Exception as exc:  # noqa: BLE001 - delivery must never cost us the edition
            log.error("delivery via %s failed: %s", name, exc)
            errors.append(f"{name}: {exc}")
    return errors


def _solution_url(cfg: dict, repo_slug: str, edition_no: int) -> str:
    owner, _, name = repo_slug.partition("/")
    base = (cfg.get("pages_base_url") or os.environ.get("PAGES_BASE_URL")
            or f"https://{owner}.github.io/{name}").rstrip("/")
    return f"{base}/solutions/edition-{edition_no:04d}.html"


def run(repo_root: Path, dry_run: bool = False, force_vault: bool = False) -> dict:
    t0 = time.perf_counter()
    cfg = json.loads((repo_root / "config.json").read_text(encoding="utf-8"))
    today = datetime.now(UTC).date()
    led = L.load(repo_root / "data" / "ledger.json")
    edition_no = L.next_edition(led, today)
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "your-name/acta-problemata")
    solution_url = _solution_url(cfg, repo_slug, edition_no)
    timings: dict[str, float] = {}

    def timed(name: str, fn, *args, **kw):
        t = time.perf_counter()
        out = fn(*args, **kw)
        timings[name] = round(time.perf_counter() - t, 2)
        return out

    content, synth_notes = timed("content", acquire_content, repo_root, cfg, led, today, force_vault)
    content, vf = timed("math_guard", verified_content, content, repo_root, led, today)
    edition = build_edition(content, vf, cfg, edition_no=edition_no, today=today,
                            repo_slug=repo_slug, solution_url=solution_url)

    def draw_and_compile() -> tuple[dict, Path]:
        overlaps: list = []
        svg = render_diagram(content.case.diagram.kind,
                             {p.symbol: p.value for p in content.case.diagram.params},
                             repo_root / "build" / "diagram_src.svg", audit=overlaps)
        try:                                   # report-only: never restyles, never blocks the edition
            for f in [*legibility.overlap_findings(overlaps), *legibility.analyze(svg)]:
                log.warning("legibility [%s] %s: %s", f.level, f.code, f.message)
        except Exception as exc:  # noqa: BLE001
            log.info("legibility check skipped: %s", exc)
        archive = repo_root / "docs" / "gazette" / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        pdf_path = archive / f"acta-{edition_no:04d}.pdf"
        return render.render_edition(edition, svg, solution_url, repo_root, pdf_path), pdf_path

    fit, pdf = timed("render", draw_and_compile)
    # Motion companion (MP4 + GIF) for the email: best-effort, never blocks publication, never committed
    # (kept under build/ so the repo does not grow by ~1.5 MB a day).
    media = timed("video", video.maybe_render, edition, repo_root,
                  repo_root / "build" / "media" / f"acta-{edition_no:04d}", cfg)
    delivery_errors = [] if dry_run else timed(
        "publish", publish, repo_root, led, today, content, edition, vf, pdf, repo_slug, media)

    total = round(time.perf_counter() - t0, 2)
    summary = {"edition": edition_no, "date": today.isoformat(), "origin": content.origin,
               "case_id": content.case_id, "result": vf.computed_result, "unit": vf.unit,
               "full_precision": vf.full_precision, "significant_figures": 3,
               "pages": fit["pages"], "pdf": str(pdf),
               "video": {k: str(v) for k, v in media.items() if v} if media else None,
               "solution_url": solution_url,
               "dry_run": dry_run, "fit": fit, "delivery_errors": delivery_errors,
               "synthesis_notes": synth_notes,
               "timings_s": timings, "total_s": total}
    (repo_root / "build").mkdir(exist_ok=True)
    (repo_root / "build" / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    core = total - timings.get("video", 0.0)          # the optional clip is outside the NFR-02 budget
    if core > NFR_BUDGET_S:
        log.warning("NFR-02 budget exceeded: %.1fs > %ds", core, NFR_BUDGET_S)
    log.info("edition №%d ready in %.1fs (%s)", edition_no, total, content.origin)
    return summary
