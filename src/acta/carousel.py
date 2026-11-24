"""LinkedIn carousel: the day's problem as 5 square 1080x1080 PNG slides + caption.txt (fr / en).

Slides: hook, data, question, hint, call-to-action. Same palette as the broadside (bone / graphite /
per-domain accent), same bundled OFL fonts and logo. Pure Pillow, no network. The hint never prints the
numeric answer; the honesty label (real vs realistic / source line) is carried on the hook slide.
Callers treat any exception as "no carousel today": this must never block publication.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import style

SIZE = 1080
M = 84                                            # outer margin
BONE, GRAPHITE, MID = (235, 235, 235), (18, 18, 18), (141, 141, 141)
LANGS = ("fr", "en")
UI = {
    "fr": {"data": "DONNÉES", "question": "À DÉTERMINER", "hint": "INDICE", "cta": "À VOUS DE JOUER",
           "cta_head": "Résolvez-le. Faites-le vérifier.", "cta_sub": "Déposez votre fiche solution : "
           "le tampon VÉRIFIÉ n'est décerné qu'aux résultats exacts.", "swipe": "GLISSER →",
           "real": "CAS PUBLIC RÉEL", "realistic": "PROBLÈME RÉALISTE", "tag_hint": "Formule de départ",
           "answer_in": "Réponse en {unit}, 3 chiffres significatifs.", "post": "Problème du jour",
           "link": "Énoncé et dépôt de solution"},
    "en": {"data": "GIVEN DATA", "question": "TO DETERMINE", "hint": "HINT", "cta": "YOUR TURN",
           "cta_head": "Solve it. Get it verified.", "cta_sub": "Submit your solution sheet: the VERIFIED "
           "stamp is only earned by exact results.", "swipe": "SWIPE →",
           "real": "REAL PUBLIC CASE", "realistic": "REALISTIC PROBLEM", "tag_hint": "Starting formula",
           "answer_in": "Answer in {unit}, 3 significant figures.", "post": "Problem of the day",
           "link": "Statement and solution upload"},
}
HASHTAGS = {
    "fr": ["#Ingénieur", "#IngénierieIndustrielle", "#Maroc", "#JeuneDiplômé", "#Industrie"],
    "en": ["#Engineering", "#IndustrialEngineering", "#Morocco", "#JuniorEngineer", "#ProblemSolving"],
}
DOMAIN_TAG = {"Mechanical": "Mécanique", "Aerospace": "Aérospatial", "Electrical": "Électricité",
              "Chemical": "GénieChimique", "Civil": "GénieCivil", "Thermal": "Thermique",
              "Materials": "Matériaux", "Fluids": "Fluides"}


@dataclass
class Deck:
    lang: str
    code: str                                     # e.g. "No. 005" / "P01"
    title: str
    kicker: str                                   # domain or sector
    accent: str
    status_label: str                             # honesty label: real vs realistic
    provenance: str                               # source line, printed small on the hook slide
    rows: list[tuple[str, str]] = field(default_factory=list)       # (label, value)
    question: str = ""
    hint: str = ""
    hint_note: str = ""
    url: str = ""
    tag: str = ""


# ---------- content ----------------------------------------------------------------------------

def _strip_math(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("$", "").replace("\\", "")).strip()


def deck_from_edition(ed: dict, lang: str | None = None) -> Deck:
    lang = lang or "en"
    ui = UI[lang]
    unit = ed["formula"]["unit"]
    src = ed.get("source_line", "")
    # Honesty Rule: "real" only with a public source URL and never for a declared scenario class.
    has_url = str(ed.get("source_url", "")).startswith(("http://", "https://"))
    real = has_url and not src.startswith("Scenario")
    return Deck(
        lang=lang, code=f"№ {ed['edition_number']:03d}", title=ed["headline"], kicker=ed["domain"],
        accent=ed.get("accent") or style.DEFAULT_ACCENT,
        status_label=ui["real"] if real else ui["realistic"],
        provenance=src, rows=list(ed["boundary_conditions"].items()), question=ed["challenge_question"],
        hint=_strip_math(ed["formula"]["symbolic"]), hint_note=ui["answer_in"].format(unit=unit),
        url=ed.get("solution_url", ""), tag=ed["domain"])


def deck_from_bank(p: dict, lang: str | None = None, base_url: str = "") -> Deck:
    from .sheet import archive_url
    lang = lang or p.get("lang", "fr")
    ui = UI[lang]
    real = p["status"] == "real"
    return Deck(
        lang=lang, code=f"P{int(p['id']):02d}", title=p["title"], kicker=f"{p['sector']} · {p['region']}",
        accent=style.DEFAULT_ACCENT, status_label=ui["real"] if real else ui["realistic"],
        provenance=p.get("source_url") or "",
        rows=[(r[0] + (f" ({r[1]})" if r[1] else ""), r[2]) for r in p["data"]],
        question=" ".join(f"{i}) {q}" for i, q in enumerate(p["questions"], 1)),
        hint=_strip_math(p["formulas"][0]) if p["formulas"] else "", hint_note="",
        url=archive_url(p, base_url) if base_url else archive_url(p), tag=p["sector"])


def load_deck(root: Path, ref: str, lang: str | None = None) -> Deck:
    """`today` -> build/edition.json when it is today's, else today's bank rotation; else a bank slug/id."""
    if ref == "today":
        f = root / "build" / "edition.json"
        if f.exists():
            ed = json.loads(f.read_text(encoding="utf-8"))
            if ed.get("date") == datetime.now(UTC).date().isoformat():
                return deck_from_edition(ed, lang)
    from . import sheet
    return deck_from_bank(sheet.load_problem(root, ref), lang)


# ---------- drawing ----------------------------------------------------------------------------

def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


@lru_cache(maxsize=4096)
def _has_glyph(path: str, ch: str) -> bool:
    """True if the font draws `ch` as something other than its .notdef box."""
    font = ImageFont.truetype(path, 40)

    def ink(c: str) -> bytes:
        im = Image.new("L", (64, 64))
        ImageDraw.Draw(im).text((8, 4), c, font=font, fill=255)
        return im.tobytes()
    return ink(ch) != ink("\uffff")


class Fonts:
    def __init__(self, root: Path):
        d = root / "templates" / "fonts"
        self.paths = {"display": d / "Anton_400Regular.ttf", "mono": d / "SpaceMono_400Regular.ttf",
                      "monob": d / "SpaceMono_700Bold.ttf", "body": d / "BarlowSemiCondensed_600SemiBold.ttf",
                      "bodyr": d / "BarlowSemiCondensed_400Regular.ttf"}

    def get(self, kind: str, size: int, text: str = "") -> ImageFont.FreeTypeFont:
        """Bundled OFL font; DejaVu (ships with matplotlib) when the text needs glyphs it lacks (Δ, ε, ⁻⁶)."""
        f = ImageFont.truetype(str(self.paths[kind]), size)
        if text and not all(_has_glyph(str(self.paths[kind]), c) for c in set(text) if not c.isspace()):
            import matplotlib
            ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
            bold = kind in ("display", "monob", "body")
            name = ("DejaVuSansMono" if kind.startswith("mono") else "DejaVuSans") + ("-Bold" if bold else "")
            return ImageFont.truetype(str(ttf / f"{name}.ttf"), size)
        return f


def wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            t = f"{cur} {word}".strip()
            if cur and draw.textlength(t, font=font) > width:
                lines.append(cur)
                cur = word
            else:
                cur = t
        lines.append(cur)
    return lines


def fit(draw, fonts: Fonts, kind: str, text: str, w: int, h: int, hi: int, lo: int, lead: float = 1.18,
        probe: str = ""):
    """Largest font size in [lo, hi] whose wrapped text fits w x h; ellipsis if even `lo` overflows."""
    for size in range(hi, lo - 1, -2):
        f = fonts.get(kind, size, probe or text)
        lines = wrap(draw, text, f, w)
        if len(lines) * size * lead <= h:
            return f, lines, int(size * lead)
    f = fonts.get(kind, lo, probe or text)
    lines = wrap(draw, text, f, w)
    keep = max(1, int(h // (lo * lead)))
    if len(lines) > keep:
        lines = [*lines[:keep - 1], lines[keep - 1].rstrip(" ,;:.") + " …"]
    return f, lines, int(lo * lead)


def _text_block(draw, xy, lines, font, step, fill):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += step
    return y


def _logo(root: Path, name: str, height: int) -> Image.Image:
    im = Image.open(root / "assets" / name).convert("RGBA")
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def _frame(deck: Deck, fonts: Fonts, root: Path, n: int, bg, fg, dark: bool, label: str):
    """Common chrome: background, top rail (label + counter), bottom rail (brand, code, logo)."""
    im = Image.new("RGB", (SIZE, SIZE), bg)
    d = ImageDraw.Draw(im)
    acc = _hex(deck.accent)
    d.rectangle([0, 0, SIZE, 14], fill=acc)
    d.text((M, 52), f"ACTA PROBLEMATA  //  {label}", font=fonts.get("monob", 24), fill=fg)
    d.text((SIZE - M, 52), f"{n:02d}/05", font=fonts.get("monob", 24), fill=acc, anchor="ra")
    d.line([M, 104, SIZE - M, 104], fill=fg, width=2)
    d.line([M, SIZE - 112, SIZE - M, SIZE - 112], fill=MID, width=1)
    d.text((M, SIZE - 82), f"{deck.code}  ·  {deck.tag.upper()}", font=fonts.get("mono", 22), fill=MID)
    lg = _logo(root, "logo-white.png" if dark else "logo.png", 64)
    im.paste(lg, (SIZE - M - lg.width, SIZE - 96), lg)
    return im, d, acc


def slide_hook(deck, fonts, root):
    ui = UI[deck.lang]
    im, d, acc = _frame(deck, fonts, root, 1, GRAPHITE, BONE, True, deck.kicker.upper()[:48])
    d.rectangle([M, 150, M + 330, 214], fill=acc)
    d.text((M + 20, 160), deck.code, font=fonts.get("display", 44), fill=GRAPHITE)
    d.text((M + 360, 168), deck.status_label, font=fonts.get("monob", 26), fill=acc)
    f, lines, step = fit(d, fonts, "display", deck.title.upper(), SIZE - 2 * M, 520, 118, 56, 1.08)
    _text_block(d, (M, 262), lines, f, step, BONE)
    prov = deck.provenance if not deck.provenance.startswith("http") else deck.provenance[:70]
    pf, pl, ps = fit(d, fonts, "mono", prov, SIZE - 2 * M - 220, 70, 20, 15, 1.3)
    _text_block(d, (M, SIZE - 214), pl, pf, ps, MID)
    d.text((SIZE - M, SIZE - 214), ui["swipe"], font=fonts.get("monob", 26), fill=acc, anchor="ra")
    return im


def slide_data(deck, fonts, root):
    ui = UI[deck.lang]
    im, d, acc = _frame(deck, fonts, root, 2, BONE, GRAPHITE, False, ui["data"])
    rows = deck.rows[:8]
    top, bottom = 150, SIZE - 140
    rh = min(112, (bottom - top) // max(1, len(rows)))
    pk, pv = " ".join(k for k, _ in rows), " ".join(v for _, v in rows)     # one font per column
    for i, (k, v) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            d.rectangle([M - 16, y, SIZE - M + 16, y + rh - 6], fill=(255, 255, 255))
        d.rectangle([M - 16, y, M - 8, y + rh - 6], fill=acc)
        kf, kl, ks = fit(d, fonts, "body", k, 400, rh - 18, 36, 22, 1.05, pk)
        _text_block(d, (M + 8, y + (rh - 6 - len(kl) * ks) // 2), kl, kf, ks, GRAPHITE)
        vf, vl, vs = fit(d, fonts, "monob", v, 430, rh - 18, 36, 20, 1.1, pv)
        _text_block(d, (M + 500, y + (rh - 6 - len(vl) * vs) // 2), vl, vf, vs, GRAPHITE)
    return im


def slide_question(deck, fonts, root):
    ui = UI[deck.lang]
    acc = _hex(deck.accent)
    im, d, _ = _frame(deck, fonts, root, 3, acc, GRAPHITE, False, ui["question"])
    f, lines, step = fit(d, fonts, "display", deck.question, SIZE - 2 * M, SIZE - 330, 92, 40, 1.12)
    _text_block(d, (M, 170), lines, f, step, GRAPHITE)
    return im


def slide_hint(deck, fonts, root):
    ui = UI[deck.lang]
    im, d, acc = _frame(deck, fonts, root, 4, GRAPHITE, BONE, True, ui["hint"])
    d.text((M, 160), ui["tag_hint"].upper(), font=fonts.get("monob", 26), fill=acc)
    box = [M, 220, SIZE - M, 220 + 330]
    d.rectangle(box, fill=(30, 30, 30), outline=acc, width=3)
    f, lines, step = fit(d, fonts, "monob", deck.hint, SIZE - 2 * M - 64, 330 - 64, 54, 24, 1.3)
    _text_block(d, (M + 32, 252), lines, f, step, BONE)
    if deck.hint_note:
        nf, nl, ns = fit(d, fonts, "body", deck.hint_note, SIZE - 2 * M, 160, 44, 28, 1.2)
        _text_block(d, (M, 600), nl, nf, ns, BONE)
    return im


def slide_cta(deck, fonts, root):
    ui = UI[deck.lang]
    acc = _hex(deck.accent)
    im, d, _ = _frame(deck, fonts, root, 5, BONE, GRAPHITE, False, ui["cta"])
    f, lines, step = fit(d, fonts, "display", ui["cta_head"].upper(), SIZE - 2 * M, 300, 104, 60, 1.08)
    y = _text_block(d, (M, 170), lines, f, step, GRAPHITE)
    sf, sl, ss = fit(d, fonts, "body", ui["cta_sub"], SIZE - 2 * M, 190, 40, 26, 1.22)
    y = _text_block(d, (M, y + 24), sl, sf, ss, GRAPHITE)
    d.rectangle([M, SIZE - 300, SIZE - M, SIZE - 190], fill=GRAPHITE)
    d.rectangle([M, SIZE - 300, M + 12, SIZE - 190], fill=acc)
    url = deck.url.replace("https://", "").replace("http://", "")
    url = url or "github.com/omax404/acta-problemata"
    uf, ul, us = fit(d, fonts, "monob", url, SIZE - 2 * M - 64, 90, 30, 16, 1.2)
    _text_block(d, (M + 36, SIZE - 300 + (110 - len(ul) * us) // 2), ul, uf, us, BONE)
    return im


SLIDES = (("1-hook", slide_hook), ("2-data", slide_data), ("3-question", slide_question),
          ("4-hint", slide_hint), ("5-cta", slide_cta))


# ---------- caption ----------------------------------------------------------------------------

def caption(deck: Deck) -> str:
    ui = UI[deck.lang]
    q = deck.question if len(deck.question) <= 220 else deck.question[:217].rstrip() + "…"
    tags = list(HASHTAGS[deck.lang])
    if deck.lang == "fr" and deck.tag in DOMAIN_TAG:
        tags.insert(0, f"#{DOMAIN_TAG[deck.tag]}")
    elif deck.lang == "en":
        tags.insert(0, f"#{deck.tag.replace(' ', '')}")
    parts = [f"{ui['post']} {deck.code} - {deck.title}", f"[{deck.status_label}]", q]
    if deck.url:
        parts.append(f"{ui['link']} : {deck.url}")
    parts.append(" ".join(tags))
    return "\n\n".join(parts) + "\n"


# ---------- entry point ------------------------------------------------------------------------

def render_carousel(deck: Deck, root: Path, out_dir: Path) -> list[Path]:
    """Write 5 PNGs (1080x1080) and caption.txt into out_dir. Returns the PNG paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fonts = Fonts(root)
    paths = []
    for name, fn in SLIDES:
        p = out_dir / f"slide-{name}.png"
        fn(deck, fonts, root).save(p, optimize=True)
        paths.append(p)
    (out_dir / "caption.txt").write_text(caption(deck), encoding="utf-8")
    return paths
