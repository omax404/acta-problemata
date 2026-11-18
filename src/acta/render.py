"""FR-04: Typst compilation with a deterministic single-page fit loop.
Prefers the Typst CLI (FR-04.1); falls back to the `typst` Python binding
for local dev. Overflow is fixed by truncating the narrative, never the layout.
"""
from __future__ import annotations

import json
import logging
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

from pypdf import PdfReader

log = logging.getLogger("acta.render")
TRUNCATION_LADDER = (None, 120, 100, 80, 60)   # words; None = full narrative

_SUP = str.maketrans("0123456789-", "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207b")


class LayoutError(RuntimeError):
    pass


def display_result(x: float) -> str:
    """3 s.f. with unicode scientific notation outside 10^-2..10^4."""
    if x == 0:
        return "0"
    exp = math.floor(math.log10(abs(x)))
    if -2 <= exp <= 4:
        return f"{x:,.{max(0, 2 - exp)}f}"
    return f"{x / 10**exp:.2f} \u00d7 10{str(exp).translate(_SUP)}"


def svg_aspect(path: Path) -> float:
    """height/width of an SVG from its viewBox (0.5 if unknown) - lets the template cap tall figures."""
    head = path.read_text(encoding="utf-8", errors="ignore")[:2000]
    m = re.search(r'viewBox="\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', head)
    return round(float(m.group(2)) / float(m.group(1)), 3) if m and float(m.group(1)) else 0.5


def make_qr(url: str, path: Path) -> None:
    import qrcode
    import qrcode.image.svg
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(str(path))


def _compile(build: Path, out_pdf: Path, entry: str = "broadside.typ") -> float:
    t0 = time.perf_counter()
    try:
        import typst  # pinned in pyproject: the SAME compiler in dev, CI and production
    except ImportError:
        typst = None
    try:
        if typst is not None:
            typst.compile(str(build / entry), output=str(out_pdf), root=str(build))
        else:
            cli = shutil.which("typst")
            if not cli:
                raise RuntimeError("no Typst compiler: pip install typst (or put the CLI on PATH)")
            r = subprocess.run([cli, "compile", "--root", str(build), entry, str(out_pdf)],
                               cwd=build, capture_output=True, text=True, timeout=30)
            if r.returncode:
                raise RuntimeError(f"typst compile failed:\n{r.stderr.strip()}")
    except RuntimeError:
        raise
    except Exception as exc:                     # typst.TypstError etc. -> one error type
        raise RuntimeError(f"typst compile failed: {exc}") from exc
    return (time.perf_counter() - t0) * 1000


def render_edition(edition: dict, diagram_svg: Path, qr_url: str,
                   repo_root: Path, out_pdf: Path) -> dict:
    build = repo_root / "build"
    build.mkdir(exist_ok=True)
    shutil.copy(repo_root / "templates" / "broadside.typ", build / "broadside.typ")
    shutil.copy(diagram_svg, build / "diagram.svg")
    make_qr(qr_url, build / "qr.svg")

    edition["diagram_aspect"] = svg_aspect(build / "diagram.svg")
    original = edition["narrative"]
    for cut in TRUNCATION_LADDER:
        edition["narrative"] = original if cut is None else \
            " ".join(original.split()[:cut]).rstrip(",;:") + " \u2026"
        (build / "edition.json").write_text(
            json.dumps(edition, ensure_ascii=False, indent=1), encoding="utf-8")
        ms = _compile(build, out_pdf)
        pages = len(PdfReader(str(out_pdf)).pages)
        log.info("render: %s words -> %d page(s), %.0f ms",
                 "full" if cut is None else cut, pages, ms)
        if pages == 1:
            return {"compile_ms": round(ms, 1), "truncated_to_words": cut, "pages": 1}
    raise LayoutError("content does not fit one A4 page even at 60 narrative words")
