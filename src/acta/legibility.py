"""Read-only legibility audit for generated SVG figures (inspired by the antialgorithm `check.py` idea).

It NEVER restyles anything: it renders the figure and reports defects a reader would notice,
so the broadside's art direction stays exactly as designed. Checks, on the rendered image:
  * clipped   – ink touching the canvas edge (a label or arrow cut off by the figure bounds)
  * contrast  – darkest ink vs background below WCAG 4.5:1
  * blank     – almost no ink at all
  * icon      – ink that disappears when the figure is shrunk to thumbnail size
"""
from __future__ import annotations

import io
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

FULL_W, ICON_W = 1200, 240
EDGE = 3                       # px band at full size that must stay clear of ink
MIN_CONTRAST = 4.5
MIN_INK = 0.004                # fraction of pixels that must be ink
MIN_ICON_INK = 0.002


@dataclass
class Finding:
    level: str                 # "error" | "warn"
    code: str
    message: str


def _render(svg: Path, width: int) -> Image.Image:
    exe = shutil.which("rsvg-convert")
    if not exe:
        raise RuntimeError("rsvg-convert not found")
    r = subprocess.run([exe, "-w", str(width), "-f", "png", str(svg)], capture_output=True, check=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGBA")


def _flatten(im: Image.Image, bg=(255, 255, 255)) -> np.ndarray:
    base = Image.new("RGBA", im.size, (*bg, 255))
    return np.asarray(Image.alpha_composite(base, im).convert("RGB"), dtype=np.float64)


def _lum(rgb: np.ndarray) -> np.ndarray:
    c = rgb / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def _ratio(a: np.ndarray, b: float) -> np.ndarray:
    hi, lo = np.maximum(a, b), np.minimum(a, b)
    return (hi + 0.05) / (lo + 0.05)


def analyze(svg: Path, page_bg=(255, 255, 255)) -> list[Finding]:
    out: list[Finding] = []
    rgb = _flatten(_render(svg, FULL_W), page_bg)
    lum = _lum(rgb)
    bg = float(_lum(np.array(page_bg, dtype=np.float64)))
    ink = _ratio(lum, bg) >= 1.5                        # any mark differing from the page
    frac = float(ink.mean())
    if frac < MIN_INK:
        out.append(Finding("error", "blank", f"almost no visible ink ({frac:.2%})"))
        return out
    band = np.zeros_like(ink)
    band[:EDGE, :] = band[-EDGE:, :] = True
    band[:, :EDGE] = band[:, -EDGE:] = True
    touching = int((ink & band).sum())
    if touching:
        out.append(Finding("warn", "clipped",
                           f"ink touches the figure edge ({touching}px): a label or arrow may be cut"))
    darkest = float(np.percentile(lum[ink], 2))
    cr = float(_ratio(np.array(darkest), bg))
    if cr < MIN_CONTRAST:
        out.append(Finding("error", "contrast", f"darkest ink is only {cr:.1f}:1 against the background"))
    icon = _lum(_flatten(_render(svg, ICON_W), page_bg))
    if float((_ratio(icon, bg) >= 3.0).mean()) < MIN_ICON_INK:   # readable marks only
        out.append(Finding("warn", "icon", "figure nearly vanishes at thumbnail size"))
    return out
