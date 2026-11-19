"""Deterministic vintage schematics (Enhancement 1, hardened).

The LLM only chooses a diagram *kind* plus numeric parameters; these audited
matplotlib renderers do all drawing. No LLM-generated code is ever executed.
Output: transparent-background SVG with text as paths (Typst-safe).
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

INK = "#1c1a17"
plt.rcParams.update({"font.family": "serif", "font.size": 11, "svg.fonttype": "path"})


def _fig(w=6.2, h=2.6):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_alpha(0)
    return fig, ax


def _arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1.3, "shrinkA": 0, "shrinkB": 0})


def _label(ax, x, y, s, **kw):
    ax.text(x, y, s, color=INK, ha="center", va="center", style="italic", **kw)


def _wall(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], color=INK, lw=1.6)
    for i in range(7):
        y = y0 + (y1 - y0) * i / 6
        ax.plot([x - 0.22, x], [y - 0.16, y], color=INK, lw=0.9)


def _dim(ax, x0, x1, y, s):
    ax.plot([x0, x1], [y, y], color=INK, lw=0.8)
    for x in (x0, x1):
        ax.plot([x, x], [y - 0.09, y + 0.09], color=INK, lw=0.8)
    _label(ax, (x0 + x1) / 2, y - 0.24, s)


def _cantilever(ax, p):
    _wall(ax, 0, -0.55, 0.75)
    ax.add_patch(Rectangle((0, -0.06), 4, 0.12, fill=False, ec=INK, lw=1.4))
    _arrow(ax, 4, 1.0, 4, 0.10); _label(ax, 4.28, 0.85, "P")
    _dim(ax, 0, 4, -0.62, "L")
    ax.set_xlim(-0.6, 4.8); ax.set_ylim(-1.15, 1.25)


def _thermal(ax, p):
    for i, s in enumerate(("R\u2081", "R\u2082", "R\u2083")):
        ax.add_patch(Rectangle((i * 1.2, 0), 1.2, 1.2, fill=False, ec=INK, lw=1.3))
        _label(ax, i * 1.2 + 0.6, 0.6, s)
    _label(ax, -0.55, 0.6, "T\u2095"); _label(ax, 4.15, 0.6, "T\u1d04")
    _arrow(ax, 0.3, 1.65, 3.3, 1.65); _label(ax, 1.8, 1.9, "q")
    ax.set_xlim(-1.0, 4.6); ax.set_ylim(-0.3, 2.2)


def _pipe(ax, p):
    ax.plot([0, 5], [0.55, 0.55], color=INK, lw=1.5)
    ax.plot([0, 5], [-0.55, -0.55], color=INK, lw=1.5)
    for y in (-0.4, -0.2, 0.0, 0.2, 0.4):
        ln = 1.1 * (1 - (y / 0.55) ** 2) + 0.15
        _arrow(ax, 1.0, y, 1.0 + ln, y)
    _label(ax, 2.6, 0.0, "v")
    _dim(ax, 0, 5, -0.95, "L")
    ax.plot([5.3, 5.3], [-0.55, 0.55], color=INK, lw=0.8)
    _label(ax, 5.6, 0.0, "D")
    ax.set_xlim(-0.3, 6.0); ax.set_ylim(-1.4, 0.9)


def _crack(ax, p):
    ax.add_patch(Rectangle((0, 0), 4, 2.2, fill=False, ec=INK, lw=1.4))
    ax.plot([0, 1.05], [1.1, 1.1], color=INK, lw=2.4)
    _label(ax, 0.55, 0.82, "a")
    for x in (0.8, 2.0, 3.2):
        _arrow(ax, x, 2.2, x, 2.9); _arrow(ax, x, 0.0, x, -0.7)
    _label(ax, 3.6, 2.65, "\u03c3")
    ax.set_xlim(-0.4, 4.4); ax.set_ylim(-1.0, 3.2)


def _divider(ax, p):
    ax.plot([0, 0], [0.2, 3.0], color=INK, lw=1.3)
    ax.plot([0, 2], [3.0, 3.0], color=INK, lw=1.3)
    ax.plot([2, 2], [3.0, 2.6], color=INK, lw=1.3)
    ax.add_patch(Rectangle((1.72, 1.8), 0.56, 0.8, fill=False, ec=INK, lw=1.3))
    _label(ax, 2.65, 2.2, "R\u2081")
    ax.plot([2, 2], [1.8, 1.4], color=INK, lw=1.3)
    ax.add_patch(Rectangle((1.72, 0.6), 0.56, 0.8, fill=False, ec=INK, lw=1.3))
    _label(ax, 2.65, 1.0, "R\u2082")
    ax.plot([2, 2], [0.6, 0.2], color=INK, lw=1.3)
    ax.plot([0, 2], [0.2, 0.2], color=INK, lw=1.3)
    for w, y in ((0.5, 0.05), (0.3, -0.08), (0.12, -0.21)):
        ax.plot([2 - w, 2 + w], [y, y], color=INK, lw=1.3)
    ax.plot([2, 3.6], [1.6, 1.6], color=INK, lw=1.3)
    ax.add_patch(Circle((3.7, 1.6), 0.07, fill=False, ec=INK, lw=1.2))
    _label(ax, 4.15, 1.6, "V\u2092\u1d64\u209c")
    _label(ax, -0.55, 1.6, "V\u1d62\u2099")
    ax.set_xlim(-1.1, 4.8); ax.set_ylim(-0.5, 3.3)


def _column(ax, p):
    ax.plot([0, 0], [0, 4], color=INK, lw=0.9, ls=(0, (4, 3)))
    ys = [4 * i / 40 for i in range(41)]
    xs = [0.55 * math.sin(math.pi * y / 4) for y in ys]
    ax.plot(xs, ys, color=INK, lw=1.6)
    for y, s in ((0, 1), (4, -1)):
        ax.add_patch(Polygon([(0, y), (-0.22, y - 0.3 * s), (0.22, y - 0.3 * s)],
                             fill=False, ec=INK, lw=1.2))
    _arrow(ax, 0, 4.9, 0, 4.35); _label(ax, 0.3, 4.75, "P")
    _arrow(ax, 0, -0.9, 0, -0.35); _label(ax, 0.3, -0.75, "P")
    ax.plot([-0.75, -0.75], [0, 4], color=INK, lw=0.8)
    _label(ax, -1.0, 2.0, "L")
    ax.set_xlim(-1.3, 1.2); ax.set_ylim(-1.2, 5.2)


KINDS = {
    "cantilever_point_load": _cantilever, "thermal_wall": _thermal,
    "pipe_flow": _pipe, "crack_plate": _crack,
    "voltage_divider": _divider, "column_buckling": _column,
}
DOMAIN_DEFAULT_KIND = {
    "Mechanical": "cantilever_point_load", "Thermal": "thermal_wall",
    "Fluids": "pipe_flow", "Materials": "crack_plate",
    "Electrical": "voltage_divider", "Civil": "column_buckling",
    "Aerospace": "cantilever_point_load", "Chemical": "thermal_wall",
}


def text_overlaps(fig, pad: float = 1.0) -> list[tuple[str, str]]:
    """Pairs of visible text labels whose boxes intersect (pixels, `pad` of slack). Read-only audit."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    boxes = [(t.get_text().strip(), t.get_window_extent(r)) for t in fig.findobj(matplotlib.text.Text)
             if t.get_visible() and t.get_text().strip()]
    return [(a, b) for i, (a, ba) in enumerate(boxes) for b, bb in boxes[i + 1:]
            if ba.x0 + pad < bb.x1 and bb.x0 + pad < ba.x1 and ba.y0 + pad < bb.y1 and bb.y0 + pad < ba.y1]


def render_diagram(kind: str, params: dict, out_path: Path, audit: list | None = None) -> Path:
    if kind not in KINDS:
        raise ValueError(f"unknown diagram kind {kind!r}; allowed: {sorted(KINDS)}")
    safe = {str(k)[:20]: float(v) for k, v in (params or {}).items()
            if isinstance(v, (int, float)) and -1e12 < v < 1e12}
    fig, ax = _fig()
    KINDS[kind](ax, safe)
    if audit is not None:                                  # report-only: the figure is never altered
        audit.extend(text_overlaps(fig))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    return out_path
