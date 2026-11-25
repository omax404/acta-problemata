"""Daily rotation policy: prefer the French Moroccan-sector bank, cap CSB (US Chemical Safety Board) cases.

config.json -> "rotation": {"prefer_lang": "fr", "prefer_region": "MA",
                            "csb_max_per_window": 1, "csb_window_days": 3}
CSB cases may appear on at most `csb_max_per_window` days out of every `csb_window_days` (default 1 in 3).
Bank picks are stateless (pure function of the date) so sheet / carousel / pick_edition always agree;
live-source CSB fetching is capped from the ledger history instead (see `csb_allowed`).
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

DEFAULTS = {"prefer_lang": "fr", "prefer_region": "MA", "csb_max_per_window": 1, "csb_window_days": 3}
CSB_SOURCE_ID = "fail-csb"


def load_cfg(root: Path | None = None, cfg: dict | None = None) -> dict:
    """Defaults < config.json["rotation"] (or `cfg`), validated."""
    if cfg is None and root is not None and (root / "config.json").exists():
        cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    out = {**DEFAULTS, **((cfg or {}).get("rotation") or {})}
    w, m = out["csb_window_days"], out["csb_max_per_window"]
    if not (isinstance(w, int) and isinstance(m, int) and w >= 1 and 0 <= m <= w):
        raise ValueError("rotation: need integers 1 <= csb_window_days and 0 <= csb_max_per_window <= window")
    return out


def is_csb(problem: dict) -> bool:
    """A bank problem derived from a CSB investigation (explicit track, or CSB source metadata)."""
    keys = ("source_url", "source_publisher", "source_title")
    blob = " ".join(str(problem.get(k, "")) for k in keys).lower()
    return problem.get("track") == "csb" or "csb.gov" in blob or "chemical safety board" in blob


def is_csb_id(case_id: str) -> bool:
    return CSB_SOURCE_ID in case_id


def matches(problem: dict, cfg: dict) -> bool:
    lang_ok = not cfg["prefer_lang"] or problem.get("lang", "fr") == cfg["prefer_lang"]
    region_ok = not cfg["prefer_region"] or problem.get("region_code", "MA") == cfg["prefer_region"]
    return lang_ok and region_ok


def pick(problems: list[dict], today: date, cfg: dict | None = None) -> dict:
    """Today's bank problem. Preferred (lang/region) non-CSB problems follow the day-of-year rotation; a CSB
    problem is served only on the first `csb_max_per_window` days of each `csb_window_days` window."""
    cfg = cfg or load_cfg()
    csb = [p for p in problems if is_csb(p)]
    rest = [p for p in problems if not is_csb(p)]
    w, m = cfg["csb_window_days"], cfg["csb_max_per_window"]
    if csb and today.toordinal() % w < m:
        return csb[(today.toordinal() // w) % len(csb)]
    pool = [p for p in rest if matches(p, cfg)] or rest or problems
    return pool[(today.timetuple().tm_yday - 1) % len(pool)]


def csb_allowed(history: list[dict], today: date, cfg: dict | None = None) -> bool:
    """Ledger check for live sources: is another CSB edition allowed today?"""
    cfg = cfg or load_cfg()
    start = today - timedelta(days=cfg["csb_window_days"] - 1)
    n = sum(1 for h in history
            if is_csb_id(str(h.get("id", ""))) and start <= date.fromisoformat(h["date"]) < today)
    return n < cfg["csb_max_per_window"]
