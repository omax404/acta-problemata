"""Procedural metallographic micrograph plate (deterministic per edition).

Pure numpy + Pillow: Voronoi grain mosaic, etched grain boundaries, inclusions, analog dither,
ink/orange duotone. The image is synthetic, so the caption says so and the figures it prints
(mean grain size, ASTM G, magnification, scale bar) are computed from the generated grains.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 480
INK = np.array([27, 24, 20], dtype=float)
PAPER = np.array([243, 236, 220], dtype=float)
ORANGE = np.array([230, 91, 24], dtype=float)

# domain -> (material label, etchant, magnification, grain count)
STYLES = {
    "Mechanical": ("AISI 1045 normalised", "2% Nital", 200, 150),
    "Materials": ("Ferrite-pearlite steel", "2% Nital", 500, 110),
    "Aerospace": ("Ti-6Al-4V alpha-beta", "Kroll's reagent", 500, 95),
    "Electrical": ("OFHC copper, annealed", "FeCl3", 100, 190),
    "Chemical": ("316L austenitic stainless", "Electrolytic oxalic", 200, 130),
    "Civil": ("Structural steel S355", "2% Nital", 200, 150),
    "Thermal": ("Alloy 800H", "Glyceregia", 200, 120),
    "Fluids": ("Cu-Zn brass (CW508L)", "FeCl3", 100, 170),
}


def _rng(seed: str) -> np.random.Generator:
    return np.random.default_rng(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big"))


def _bayer(n: int = 8) -> np.ndarray:
    m = np.array([[0]])
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / m.size


def make_micrograph(seed: str, domain: str, out_png: Path) -> dict:
    """Render the plate to out_png and return caption data (all values computed, none invented)."""
    material, etchant, mag, n = STYLES.get(domain, STYLES["Mechanical"])
    rng = _rng(f"{seed}|{domain}")
    pts = rng.uniform(0, SIZE, (n, 2))
    tone = rng.uniform(0.42, 0.9, n)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    best = np.full((SIZE, SIZE), np.inf)
    second = np.full((SIZE, SIZE), np.inf)
    idx = np.zeros((SIZE, SIZE), dtype=int)
    for i, (px, py) in enumerate(pts):          # periodic wrap avoids empty borders
        d = np.minimum.reduce([np.hypot(xx - px - dx, yy - py - dy)
                               for dx in (-SIZE, 0, SIZE) for dy in (-SIZE, 0, SIZE)])
        closer = d < best
        second = np.where(closer, best, np.minimum(second, d))
        idx = np.where(closer, i, idx)
        best = np.where(closer, d, best)
    boundary = np.clip(1 - (second - best) / 3.2, 0, 1)          # thin dark etched boundary
    grain = tone[idx] - 0.10 * (best / best.max())               # per-grain etch response
    noise = rng.normal(0, 0.035, (SIZE, SIZE))
    img = np.clip(grain + noise, 0, 1)
    for _ in range(int(n * 0.35)):                               # inclusions / carbide specks
        cx, cy, r = rng.uniform(0, SIZE), rng.uniform(0, SIZE), rng.uniform(1.2, 3.4)
        img[(xx - cx) ** 2 + (yy - cy) ** 2 < r * r] *= 0.25
    img = np.clip(img * (1 - 0.82 * boundary), 0, 1)
    vig = 1 - 0.18 * (np.hypot(xx - SIZE / 2, yy - SIZE / 2) / (SIZE * 0.71)) ** 2
    img = np.clip(img * vig, 0, 1)
    dith = (img > np.tile(_bayer(8), (SIZE // 8, SIZE // 8))).astype(float)  # analog dither
    mix = 0.78 * dith + 0.22 * img
    rgb = INK[None, None, :] * (1 - mix[..., None]) + PAPER[None, None, :] * mix[..., None]
    rgb[boundary > 0.9] = rgb[boundary > 0.9] * 0.6 + ORANGE * 0.4   # orange etch on boundaries
    # scale bar: 50 um at the stated magnification (1 px = 0.1 mm on a 100 dpi print / mag)
    um_per_px = 25.4e3 / 100 / mag                                # 100 px/in plate scale
    bar_um = 50 if 50 / um_per_px < SIZE / 2 else 25
    bar_px = int(round(bar_um / um_per_px))
    rgb[SIZE - 22:SIZE - 16, 18:18 + bar_px] = PAPER
    rgb[SIZE - 24:SIZE - 14, 18:20] = PAPER
    rgb[SIZE - 24:SIZE - 14, 16 + bar_px:18 + bar_px] = PAPER
    Image.fromarray(rgb.astype("uint8")).save(out_png, optimize=True)
    area_mm2 = (SIZE * um_per_px / 1000) ** 2
    mean_d_um = 2 * math.sqrt(area_mm2 * 1e6 / (n * math.pi))      # equivalent circle diameter
    n_per_mm2 = n / area_mm2
    astm_g = round(math.log2(n_per_mm2 / 15.5) + 1, 1) if n_per_mm2 > 0 else 0.0  # ASTM E112 (N_AE at 1x)
    return {"material": material, "etchant": etchant, "mag": mag, "grains": n,
            "mean_d_um": round(mean_d_um, 1), "astm_g": astm_g, "bar_um": bar_um,
            "seed": hashlib.sha256(seed.encode()).hexdigest()[:6].upper()}
